/*
 * T-INT2 -- Adquisicion simultanea de todos los sensores de la galleta
 * (celda de carga por HX711 + 2x VL53L1X + BNO055) en el mismo ESP32.
 *
 * Objetivo de la prueba (Reportes-Semanales/S12/Resumen-Semana12.md, secc. 2.3):
 * leer celda, ToF e IMU a la vez durante 5 min y obtener la frecuencia real
 * de cada sensor, las muestras perdidas y los conflictos en el bus.
 *
 * Pinout: el mismo de la galleta 70x90 y de la PCB final
 * (Firmware/PCB_placa_superior_PINOUT.md, Registro C-29):
 *
 *   Sensor           Bus / pines                       Libreria
 *   ------           -----------                       --------
 *   HX711 (celda)    DT=GPIO32, SCK=GPIO33             "HX711" (Bogdan Necula)
 *   ToF1 (U3)        Wire  SDA=21 SCL=22, SHUT=GPIO25  "VL53L1X" (Pololu)
 *                    direccion reasignada a 0x30
 *   ToF2 (U2)        Wire  SDA=21 SCL=22, SHUT=GPIO26  "VL53L1X" (Pololu)
 *                    direccion de fabrica 0x29
 *   BNO055           Wire1 SDA=17 SCL=16, dir. 0x28    "DFRobot_BNO055"
 *
 * DIFERENCIA CON LOS SKETCHES DE PRUEBA INDIVIDUALES: en test_hx711.ino y
 * test_tof.ino las lecturas son BLOQUEANTES (wait_ready_timeout(), read()
 * esperando el dato). Con tres sensores en el mismo loop eso haria que cada
 * uno frene a los demas y la frecuencia medida seria la del loop, no la de
 * los sensores. Aqui cada sensor se lee SOLO cuando ya tiene un dato listo
 * (HX711: is_ready(); ToF: dataReady(); BNO055: cada IMU_PERIODO_MS), asi
 * el loop nunca se queda esperando.
 *
 * Que mide este sketch:
 *   - Marca de tiempo del ESP32 (micros) en cada muestra -> frecuencia real
 *     e intervalos entre muestras de cada sensor (en el PC).
 *   - Contador global de lineas (n) -> si falta un n en el PC, se perdio una
 *     linea en el Serial (problema del enlace, no del sensor).
 *   - Errores por sensor: HX711 sin datos > 500 ms; ToF con error I2C o sin
 *     datos > 500 ms; BNO055 con lectura fallida (lastOperateStatus).
 *   - Duracion de cada lectura del BNO055 (dur_us) -> si el bus Wire1 se
 *     traba (clock stretching del BNO055), aparece como picos aqui.
 *   - Duracion maxima del loop por segundo y veces que el buffer del
 *     Serial estuvo lleno (serialBloq) -> si el Serial frena la adquisicion.
 *
 * Al arrancar imprime un reporte con el escaneo I2C de ambos buses (lo que
 * tambien cubre la parte de escaneo de T-INT1) y la configuracion vigente.
 *
 * Salida por Serial (115200 baudios). Lineas que empiezan con '#' son
 * informativas. Lineas de datos (CSV con prefijo de tipo):
 *   H,n,t_us,raw,force_N
 *   T,n,t_us,sensor,dist_mm,status
 *   I,n,t_us,dur_us,ok,roll,pitch,heading,sys,gyr,acc,mag
 *   S,n,t_us,cntH,cntT1,cntT2,cntI,errH,errT1,errT2,errI,loopMax_us,serialBloq
 *   E,n,t_us,sensor,motivo,detalle
 * Los contadores de S son acumulados desde el arranque (o desde 'r');
 * loopMax_us es el maximo del ultimo segundo.
 *
 * Roll/pitch/heading del BNO055 salen CRUDOS (sin EMA, sin cero, sin
 * corregirRoll()): esta prueba evalua la adquisicion, no el angulo.
 *
 * Comandos por Serial:
 *   i -> vuelve a imprimir el reporte inicial (con el escaneo I2C guardado
 *        del arranque: no se vuelve a escanear, ver escanearBus())
 *   r -> reinicia los contadores acumulados
 *
 * Uso: cargar el sketch y correr visor_python/log_integracion.py
 * (ver INSTRUCCIONES.md).
 */

