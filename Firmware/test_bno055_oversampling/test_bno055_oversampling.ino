/*
 * Test IMU BNO055 con SOBREMUESTREO (oversampling) por software
 * Plataforma: ESP32 (I2C)
 *
 * Idea: el BNO055 ya entrega orientacion fusionada (Euler), pero esa señal
 * sigue teniendo ruido aleatorio de muestra a muestra. Si tomamos N lecturas
 * seguidas y las promediamos antes de usar/registrar el dato, el ruido
 * aleatorio (no correlacionado entre muestras) baja aproximadamente en un
 * factor sqrt(N) -- el mismo principio que promediar varios IMUs físicos,
 * pero sin hardware extra. OJO: esto reduce ruido aleatorio, NO corrige un
 * bias/drift sistematico (para eso hace falta calibracion, no sobremuestreo).
 *
 * Detalle importante: los angulos NO se pueden promediar como numeros
 * comunes porque el heading da la vuelta en 0/360 (p. ej. promediar 359 y 1
 * "a mano" da 180, cuando el resultado correcto es 0). Por eso aqui se
 * promedia el VECTOR (seno, coseno) de cada angulo y se reconstruye el
 * angulo promedio con atan2 -- esto es lo tecnicamente correcto.
 *
 * Trade-off tasa de salida vs. reduccion de ruido:
 *   tasa_salida (Hz) = 1000 / (N_SAMPLES * SAMPLE_INTERVAL_MS)
 *   Con los valores por defecto (N_SAMPLES=10, SAMPLE_INTERVAL_MS=10 ms):
 *   1000 / (10*10) = 10 Hz de salida.
 *   Si tu requerimiento es mantener >=100 Hz de salida (ver README del
 *   proyecto), baja N_SAMPLES (menos reduccion de ruido) o el intervalo
 *   entre muestras crudas (si el BNO055 puede entregar datos mas rapido).
 *
 * Salida por Serial (CSV, 115200 baudios), pensada para pegar directo a un
 * .csv y comparar en Excel/Python:
 *   raw_heading,raw_roll,raw_pitch,avg_heading,avg_roll,avg_pitch,n,sys,gyro,accel,mag
 *   - raw_*: la PRIMERA muestra cruda del bloque (sin promediar)
 *   - avg_*: el promedio de las N muestras del bloque
 *
 * Como comprobar que el sobremuestreo realmente reduce el ruido:
 *   1. Dejar el sensor QUIETO sobre una superficie estable.
 *   2. Correr primero test_bno055.ino (sin promediar) y guardar ~30 s de
 *      datos crudos (raw_heading/roll/pitch) en un .csv.
 *   3. Correr este sketch y guardar ~30 s de avg_heading/roll/pitch.
 *   4. Calcular la desviacion estandar de cada columna: la de "avg" deberia
 *      salir menor que la de "raw" (idealmente cerca de raw_std / sqrt(N)).
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <math.h>

Adafruit_BNO055 bno = Adafruit_BNO055(55, BNO055_ADDRESS_A, &Wire);

// --- Configuracion de sobremuestreo ---
#define N_SAMPLES          10   // muestras crudas promediadas por cada dato reportado
#define SAMPLE_INTERVAL_MS 10   // separacion entre muestras crudas (10 ms ~ 100 Hz de muestreo interno)

// Acumuladores vectoriales (seno/coseno) para promediar angulos sin problema de wraparound
float sumSinH = 0, sumCosH = 0; // heading (0-360 grados)
float sumSinR = 0, sumCosR = 0; // roll
float sumSinP = 0, sumCosP = 0; // pitch
uint16_t sampleCount = 0;

float firstRawH = 0, firstRawR = 0, firstRawP = 0; // primer valor crudo del bloque (para comparar)

unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("=== Test IMU BNO055 con sobremuestreo ===");

  Wire.begin(21, 22);

  if (!bno.begin()) {
    Serial.println("ERROR: no se detecto el BNO055. Revisar alimentacion, SDA/SCL y direccion I2C.");
    while (1) { delay(1000); }
  }

  Serial.println("BNO055 detectado correctamente.");
  delay(1000);
  bno.setExtCrystalUse(true);

  Serial.println("raw_heading,raw_roll,raw_pitch,avg_heading,avg_roll,avg_pitch,n,sys,gyro,accel,mag");
}

void loop() {
  unsigned long now = millis();
  if (now - lastSampleTime < SAMPLE_INTERVAL_MS) return; // aun no toca tomar la siguiente muestra cruda
  lastSampleTime = now;

  sensors_event_t orientationData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);

  float h = orientationData.orientation.x; // heading, 0-360
  float r = orientationData.orientation.y; // roll
  float p = orientationData.orientation.z; // pitch

  if (sampleCount == 0) {
    firstRawH = h; firstRawR = r; firstRawP = p; // guardar la primera muestra cruda del bloque
  }

  // Acumular como vector unitario para promediar angulos correctamente
  sumSinH += sin(radians(h)); sumCosH += cos(radians(h));
  sumSinR += sin(radians(r)); sumCosR += cos(radians(r));
  sumSinP += sin(radians(p)); sumCosP += cos(radians(p));
  sampleCount++;

  if (sampleCount >= N_SAMPLES) {
    float avgH = degrees(atan2(sumSinH / N_SAMPLES, sumCosH / N_SAMPLES));
    float avgR = degrees(atan2(sumSinR / N_SAMPLES, sumCosR / N_SAMPLES));
    float avgP = degrees(atan2(sumSinP / N_SAMPLES, sumCosP / N_SAMPLES));
    if (avgH < 0) avgH += 360; // volver al rango 0-360, igual que el BNO055

    uint8_t sys, gyro, accel, mag;
    bno.getCalibration(&sys, &gyro, &accel, &mag);

    Serial.print(firstRawH, 2); Serial.print(",");
    Serial.print(firstRawR, 2); Serial.print(",");
    Serial.print(firstRawP, 2); Serial.print(",");
    Serial.print(avgH, 2); Serial.print(",");
    Serial.print(avgR, 2); Serial.print(",");
    Serial.print(avgP, 2); Serial.print(",");
    Serial.print(N_SAMPLES); Serial.print(",");
    Serial.print(sys); Serial.print(",");
    Serial.print(gyro); Serial.print(",");
    Serial.print(accel); Serial.print(",");
    Serial.println(mag);

    // reiniciar acumuladores para el siguiente bloque
    sumSinH = sumCosH = 0;
    sumSinR = sumCosR = 0;
    sumSinP = sumCosP = 0;
    sampleCount = 0;
  }
}
