/*
 * Test envio de datos por WiFi (UDP) -- ESP32 como PUNTO DE ACCESO propio +
 * BNO055 (modulo DFRobot SEN0374)
 *
 * Version de test_wifi_udp_bno055.ino que NO depende de ninguna red WiFi
 * existente (ni la de casa, ni la de la universidad con su login
 * enterprise que no funciona con este codigo). Aqui el ESP32 crea su
 * PROPIA red WiFi (modo Access Point / AP) y tu laptop se conecta
 * directamente a esa red -- sin router de por medio, sin depender de que
 * haya WiFi disponible en el laboratorio.
 *
 * Como funciona la direccion IP en este modo (fija, no hay que
 * averiguarla con visor_wifi_bno055.py como en la version anterior):
 *   - El ESP32 siempre es 192.168.4.1 (IP por defecto del modo AP de
 *     Espressif, no configurable a menos que la cambies a mano).
 *   - Tu laptop, al conectarse a la red del ESP32, recibe una IP en el
 *     mismo rango (tipicamente 192.168.4.2) que el propio ESP32 le asigna
 *     por DHCP -- no necesitas saberla ni escribirla en ningun lado.
 *   - El ESP32 manda los datos por BROADCAST (192.168.4.255) en vez de a
 *     una IP fija de PC -- asi le llegan a cualquier laptop conectada a
 *     su red, sin tener que configurar nada de tu parte.
 *
 * Conexionado del sensor: identico a test_bno055.ino / test_wifi_udp_bno055.ino
 *   BNO055 (SEN0374) VCC -> ESP32 3V3
 *   BNO055 (SEN0374) GND -> ESP32 GND
 *   BNO055 (SEN0374) SDA -> ESP32 GPIO21
 *   BNO055 (SEN0374) SCL -> ESP32 GPIO22
 *
 * ANTES DE CARGAR: puedes cambiar AP_SSID/AP_PASSWORD si quieres (el
 * password debe tener minimo 8 caracteres o el ESP32 crea la red abierta,
 * sin contraseña). NO hace falta tocar ninguna IP.
 *
 * Como probarlo:
 *   1. Cargar este sketch.
 *   2. En tu laptop, conectarte por WiFi a la red "LIBRA_ESP32" (o el
 *      nombre que hayas puesto), con la contraseña configurada abajo --
 *      exactamente como te conectarias a cualquier otra red WiFi.
 *   3. Mientras estes conectado a esta red, tu laptop probablemente pierda
 *      acceso a internet (el ESP32 no reenvia trafico a internet) -- es
 *      normal y no afecta esta prueba.
 *   4. Correr visor_wifi_ap_bno055.py -- ya no hace falta preguntarle tu
 *      IP ni escribirla en el sketch, todo es automatico.
 *
 * Libreria requerida: DFRobot_BNO055 (igual que test_wifi_udp_bno055.ino).
 * WiFi.h y WiFiUdp.h ya vienen en el core de ESP32.
 *
 * Mismas notas de unidades y de comandos z/c que test_wifi_udp_bno055.ino
 * (ver ese sketch) -- lo unico que cambia aca es como se arma la red WiFi.
 */

#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Preferences.h>
#include <math.h>
#include "DFRobot_BNO055.h"

typedef DFRobot_BNO055_IIC BNO;

// ------------------- CONFIGURAR (opcional) -------------------
const char* AP_SSID     = "LIBRA_ESP32";
const char* AP_PASSWORD = "libra2026";   // minimo 8 caracteres, si no la red queda abierta
const uint16_t UDP_PORT = 4211;
// ---------------------------------------------------------------

IPAddress BROADCAST_IP(192, 168, 4, 255);  // subred fija del modo AP del ESP32

BNO bno(&Wire, 0x28);
WiFiUDP udp;