#include <Wire.h>
#include <HX711.h>
#include <VL53L1X.h>
#include <Preferences.h>
#include "DFRobot_BNO055.h"

typedef DFRobot_BNO055_IIC BNO;

// ---------------------------------------------------------------------
// Pines (galleta 70x90 = PCB final)
// ---------------------------------------------------------------------
#define PIN_HX711_DT   32
#define PIN_HX711_SCK  33
#define PIN_I2C_SDA    21   // Wire  -> ToF
#define PIN_I2C_SCL    22
#define PIN_SHUT_TOF1  25   // U3
#define PIN_SHUT_TOF2  26   // U2
#define PIN_I2C2_SDA   17   // Wire1 -> BNO055
#define PIN_I2C2_SCL   16

// ---------------------------------------------------------------------
// Configuracion de la prueba
// ---------------------------------------------------------------------
const uint32_t SERIAL_BAUD        = 115200;
const uint32_t I2C_WIRE_HZ        = 100000;  // igual que test_tof.ino (default)
const uint32_t I2C_WIRE1_HZ       = 100000;  // igual que test_wifi_ap_bno055.ino (default)
const uint8_t  DIRECCION_TOF1     = 0x30;
const uint8_t  DIRECCION_TOF2     = 0x29;
const uint8_t  DIRECCION_BNO055   = 0x28;
const uint32_t TOF_BUDGET_US      = 50000;   // igual que test_tof.ino
// 100 ms -> 10 Hz por sensor (decision 2026-11-10). Con 50 ms (igual que
// test_tof.ino) el periodo coincidia con el budget de 50 ms y el VL53L1X
// salia a ~10.8 Hz en vez de 20 Hz. Se fija 10 Hz explicito en vez de bajar
// el budget a ~33 ms para 20 Hz: menos ruido, y 0.1 s alcanza para LIBRA.
const uint32_t TOF_PERIODO_MS     = 100;
const uint32_t TOF_POLL_MS        = 5;       // cada cuanto se pregunta dataReady() (evita saturar el bus)
const uint32_t IMU_PERIODO_MS     = 100;     // igual que test_wifi_ap_bno055.ino -> 10 Hz
const uint32_t HX711_SPS_ESPERADO = 10;      // nominal (pin RATE); con oscilador interno sale ~11.5 Hz (P-18)
const uint32_t TIMEOUT_SIN_DATOS_MS = 500;   // sin dato nuevo en este tiempo -> error
const uint32_t E_MIN_INTERVALO_MS = 500;     // limita lineas E repetidas (se cuentan todas)

// ---------------------------------------------------------------------
// Objetos de los sensores
// ---------------------------------------------------------------------
HX711   balanza;
VL53L1X tof1;
VL53L1X tof2;
BNO     bno(&Wire1, DIRECCION_BNO055);
Preferences prefs;

bool hxPresente = false, tof1Presente = false, tof2Presente = false, imuPresente = false;

// Calibracion de la celda guardada por test_hx711.ino (solo lectura)
long  taraOffsetRaw = 0;
float escalaNporCount = 0.0f;
bool  taraSet = false, calibrado = false;

// ---------------------------------------------------------------------
// Contadores
// ---------------------------------------------------------------------
uint32_t nLinea = 0;
uint32_t cntH = 0, cntT1 = 0, cntT2 = 0, cntI = 0;
uint32_t errH = 0, errT1 = 0, errT2 = 0, errI = 0;
uint32_t serialBloq = 0;
uint32_t loopMaxUs = 0;

uint32_t ultimoH_ms = 0, ultimoT1_ms = 0, ultimoT2_ms = 0;
bool     hSinDatos = false, t1SinDatos = false, t2SinDatos = false;
uint32_t ultimoE_ms[4] = {0, 0, 0, 0};  // 0=HX711 1=ToF1 2=ToF2 3=BNO055

uint32_t proximoImu_ms = 0, proximoTofPoll_ms = 0, proximoS_ms = 0;

char buf[160];

// =======================================================================
// Salida
// =======================================================================

