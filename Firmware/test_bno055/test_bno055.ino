/*
 * Test de comunicacion y lectura basica -- IMU BNO055 (Bosch)
 * Plataforma: ESP32 (I2C)
 *
 * Librerias requeridas (Arduino IDE > Herramientas > Administrar bibliotecas):
 *   - Adafruit BNO055
 *   - Adafruit Unified Sensor
 *   (Wire ya viene incluida en el core de Arduino/ESP32)
 *
 * Conexionado (I2C, direccion por defecto 0x28, pin ADR a GND o sin conectar):
 *   BNO055 VIN  -> ESP32 3V3
 *   BNO055 GND  -> ESP32 GND
 *   BNO055 SDA  -> ESP32 GPIO21 (SDA por defecto)
 *   BNO055 SCL  -> ESP32 GPIO22 (SCL por defecto)
 *   BNO055 ADR  -> GND (direccion 0x28) o 3V3 (direccion 0x29, usar BNO055_ADDRESS_B)
 *   BNO055 RST  -> opcional, no es necesario conectarlo para esta prueba
 *
 * Que hace este sketch:
 *   1. Verifica que el sensor responde en el bus I2C (detecta el chip).
 *   2. Imprime el estado de calibracion (sistema, giroscopio, acelerometro,
 *      magnetometro), cada uno de 0 (sin calibrar) a 3 (totalmente calibrado).
 *   3. Imprime orientacion (Euler: heading/roll/pitch), aceleracion lineal
 *      y temperatura cada 200 ms por el puerto serie (115200 baudios).
 *   4. Permite establecer un CERO ABSOLUTO persistente (homing): con el
 *      pivote quieto en la posicion de referencia, se guarda el heading/
 *      roll/pitch actual en la memoria flash del ESP32 (Preferences/NVS),
 *      y a partir de ahi se reportan tambien los angulos relativos a ese
 *      cero. El cero sobrevive apagar y encender el ESP32.
 *
 * Comandos por Serial (escribe la letra y Enter en el Monitor Serie):
 *   z  -> Establece la orientacion ACTUAL como cero absoluto (pide mantener
 *         quieto el pivote ~1 s) y lo guarda en flash.
 *   c  -> Borra el cero guardado (vuelve a "sin calibrar").
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <Preferences.h>

// Direccion I2C por defecto (ADR a GND). Cambiar a BNO055_ADDRESS_B si ADR esta a 3V3.
Adafruit_BNO055 bno = Adafruit_BNO055(55, BNO055_ADDRESS_A, &Wire);

Preferences prefs;
const char* NVS_NAMESPACE = "libra_home";
const int HOME_SAMPLES = 100; // muestras a promediar al establecer el cero (~1 s a 10 ms/muestra)

// --- Cero absoluto (cargado/guardado en flash) ---
float zeroHeading = 0, zeroRoll = 0, zeroPitch = 0;
bool zeroIsSet = false;

void cargarZeroDesdeFlash() {
  prefs.begin(NVS_NAMESPACE, true); // solo lectura
  zeroIsSet = prefs.getBool("zero_set", false);
  if (zeroIsSet) {
    zeroHeading = prefs.getFloat("zero_heading", 0);
    zeroRoll = prefs.getFloat("zero_roll", 0);
    zeroPitch = prefs.getFloat("zero_pitch", 0);
  }
  prefs.end();
}

void guardarZeroEnFlash(float h, float r, float p) {
  prefs.begin(NVS_NAMESPACE, false); // lectura/escritura
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

// Promedia HOME_SAMPLES lecturas de orientacion (con el pivote quieto) y las
// guarda como el nuevo cero absoluto persistente.
void establecerZeroActual() {
  Serial.println("Estableciendo cero absoluto -- MANTEN EL SENSOR QUIETO en la posicion de referencia...");
  double sumHeading = 0, sumRoll = 0, sumPitch = 0;
  sensors_event_t orientationData;

  for (int i = 0; i < HOME_SAMPLES; i++) {
    bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
    sumHeading += orientationData.orientation.x;
    sumRoll += orientationData.orientation.y;
    sumPitch += orientationData.orientation.z;
    delay(10);
  }

  float h0 = sumHeading / HOME_SAMPLES;
  float r0 = sumRoll / HOME_SAMPLES;
  float p0 = sumPitch / HOME_SAMPLES;
  guardarZeroEnFlash(h0, r0, p0);

  Serial.print("Cero absoluto guardado en flash: heading0=");
  Serial.print(h0, 2);
  Serial.print("  roll0=");
  Serial.print(r0, 2);
  Serial.print("  pitch0=");
  Serial.println(p0, 2);
}

// Escanea el bus I2C e imprime por Serial las direcciones que respondan.
// Util para diagnosticar cableado sin depender del debugger JTAG.
void scanI2C() {
  Serial.println("Escaneando bus I2C...");
  uint8_t encontrados = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("  Dispositivo I2C encontrado en 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      encontrados++;
    }
  }
  if (encontrados == 0) {
    Serial.println("  Ningun dispositivo I2C respondio. Revisar alimentacion y cableado SDA/SCL.");
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("=== Test IMU BNO055 ===");

  // I2C en pines por defecto de ESP32 (SDA=21, SCL=22). Ajustar si el cableado es distinto.
  Wire.begin(21, 22);

  scanI2C();

  if (!bno.begin()) {
    Serial.println("ERROR: no se detecto el BNO055. Revisar:");
    Serial.println(" - Alimentacion (3.3V y GND)");
    Serial.println(" - SDA/SCL en los pines correctos");
    Serial.println(" - Direccion I2C (ADR a GND=0x28, a 3V3=0x29)");
    while (1) { delay(1000); }
  }

  Serial.println("BNO055 detectado correctamente.");
  delay(1000);

  bno.setExtCrystalUse(true); // usar el cristal externo del BNO055 (mayor precision)

  cargarZeroDesdeFlash();
  if (zeroIsSet) {
    Serial.print("Cero absoluto cargado de la memoria flash: heading0=");
    Serial.print(zeroHeading, 2);
    Serial.print("  roll0=");
    Serial.print(zeroRoll, 2);
    Serial.print("  pitch0=");
    Serial.println(zeroPitch, 2);
  } else {
    Serial.println("No hay ningun cero absoluto guardado todavia.");
  }
  Serial.println("Comandos: 'z' + Enter = establecer cero actual | 'c' + Enter = borrar cero guardado");
}

void loop() {
  // --- Comandos por Serial ---
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'z' || c == 'Z') {
      establecerZeroActual();
    } else if (c == 'c' || c == 'C') {
      borrarZeroDeFlash();
      Serial.println("Cero absoluto borrado.");
    }
  }

  // --- Estado de calibracion (0 = sin calibrar, 3 = totalmente calibrado) ---
  uint8_t sys, gyro, accel, mag;
  bno.getCalibration(&sys, &gyro, &accel, &mag);

  // --- Orientacion (Euler, en grados) ---
  sensors_event_t orientationData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);

  // --- Aceleracion lineal (sin gravedad, m/s^2) ---
  sensors_event_t linAccelData;
  bno.getEvent(&linAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);

  int8_t temp = bno.getTemp();

  Serial.print("Calib[sys,gyro,accel,mag]=");
  Serial.print(sys); Serial.print(",");
  Serial.print(gyro); Serial.print(",");
  Serial.print(accel); Serial.print(",");
  Serial.print(mag);

  Serial.print("  |  Euler[heading,roll,pitch]=");
  Serial.print(orientationData.orientation.x, 2); Serial.print(",");
  Serial.print(orientationData.orientation.y, 2); Serial.print(",");
  Serial.print(orientationData.orientation.z, 2);

  Serial.print("  |  LinAccel[x,y,z]=");
  Serial.print(linAccelData.acceleration.x, 2); Serial.print(",");
  Serial.print(linAccelData.acceleration.y, 2); Serial.print(",");
  Serial.print(linAccelData.acceleration.z, 2);

  Serial.print("  |  Temp="); Serial.print(temp); Serial.print(" C");

  Serial.print("  |  Zero="); Serial.print(zeroIsSet ? "SI" : "NO");
  if (zeroIsSet) {
    Serial.print("  |  EulerAbs[heading,roll,pitch]=");
    Serial.print(orientationData.orientation.x - zeroHeading, 2); Serial.print(",");
    Serial.print(orientationData.orientation.y - zeroRoll, 2); Serial.print(",");
    Serial.print(orientationData.orientation.z - zeroPitch, 2);
  }
  Serial.println();

  delay(200);
}