Preferences prefs;
const char* NVS_NAMESPACE = "libra_home";
const char* NVS_NAMESPACE_ACCEL = "libra_accal";
const int HOME_SAMPLES = 200;          // ~2 s de muestras (antes 100 = ~1 s) -- promedio mas estable
const float HOME_MAX_STD_DEG = 0.5f;   // si el sensor se movio mas que esto durante la captura, se rechaza el cero

const float MG_TO_MS2 = 9.80665f / 1000.0f;

float zeroHeading = 0, zeroRoll = 0, zeroPitch = 0;
bool zeroIsSet = false;

void cargarZeroDesdeFlash() {
  prefs.begin(NVS_NAMESPACE, true);
  zeroIsSet = prefs.getBool("zero_set", false);
  if (zeroIsSet) {
    zeroHeading = prefs.getFloat("zero_heading", 0);
    zeroRoll = prefs.getFloat("zero_roll", 0);
    zeroPitch = prefs.getFloat("zero_pitch", 0);
  }
  prefs.end();
}

void guardarZeroEnFlash(float h, float r, float p) {
  prefs.begin(NVS_NAMESPACE, false);
  prefs.putFloat("zero_heading", h);
  prefs.putFloat("zero_roll", r);
  prefs.putFloat("zero_pitch", p);
  prefs.putBool("zero_set", true);
  prefs.end();
  zeroHeading = h;
  zeroRoll = r;
  zeroPitch = p;
  zeroIsSet = true;
}

void borrarZeroDeFlash() {
  prefs.begin(NVS_NAMESPACE, false);
  prefs.clear();
  prefs.end();
  zeroHeading = 0;
  zeroRoll = 0;
  zeroPitch = 0;
  zeroIsSet = false;
}

void establecerZeroActual() {
  Serial.println("Estableciendo cero absoluto -- MANTEN EL SENSOR QUIETO en la posicion de referencia...");

  BNO::sRegCalibState_t calibInicio = bno.getCalStatus();
  if (calibInicio.ACC < 2) {
    Serial.println("AVISO: el acelerometro no esta bien calibrado (calib.accel < 2/3) -- el cero puede no ser preciso. Si puedes, calibra el sensor (moverlo lentamente en varias orientaciones) antes de fijar el cero.");
  }

  double sumHeading = 0, sumRoll = 0, sumPitch = 0;
  double sumRollSq = 0, sumPitchSq = 0;

  for (int i = 0; i < HOME_SAMPLES; i++) {
    BNO::sEulAnalog_t eul = bno.getEul();
    sumHeading += eul.head;
    sumRoll += eul.roll;
    sumPitch += eul.pitch;
    sumRollSq += (double)eul.roll * eul.roll;
    sumPitchSq += (double)eul.pitch * eul.pitch;
    delay(10);
  }

  float h0 = sumHeading / HOME_SAMPLES;
  float r0 = sumRoll / HOME_SAMPLES;
  float p0 = sumPitch / HOME_SAMPLES;

  double varRoll = sumRollSq / HOME_SAMPLES - (double)r0 * r0;
  double varPitch = sumPitchSq / HOME_SAMPLES - (double)p0 * p0;
  float rollStd = (varRoll > 0) ? sqrt(varRoll) : 0.0f;
  float pitchStd = (varPitch > 0) ? sqrt(varPitch) : 0.0f;

  Serial.print("Muestras usadas: ");
  Serial.print(HOME_SAMPLES);
  Serial.print("  roll0=");
  Serial.print(r0, 3);
  Serial.print(" (std=");
  Serial.print(rollStd, 3);
  Serial.print(" grados)  pitch0=");
  Serial.print(p0, 3);
  Serial.print(" (std=");
  Serial.print(pitchStd, 3);
  Serial.println(" grados)");

  // Si el sensor se movio durante la captura, el promedio no es confiable --
  // mejor rechazar el cero y pedir que se repita bien quieto, que guardar
  // uno impreciso sin avisar.
  if (rollStd > HOME_MAX_STD_DEG || pitchStd > HOME_MAX_STD_DEG) {
    Serial.println("RECHAZADO: el sensor se movio demasiado durante la captura (std > 0.5 grados). Manten el sensor bien quieto y vuelve a mandar 'z'.");
    return;
  }

  guardarZeroEnFlash(h0, r0, p0);

  Serial.print("Cero absoluto guardado en flash: heading0=");
  Serial.print(h0, 2);
  Serial.print("  roll0=");
  Serial.print(r0, 2);
  Serial.print("  pitch0=");
  Serial.println(p0, 2);
}