// Escribe una linea de datos. Si el buffer de TX no tiene espacio, la
// escritura bloquea hasta que se vacie: se cuenta en serialBloq para saber
// si el Serial esta frenando la adquisicion.
void emitir(int len) {
  if (len <= 0) return;
  if (len >= (int)sizeof(buf)) len = sizeof(buf) - 1;
  if (Serial.availableForWrite() < len + 1) serialBloq++;
  Serial.write((const uint8_t*)buf, len);
  Serial.write('\n');
}

const char* NOMBRE_SENSOR[4] = {"HX711", "ToF1", "ToF2", "BNO055"};

void emitirError(int idx, const char* motivo, int detalle) {
  uint32_t ahora = millis();
  if (ultimoE_ms[idx] != 0 && (ahora - ultimoE_ms[idx]) < E_MIN_INTERVALO_MS) return;
  ultimoE_ms[idx] = ahora;
  int len = snprintf(buf, sizeof(buf), "E,%lu,%lu,%s,%s,%d",
                     (unsigned long)nLinea++, (unsigned long)micros(),
                     NOMBRE_SENSOR[idx], motivo, detalle);
  emitir(len);
}

// =======================================================================
// Inicializacion
// =======================================================================

void cargarCalibracionHX711() {
  prefs.begin("libra_hx711", true);  // mismo namespace que test_hx711.ino
  taraSet = prefs.getBool("tara_set", false);
  taraOffsetRaw = prefs.getLong("tara_raw", 0);
  calibrado = prefs.getBool("cal_set", false);
  escalaNporCount = prefs.getFloat("escala", 0.0f);
  prefs.end();
}

void inicializarToF() {
  pinMode(PIN_SHUT_TOF1, OUTPUT);
  pinMode(PIN_SHUT_TOF2, OUTPUT);
  digitalWrite(PIN_SHUT_TOF1, LOW);
  digitalWrite(PIN_SHUT_TOF2, LOW);
  delay(10);

  // ToF1 sale de reset primero y se mueve a 0x30 (ver test_tof.ino)
  digitalWrite(PIN_SHUT_TOF1, HIGH);
  delay(10);
  tof1.setTimeout(500);
  tof1Presente = tof1.init();
  if (tof1Presente) tof1.setAddress(DIRECCION_TOF1);

  // ToF2 sale de reset despues y se queda en 0x29
  digitalWrite(PIN_SHUT_TOF2, HIGH);
  delay(10);
  tof2.setTimeout(500);
  tof2Presente = tof2.init();

  if (tof1Presente) {
    tof1.setDistanceMode(VL53L1X::Long);
    tof1.setMeasurementTimingBudget(TOF_BUDGET_US);
    tof1.startContinuous(TOF_PERIODO_MS);
  }
  if (tof2Presente) {
    tof2.setDistanceMode(VL53L1X::Long);
    tof2.setMeasurementTimingBudget(TOF_BUDGET_US);
    tof2.startContinuous(TOF_PERIODO_MS);
  }
}

void inicializarIMU() {
  imuPresente = (bno.begin() == BNO::eStatusOK);
  if (!imuPresente) return;
  // Igual que test_wifi_ap_bno055.ino: descartar las primeras lecturas
  // mientras se estabiliza la fusion interna (pueden salir en 0).
  for (int i = 0; i < 30; i++) {
    bno.getEul();
    delay(20);
  }
}

// Escanea un bus y guarda la linea "# SCAN ..." en 'linea' (se imprime en
// reporteInicial()). Devuelve cuantas de las esperadas respondieron.
//
// IMPORTANTE: el escaneo se hace UNA sola vez en setup(), ANTES de
// inicializarIMU(). Las transacciones vacias del escaneo (solo direccion,
// sin datos) sacan al BNO055 del modo de fusion: despues de un escaneo
// getEul() devuelve 0.00 en todo (verificado el 2026-11-10: 201/201 lecturas
// reales antes del escaneo, 201/201 en cero despues). Por eso 'i' reimprime
// el escaneo guardado en vez de volver a escanear.
char lineaScanWire[120];
char lineaScanWire1[120];

