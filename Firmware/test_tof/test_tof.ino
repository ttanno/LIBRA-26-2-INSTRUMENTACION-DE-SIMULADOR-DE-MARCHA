/*
 * Test de comunicacion y lectura basica -- 2x VL53L1X (sensores de distancia
 * ToF, ST Microelectronics), mismo bus I2C, con reasignacion de direccion.
 * Plataforma: ESP32 (I2C)
 *
 * Ver pinout completo y justificacion de la asignacion de pines en
 * Firmware/PCB_placa_superior_PINOUT.md (Secc. 2-4). Resumen:
 *
 *   Señal                ESP32      Notas
 *   -----                -----      -----
 *   I2C SDA (compartido) GPIO21     pin I2C por defecto del ESP32
 *   I2C SCL (compartido) GPIO22     pin I2C por defecto del ESP32
 *   SHUT ToF1 (U3)       GPIO25     XSHUT, activo en bajo -- salida del ESP32
 *   SHUT ToF2 (U2)       GPIO26     XSHUT, activo en bajo -- salida del ESP32
 *   INT ToF1 / ToF2      NC         no se usa, este sketch lee por polling
 *
 * POR QUE HACE FALTA REASIGNAR DIRECCION: los dos VL53L1X vienen de fabrica
 * con la misma direccion I2C fija (0x29), asi que no se pueden diferenciar
 * en el mismo bus por direccion sola. Se resuelve con el pin SHUT de cada
 * uno: se mantienen ambos en reset, se saca a uno del reset y se le asigna
 * una direccion nueva (0x30) ANTES de sacar al segundo del reset -- asi
 * cuando el segundo arranca (todavia en 0x29 de fabrica) no choca con el
 * primero, que ya se movio.
 *
 * Libreria requerida (Arduino IDE > Herramientas > Administrar bibliotecas):
 *   - "VL53L1X" de Pololu (https://github.com/pololu/vl53l1x-arduino)
 *   (Wire ya viene incluida en el core de Arduino/ESP32)
 *
 * Que hace este sketch:
 *   1. Resetea ambos sensores via SHUT, saca al ToF1 del reset y le asigna
 *      la direccion 0x30, luego saca al ToF2 del reset (se queda en 0x29).
 *   2. Escanea el bus I2C e imprime las direcciones encontradas (deberian
 *      aparecer 0x29 y 0x30 si la reasignacion funciono).
 *   3. Inicializa ambos sensores en modo "Long" (alcance hasta ~4 m) y
 *      arranca lecturas continuas.
 *   4. Imprime por Serial (115200 baudios) la distancia de cada sensor en
 *      mm y su codigo de estado cada ciclo.
 *
 * Este sketch NO tiene comandos de calibracion por Serial: el VL53L1X ya
 * viene calibrado de fabrica (compensacion de offset/crosstalk interna del
 * chip ST) y no hace falta un paso de tara/escala como con el HX711 -- es
 * solo una prueba de wiring/direccionamiento y lectura basica.
 */

#include <Wire.h>
#include <VL53L1X.h>

// ---------------------------------------------------------------------
// Pines (ajustar si tu cableado es distinto al de PCB_placa_superior_PINOUT.md)
// ---------------------------------------------------------------------
#define PIN_I2C_SDA   21
#define PIN_I2C_SCL   22
#define PIN_SHUT_TOF1 25  // U3
#define PIN_SHUT_TOF2 26  // U2

const uint8_t DIRECCION_TOF1 = 0x30;  // reasignada; ToF2 se queda en la de fabrica (0x29)

VL53L1X tof1;
VL53L1X tof2;

// Escanea el bus I2C e imprime por Serial las direcciones que respondan.
// Util para confirmar que la reasignacion de direccion funciono (deberian
// verse 0x29 y 0x30) sin depender del debugger JTAG.
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

// Mantiene ambos sensores en reset (SHUT en bajo), saca al ToF1 y le
// reasigna direccion, y recien despues saca al ToF2 (se queda en 0x29).
void inicializarSensoresConDireccion() {
  pinMode(PIN_SHUT_TOF1, OUTPUT);
  pinMode(PIN_SHUT_TOF2, OUTPUT);

  digitalWrite(PIN_SHUT_TOF1, LOW);
  digitalWrite(PIN_SHUT_TOF2, LOW);
  delay(10);  // asegurar que ambos queden apagados/en reset

  // --- ToF1: sale de reset primero, todavia en la direccion de fabrica (0x29) ---
  digitalWrite(PIN_SHUT_TOF1, HIGH);
  delay(10);
  tof1.setTimeout(500);
  if (!tof1.init()) {
    Serial.println("ERROR: no se detecto ToF1 (U3) en 0x29. Revisar SHUT/alimentacion/cableado.");
  } else {
    tof1.setAddress(DIRECCION_TOF1);
    Serial.print("ToF1 (U3) inicializado y reasignado a 0x");
    Serial.println(DIRECCION_TOF1, HEX);
  }

  // --- ToF2: sale de reset recien ahora, no choca porque ToF1 ya se movio ---
  digitalWrite(PIN_SHUT_TOF2, HIGH);
  delay(10);
  tof2.setTimeout(500);
  if (!tof2.init()) {
    Serial.println("ERROR: no se detecto ToF2 (U2) en 0x29. Revisar SHUT/alimentacion/cableado.");
  } else {
    Serial.println("ToF2 (U2) inicializado en 0x29 (direccion de fabrica).");
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("=== Test 2x VL53L1X (ToF) ===");

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);

  inicializarSensoresConDireccion();
  scanI2C();

  tof1.setDistanceMode(VL53L1X::Long);
  tof1.setMeasurementTimingBudget(50000);
  tof1.startContinuous(50);

  tof2.setDistanceMode(VL53L1X::Long);
  tof2.setMeasurementTimingBudget(50000);
  tof2.startContinuous(50);

  Serial.println("dist1_mm,status1,dist2_mm,status2");
}

void loop() {
  uint16_t dist1 = tof1.read();
  uint8_t status1 = tof1.ranging_data.range_status;
  if (tof1.timeoutOccurred()) {
    Serial.println("ERROR: timeout esperando datos de ToF1 (revisar cableado/alimentacion).");
  }

  uint16_t dist2 = tof2.read();
  uint8_t status2 = tof2.ranging_data.range_status;
  if (tof2.timeoutOccurred()) {
    Serial.println("ERROR: timeout esperando datos de ToF2 (revisar cableado/alimentacion).");
  }

  Serial.print(dist1);
  Serial.print(",");
  Serial.print(status1);
  Serial.print(",");
  Serial.print(dist2);
  Serial.print(",");
  Serial.println(status2);
}