// ---- Calibracion de acelerometro (6 posiciones, ver calibrar_acelerometro.py) ----
// El offset (mg) se escribe directo en los registros del chip via
// setAxisOffset() -- eso es lo que de verdad mejora la precision de
// Euler[heading,roll,pitch], porque esos angulos los calcula el propio
// BNO055 usando SU acelerometro interno. Corregir el numero solo en
// software (Python/ESP32) despues de leerlo no alcanzaria: no le llega a
// la fusion interna del chip.
void guardarCalibAccelEnFlash(float x, float y, float z) {
  prefs.begin(NVS_NAMESPACE_ACCEL, false);
  prefs.putFloat("ax", x);
  prefs.putFloat("ay", y);
  prefs.putFloat("az", z);
  prefs.putBool("set", true);
  prefs.end();
}

void aplicarCalibracionAccel(float offX, float offY, float offZ, bool guardar) {
  BNO::sAxisAnalog_t offset;
  offset.x = offX;
  offset.y = offY;
  offset.z = offZ;

  bno.setOprMode(BNO::eOprModeConfig);  // los registros de offset solo se pueden escribir en modo CONFIG
  delay(25);
  bno.setAxisOffset(BNO::eAxisAcc, offset);
  delay(25);
  bno.setOprMode(BNO::eOprModeNdof);    // volver al modo de fusion normal
  delay(25);

  if (guardar) {
    guardarCalibAccelEnFlash(offX, offY, offZ);
  }

  Serial.print("Calibracion de acelerometro aplicada: offX=");
  Serial.print(offX, 1);
  Serial.print(" offY=");
  Serial.print(offY, 1);
  Serial.print(" offZ=");
  Serial.println(offZ, 1);
}

void cargarCalibAccelDesdeFlash() {
  prefs.begin(NVS_NAMESPACE_ACCEL, true);
  bool tiene = prefs.getBool("set", false);
  float x = prefs.getFloat("ax", 0);
  float y = prefs.getFloat("ay", 0);
  float z = prefs.getFloat("az", 0);
  prefs.end();
  if (tiene) {
    Serial.println("Aplicando calibracion de acelerometro guardada en flash...");
    aplicarCalibracionAccel(x, y, z, false);
  } else {
    Serial.println("No hay calibracion de acelerometro guardada todavia -- correr calibrar_acelerometro.py cuando quieras.");
  }
}