int escanearBus(TwoWire& bus, const char* nombre, const uint8_t* esperadas, int nEsperadas,
                char* linea, size_t tam) {
  int pos = snprintf(linea, tam, "# SCAN %s:", nombre);
  int encontradas = 0, total = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    bus.beginTransmission(addr);
    if (bus.endTransmission() == 0) {
      pos += snprintf(linea + pos, tam - pos, " 0x%02X", addr);
      total++;
      for (int k = 0; k < nEsperadas; k++) {
        if (esperadas[k] == addr) encontradas++;
      }
    }
  }
  if (total == 0) pos += snprintf(linea + pos, tam - pos, " (ninguno)");
  pos += snprintf(linea + pos, tam - pos, " -> esperado");
  for (int k = 0; k < nEsperadas; k++) pos += snprintf(linea + pos, tam - pos, " 0x%02X", esperadas[k]);
  snprintf(linea + pos, tam - pos, "%s", encontradas == nEsperadas ? " : OK" : " : FALTA");
  return encontradas;
}

void escanearBuses() {
  const uint8_t espWire[2]  = {DIRECCION_TOF2, DIRECCION_TOF1};
  const uint8_t espWire1[1] = {DIRECCION_BNO055};
  escanearBus(Wire,  "Wire (GPIO21/22, ToF)",     espWire,  2, lineaScanWire,  sizeof(lineaScanWire));
  escanearBus(Wire1, "Wire1 (GPIO17/16, BNO055)", espWire1, 1, lineaScanWire1, sizeof(lineaScanWire1));
}

void reporteInicial() {
  Serial.println("# === T-INT2 Adquisicion simultanea (celda + 2x ToF + BNO055) ===");
  Serial.printf("# CONFIG baud=%lu tof_periodo_ms=%lu tof_budget_us=%lu imu_periodo_ms=%lu "
                "hx711_sps_esperado=%lu i2c_wire_hz=%lu i2c_wire1_hz=%lu\n",
                (unsigned long)SERIAL_BAUD, (unsigned long)TOF_PERIODO_MS,
                (unsigned long)TOF_BUDGET_US, (unsigned long)IMU_PERIODO_MS,
                (unsigned long)HX711_SPS_ESPERADO, (unsigned long)I2C_WIRE_HZ,
                (unsigned long)I2C_WIRE1_HZ);

  Serial.println(lineaScanWire);   // escaneo hecho en setup(), ver escanearBus()
  Serial.println(lineaScanWire1);

  Serial.printf("# INIT HX711=%s ToF1=%s ToF2=%s BNO055=%s\n",
                hxPresente ? "OK" : "FALLA", tof1Presente ? "OK" : "FALLA",
                tof2Presente ? "OK" : "FALLA", imuPresente ? "OK" : "FALLA");
  Serial.printf("# CAL HX711 tara=%d calibrado=%d escala_N_por_cuenta=%.8f\n",
                taraSet ? 1 : 0, calibrado ? 1 : 0, escalaNporCount);
  Serial.println("# FORMATO H,n,t_us,raw,force_N");
  Serial.println("# FORMATO T,n,t_us,sensor,dist_mm,status");
  Serial.println("# FORMATO I,n,t_us,dur_us,ok,roll,pitch,heading,sys,gyr,acc,mag");
  Serial.println("# FORMATO S,n,t_us,cntH,cntT1,cntT2,cntI,errH,errT1,errT2,errI,loopMax_us,serialBloq");
  Serial.println("# FORMATO E,n,t_us,sensor,motivo,detalle");
  Serial.println("# LISTO");
}

void reiniciarContadores() {
  cntH = cntT1 = cntT2 = cntI = 0;
  errH = errT1 = errT2 = errI = 0;
  serialBloq = 0;
  loopMaxUs = 0;
  Serial.println("# CONTADORES REINICIADOS");
}

// =======================================================================
// Lectura de cada sensor (sin bloqueo)
// =======================================================================

void leerHX711() {
  if (!hxPresente) return;
  uint32_t ahora = millis();
  if (balanza.is_ready()) {
    uint32_t t = micros();
    long raw = balanza.read();   // ya esta listo -> no espera
    float forceN = calibrado ? (raw - taraOffsetRaw) * escalaNporCount : 0.0f;
    cntH++;
    ultimoH_ms = ahora;
    hSinDatos = false;
    int len = snprintf(buf, sizeof(buf), "H,%lu,%lu,%ld,%.4f",
                       (unsigned long)nLinea++, (unsigned long)t, raw, forceN);
    emitir(len);
  } else if (!hSinDatos && (ahora - ultimoH_ms) > TIMEOUT_SIN_DATOS_MS) {
    hSinDatos = true;  // se cuenta una vez por episodio
    errH++;
    emitirError(0, "sin_datos", (int)(ahora - ultimoH_ms));
  }
}

