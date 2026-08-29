/*
 * Homing / cero absoluto persistente para el pivote de flexo-extension
 * Sensor: MPU6050 (misma logica aplica al BNO055, ver nota al final)
 * Plataforma: ESP32 (I2C)
 *
 * IDEA (surge de la conversacion sobre "a = g*cos(theta)"):
 * la gravedad es una referencia absoluta que no se apaga ni deriva con el
 * tiempo. Si defines que "cero grados de flexion" corresponde a una
 * orientacion conocida respecto a la gravedad (ej. el pylon perfectamente
 * vertical), puedes usar el acelerometro para "anclar" ese cero -- y si
 * ademas guardas ese valor en la memoria flash del ESP32 (no en RAM), el
 * cero SOBREVIVE a apagar y encender el sistema. Eso es justo lo que
 * resuelve el pendiente de "referencia de posicion absoluta" para el eje
 * de rotacion (NO resuelve el eje de traslacion -- ahi sigue haciendo
 * falta un encoder absoluto o un switch de home, como ya quedo anotado).
 *
 * LIMITACION IMPORTANTE: esto solo es valido con el sistema QUIETO en el
 * momento de establecer el cero -- si hay movimiento, el acelerometro mide
 * gravedad + aceleracion dinamica mezcladas, y el "cero" quedaria mal
 * capturado. Es una rutina de HOMING (se hace una vez al empezar cada
 * sesion de ensayo), no una medicion continua de referencia absoluta.
 *
 * Comandos por Serial (escribe la letra y Enter en el Monitor Serie):
 *   z  -> Establece la posicion ACTUAL como cero absoluto (pide mantener
 *         quieto el pivote en la posicion de referencia ~1 s) y lo guarda
 *         en la memoria flash (Preferences/NVS del ESP32).
 *   c  -> Borra el cero guardado (vuelve a "sin calibrar").
 *
 * Salida CSV normal: roll,pitch (relativos al cero guardado, o crudos si
 * todavia no se estableció ningún cero), zero_set (0/1).
 *
 * Librerias requeridas: Adafruit MPU6050, Adafruit Unified Sensor,
 * Adafruit BusIO (Preferences.h ya viene incluida en el core de ESP32).
 *
 * Conexionado: igual que test_mpu6050.ino (VCC->3V3, GND->GND, SDA->GPIO21,
 * SCL->GPIO22, AD0->GND para direccion 0x68).
 */

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Preferences.h>

Adafruit_MPU6050 mpu;
Preferences prefs;

#define GYRO_WEIGHT 0.98f
const char* NVS_NAMESPACE = "libra_home";

// --- Estado del filtro complementario (igual que en test_mpu6050.ino) ---
float roll = 0, pitch = 0;
unsigned long lastTime = 0;
float gyroBiasX = 0, gyroBiasY = 0, gyroBiasZ = 0;
const int CAL_SAMPLES = 200;

// --- Cero absoluto (cargado/guardado en flash) ---
float zeroRoll = 0, zeroPitch = 0;
bool zeroIsSet = false;
const int HOME_SAMPLES = 100; // ~1 s de promedio al establecer el cero

void calibrarGiro() {
  Serial.println("Calibrando giroscopio -- manten el sensor quieto...");
  double sumX = 0, sumY = 0, sumZ = 0;
  sensors_event_t a, g, temp;
  for (int i = 0; i < CAL_SAMPLES; i++) {
    mpu.getEvent(&a, &g, &temp);
    sumX += g.gyro.x; sumY += g.gyro.y; sumZ += g.gyro.z;
    delay(5);
  }
  gyroBiasX = sumX / CAL_SAMPLES;
  gyroBiasY = sumY / CAL_SAMPLES;
  gyroBiasZ = sumZ / CAL_SAMPLES;
}

void cargarZeroDesdeFlash() {
  prefs.begin(NVS_NAMESPACE, true); // solo lectura
  zeroIsSet = prefs.getBool("zero_set", false);
  if (zeroIsSet) {
    zeroRoll = prefs.getFloat("zero_roll", 0);
    zeroPitch = prefs.getFloat("zero_pitch", 0);
  }
  prefs.end();
}