// Atiende un comando venga de donde venga (Serial o UDP), como linea de texto:
//   z              -> fija el cero absoluto actual
//   c              -> borra el cero absoluto guardado
//   a<x>,<y>,<z>   -> aplica y guarda una calibracion de acelerometro (mg)
void procesarComando(String linea) {
  linea.trim();
  if (linea.length() == 0) return;
  char primero = linea.charAt(0);

  if (primero == 'z' || primero == 'Z') {
    establecerZeroActual();
  } else if (primero == 'c' || primero == 'C') {
    borrarZeroDeFlash();
    Serial.println("Cero absoluto borrado.");
  } else if (primero == 'a' || primero == 'A') {
    String resto = linea.substring(1);
    int coma1 = resto.indexOf(',');
    int coma2 = resto.indexOf(',', coma1 + 1);
    if (coma1 > 0 && coma2 > coma1) {
      float ox = resto.substring(0, coma1).toFloat();
      float oy = resto.substring(coma1 + 1, coma2).toFloat();
      float oz = resto.substring(coma2 + 1).toFloat();
      aplicarCalibracionAccel(ox, oy, oz, true);
    } else {
      Serial.println("Formato invalido para 'a'. Usar: a<offX>,<offY>,<offZ>");
    }
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("=== Test WiFi AP propio + UDP (BNO055 DFRobot) ===");

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.print("Red WiFi propia creada: \"");
  Serial.print(AP_SSID);
  Serial.println("\"");
  Serial.print("IP del ESP32 (siempre es esta en modo AP): ");
  Serial.println(WiFi.softAPIP());
  Serial.println("Conecta tu laptop a esta red WiFi y corre visor_wifi_ap_bno055.py");

  Wire.begin(21, 22);

  if (bno.begin() != BNO::eStatusOK) {
    Serial.println("ERROR: no se detecto el BNO055. Revisar alimentacion, SDA/SCL y direccion I2C.");
    while (1) { delay(1000); }
  }
  Serial.println("BNO055 detectado correctamente.");

  cargarCalibAccelDesdeFlash();

  cargarZeroDesdeFlash();
  if (zeroIsSet) {
    Serial.print("Cero absoluto cargado de flash: heading0=");
    Serial.print(zeroHeading, 2);
    Serial.print("  roll0=");
    Serial.print(zeroRoll, 2);
    Serial.print("  pitch0=");
    Serial.println(zeroPitch, 2);
  } else {
    Serial.println("No hay ningun cero absoluto guardado todavia.");
  }
  Serial.println("Comandos 'z' (fijar cero) / 'c' (borrar cero) / 'a<x>,<y>,<z>' (calibrar accel) -- por Serial o por WiFi (UDP).");

  udp.begin(UDP_PORT);
}

void loop() {
  // En modo AP el ESP32 no se "desconecta" de si mismo, asi que no hace
  // falta la logica de reconexion que si tenia la version con red externa.

  if (Serial.available() > 0) {
    String linea = Serial.readStringUntil('\n');
    procesarComando(linea);
  }

  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    char cmdBuf[48] = {0};
    int len = udp.read(cmdBuf, sizeof(cmdBuf) - 1);
    if (len > 0) {
      cmdBuf[len] = '\0';
      procesarComando(String(cmdBuf));
    }
  }

  BNO::sRegCalibState_t calib = bno.getCalStatus();
  BNO::sEulAnalog_t eul = bno.getEul();
  BNO::sAxisAnalog_t lia = bno.getAxis(BNO::eAxisLia);
  BNO::sAxisAnalog_t accRaw = bno.getAxis(BNO::eAxisAcc);  // mg -- usado por calibrar_acelerometro.py

  float liaX = lia.x * MG_TO_MS2;
  float liaY = lia.y * MG_TO_MS2;
  float liaZ = lia.z * MG_TO_MS2;

  char buf[260];
  int len = snprintf(buf, sizeof(buf),
                      "Calib[sys,gyro,accel,mag]=%u,%u,%u,%u | Euler[heading,roll,pitch]=%.2f,%.2f,%.2f | LinAccel[x,y,z]=%.2f,%.2f,%.2f | AccRaw[x,y,z]=%.1f,%.1f,%.1f | Zero=%s",
                      calib.SYS, calib.GYR, calib.ACC, calib.MAG,
                      eul.head, eul.roll, eul.pitch,
                      liaX, liaY, liaZ,
                      accRaw.x, accRaw.y, accRaw.z,
                      zeroIsSet ? "SI" : "NO");

  if (zeroIsSet) {
    len += snprintf(buf + len, sizeof(buf) - len,
                     " | EulerAbs[heading,roll,pitch]=%.2f,%.2f,%.2f",
                     eul.head - zeroHeading, eul.roll - zeroRoll, eul.pitch - zeroPitch);
  }

  // Broadcast: le llega a cualquier laptop conectada a la red del ESP32,
  // sin tener que saber su IP de antemano.
  udp.beginPacket(BROADCAST_IP, UDP_PORT);
  udp.write((const uint8_t*)buf, len);
  udp.endPacket();

  Serial.println(buf);

  delay(100); // ~10 Hz
}