void leerUnToF(VL53L1X& tof, int sensor, uint32_t& cnt, uint32_t& err,
               uint32_t& ultimo_ms, bool& sinDatos) {
  uint32_t ahora = millis();
  bool listo = tof.dataReady();
  if (tof.last_status != 0) {          // fallo I2C al preguntar
    err++;
    emitirError(sensor, "i2c", tof.last_status);
    return;
  }
  if (listo) {
    uint32_t t = micros();
    uint16_t dist = tof.read(false);   // ya esta listo -> no espera
    if (tof.last_status != 0) {
      err++;
      emitirError(sensor, "i2c", tof.last_status);
      return;
    }
    uint8_t st = (uint8_t)tof.ranging_data.range_status;
    cnt++;
    ultimo_ms = ahora;
    sinDatos = false;
    int len = snprintf(buf, sizeof(buf), "T,%lu,%lu,%d,%u,%u",
                       (unsigned long)nLinea++, (unsigned long)t, sensor, dist, st);
    emitir(len);
  } else if (!sinDatos && (ahora - ultimo_ms) > TIMEOUT_SIN_DATOS_MS) {
    sinDatos = true;
    err++;
    emitirError(sensor, "sin_datos", (int)(ahora - ultimo_ms));
  }
}

void leerToF() {
  uint32_t ahora = millis();
  if ((int32_t)(ahora - proximoTofPoll_ms) < 0) return;
  proximoTofPoll_ms = ahora + TOF_POLL_MS;
  if (tof1Presente) leerUnToF(tof1, 1, cntT1, errT1, ultimoT1_ms, t1SinDatos);
  if (tof2Presente) leerUnToF(tof2, 2, cntT2, errT2, ultimoT2_ms, t2SinDatos);
}

// Lectura de Euler con verificacion. Con bno.getEul() de la libreria (una
// lectura de 6 bytes), ~1-2 % de las muestras llegaban corruptas y pasaban
// como validas: los 2 primeros bytes (heading) siempre bien, y del 3.o en
// adelante 0xFF o bits cambiados (ej. roll=-0.06 o -5.69 en vez de -37.69;
// medido el 2026-11-10, core ESP32 3.3.12). Las lecturas de 1-2 bytes no
// mostraron ese problema, asi que cada angulo se lee en su propia
// transaccion de 2 bytes (registros 0x1A/0x1C/0x1E, pagina 0 -- la deja
// seleccionada getCalStatus()). Aun asi ~0.9 % de las lecturas de 2 bytes
// salian con un bit cambiado (roll -5.81 en vez de -37.81: byte alto 0xFD ->
// 0xFF), asi que cada eje se lee hasta 3 veces y solo se acepta cuando dos
// lecturas seguidas coinciden: una corrupcion aleatoria no se repite igual.
// Escala igual que getEul(): 1 grado = 16 LSB.
bool leerEjeCrudo(uint8_t reg, int16_t& raw) {
  Wire1.beginTransmission(DIRECCION_BNO055);
  Wire1.write(reg);
  if (Wire1.endTransmission() != 0) return false;
  if (Wire1.requestFrom(DIRECCION_BNO055, (uint8_t)2) != 2) {
    while (Wire1.available()) Wire1.read();
    return false;
  }
  uint8_t lo = Wire1.read(), hi = Wire1.read();
  raw = (int16_t)((hi << 8) | lo);
  return true;
}

bool leerEje(uint8_t reg, float& valor) {
  int16_t anterior = 0, actual = 0;
  bool hayAnterior = false;
  for (int intento = 0; intento < 3; intento++) {
    if (!leerEjeCrudo(reg, actual)) { hayAnterior = false; continue; }
    if (hayAnterior && actual == anterior) {
      valor = actual / 16.0f;
      return true;
    }
    anterior = actual;
    hayAnterior = true;
  }
  valor = 0.0f;
  return false;
}