void guardarZeroEnFlash(float r, float p) {
  prefs.begin(NVS_NAMESPACE, false); // lectura/escritura
  prefs.putFloat("zero_roll", r);
  prefs.putFloat("zero_pitch", p);
  prefs.putBool("zero_set", true);
  prefs.end();
  zeroRoll = r;
  zeroPitch = p;
  zeroIsSet = true;
}

void borrarZeroDeFlash() {
  prefs.begin(NVS_NAMESPACE, false);
  prefs.clear();
  prefs.end();
  zeroRoll = 0;
  zeroPitch = 0;
  zeroIsSet = false;
}

// Promedia SOLO el angulo derivado del acelerometro (sin el giro) durante
// HOME_SAMPLES muestras, y lo guarda como el nuevo cero absoluto.
void establecerZeroActual() {
  Serial.println("Estableciendo cero absoluto -- MANTEN EL PIVOTE QUIETO en la posicion de referencia...");
  double sumRoll = 0, sumPitch = 0;
  sensors_event_t a, g, temp;

  for (int i = 0; i < HOME_SAMPLES; i++) {
    mpu.getEvent(&a, &g, &temp);
    float r = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
    float p = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
    sumRoll += r;
    sumPitch += p;
    delay(10);
  }

  float r0 = sumRoll / HOME_SAMPLES;
  float p0 = sumPitch / HOME_SAMPLES;
  guardarZeroEnFlash(r0, p0);

  Serial.print("Cero absoluto guardado en flash: roll0=");
  Serial.print(r0, 2);
  Serial.print("  pitch0=");
  Serial.println(p0, 2);
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("=== Homing / cero absoluto persistente (MPU6050) ===");

  Wire.begin(21, 22);

  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("ERROR: no se detecto el MPU6050. Revisar alimentacion, SDA/SCL y direccion I2C.");
    while (1) { delay(1000); }
  }

  Serial.println("MPU6050 detectado correctamente.");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(300);
  calibrarGiro();

  cargarZeroDesdeFlash();
  if (zeroIsSet) {
    Serial.print("Cero absoluto cargado de la memoria flash: roll0=");
    Serial.print(zeroRoll, 2);
    Serial.print("  pitch0=");
    Serial.println(zeroPitch, 2);
  } else {
    Serial.println("No hay ningun cero guardado todavia.");
  }
  Serial.println("Comandos: 'z' + Enter = establecer cero actual | 'c' + Enter = borrar cero guardado");

  // Inicializar el filtro con el angulo crudo del acelerometro
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  roll  = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  pitch = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
  lastTime = millis();

  Serial.println("roll,pitch,roll_abs,pitch_abs,zero_set");
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

  // --- Filtro complementario (igual que test_mpu6050.ino) ---
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0f;
  lastTime = now;

  float gx = g.gyro.x - gyroBiasX;
  float gy = g.gyro.y - gyroBiasY;

  float accelRoll  = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  float accelPitch = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;

  float gyroRollRate  = gx * 180.0 / PI;
  float gyroPitchRate = gy * 180.0 / PI;

  roll  = GYRO_WEIGHT * (roll  + gyroRollRate  * dt) + (1.0f - GYRO_WEIGHT) * accelRoll;
  pitch = GYRO_WEIGHT * (pitch + gyroPitchRate * dt) + (1.0f - GYRO_WEIGHT) * accelPitch;

  // --- Angulo relativo al cero absoluto guardado ---
  float rollAbs  = roll  - zeroRoll;
  float pitchAbs = pitch - zeroPitch;

  Serial.print(roll, 2); Serial.print(",");
  Serial.print(pitch, 2); Serial.print(",");
  Serial.print(rollAbs, 2); Serial.print(",");
  Serial.print(pitchAbs, 2); Serial.print(",");
  Serial.println(zeroIsSet ? 1 : 0);

  delay(20); // ~50 Hz
}

/*
 * Nota para adaptar esto al BNO055: la logica de homing/flash es identica
 * -- lo unico que cambia es de donde sacas roll/pitch. En vez del filtro
 * complementario de aca, usarias directamente
 * bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER) (como en
 * test_bno055.ino) para roll/pitch, y el resto (establecerZeroActual,
 * guardarZeroEnFlash, cargarZeroDesdeFlash) se reusa igual.
 */