bool leerEulerVerificado(BNO::sEulAnalog_t& eul) {
  bool okH = leerEje(0x1A, eul.head);
  bool okR = leerEje(0x1C, eul.roll);
  bool okP = leerEje(0x1E, eul.pitch);
  return okH && okR && okP;
}

void leerIMU() {
  if (!imuPresente) return;
  uint32_t ahora = millis();
  if ((int32_t)(ahora - proximoImu_ms) < 0) return;
  // Base de tiempo fija (no acumula deriva); si se atraso mas de un
  // periodo, se resincroniza en vez de leer varias veces seguidas.
  proximoImu_ms += IMU_PERIODO_MS;
  if ((int32_t)(ahora - proximoImu_ms) > 0) proximoImu_ms = ahora + IMU_PERIODO_MS;

  uint32_t t0 = micros();
  BNO::sRegCalibState_t calib = bno.getCalStatus();
  bool ok = (bno.lastOperateStatus == BNO::eStatusOK);
  BNO::sEulAnalog_t eul;
  ok = leerEulerVerificado(eul) && ok;
  uint32_t dur = micros() - t0;

  cntI++;
  if (!ok) {
    errI++;
    emitirError(3, "lectura", (int)bno.lastOperateStatus);
  }
  int len = snprintf(buf, sizeof(buf), "I,%lu,%lu,%lu,%d,%.2f,%.2f,%.2f,%u,%u,%u,%u",
                     (unsigned long)nLinea++, (unsigned long)t0, (unsigned long)dur,
                     ok ? 1 : 0, eul.roll, eul.pitch, eul.head,
                     calib.SYS, calib.GYR, calib.ACC, calib.MAG);
  emitir(len);
}

void emitirEstado() {
  uint32_t ahora = millis();
  if ((int32_t)(ahora - proximoS_ms) < 0) return;
  proximoS_ms += 1000;
  if ((int32_t)(ahora - proximoS_ms) > 0) proximoS_ms = ahora + 1000;
  int len = snprintf(buf, sizeof(buf), "S,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu",
                     (unsigned long)nLinea++, (unsigned long)micros(),
                     (unsigned long)cntH, (unsigned long)cntT1, (unsigned long)cntT2,
                     (unsigned long)cntI, (unsigned long)errH, (unsigned long)errT1,
                     (unsigned long)errT2, (unsigned long)errI,
                     (unsigned long)loopMaxUs, (unsigned long)serialBloq);
  emitir(len);
  loopMaxUs = 0;
}

void atenderComandos() {
  if (Serial.available() <= 0) return;
  String linea = Serial.readStringUntil('\n');
  linea.trim();
  if (linea.length() == 0) return;
  char c = linea.charAt(0);
  if (c == 'i' || c == 'I') reporteInicial();
  else if (c == 'r' || c == 'R') reiniciarContadores();
  else Serial.println("# Comandos: i (reporte/escaneo I2C) | r (reiniciar contadores)");
}

// =======================================================================
// setup() / loop()
// =======================================================================

void setup() {
  Serial.setTxBufferSize(1024);  // debe ir antes de begin()
  Serial.begin(SERIAL_BAUD);
  while (!Serial) delay(10);
  Serial.setTimeout(20);         // readStringUntil no debe frenar el loop

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(I2C_WIRE_HZ);
  Wire1.begin(PIN_I2C2_SDA, PIN_I2C2_SCL);
  Wire1.setClock(I2C_WIRE1_HZ);

  balanza.begin(PIN_HX711_DT, PIN_HX711_SCK, 128);
  hxPresente = balanza.wait_ready_timeout(2000);
  cargarCalibracionHX711();

  inicializarToF();
  escanearBuses();   // despues de los ToF (ToF1 ya en 0x30) y ANTES del BNO055
  inicializarIMU();

  reporteInicial();

  uint32_t ahora = millis();
  ultimoH_ms = ultimoT1_ms = ultimoT2_ms = ahora;
  proximoImu_ms = ahora;
  proximoTofPoll_ms = ahora;
  proximoS_ms = ahora + 1000;
}

void loop() {
  uint32_t t0 = micros();

  atenderComandos();
  leerHX711();
  leerToF();
  leerIMU();
  emitirEstado();

  uint32_t dur = micros() - t0;
  if (dur > loopMaxUs) loopMaxUs = dur;
}
