/*
 * Test IMU MPU6050 (6 ejes: acelerometro + giroscopio, SIN magnetometro)
 * Plataforma: ESP32 (I2C)
 *
 * Diferencia clave con el BNO055 que ya probaste: el MPU6050 NO tiene fusion
 * de sensores integrada ni magnetometro. Este sketch calcula roll y pitch
 * con un FILTRO COMPLEMENTARIO propio (acelerometro + giroscopio) -- es
 * exactamente el tipo de trabajo de software que el BNO055 te ahorraba.
 * El YAW (heading) NO se puede obtener de forma absoluta sin magnetometro:
 * aqui se muestra tambien un "yaw_solo_giro" (integracion pura del giro Z)
 * solo para que VEAS el drift del que hablamos -- ese valor se va a ir
 * alejando de la realidad con el tiempo, incluso con el sensor quieto.
 *
 * Librerias requeridas (Arduino IDE > Administrar bibliotecas):
 *   - Adafruit MPU6050
 *   - Adafruit Unified Sensor
 *   - Adafruit BusIO
 *
 * Conexionado (I2C, direccion por defecto 0x68, pin AD0 a GND o sin conectar):
 *   MPU6050/GY-521 VCC -> ESP32 3V3 (la mayoria de modulos GY-521 traen
 *                          regulador a bordo y aceptan 3.3-5V; revisa el tuyo)
 *   MPU6050/GY-521 GND -> ESP32 GND
 *   MPU6050/GY-521 SDA -> ESP32 GPIO21
 *   MPU6050/GY-521 SCL -> ESP32 GPIO22
 *   MPU6050/GY-521 AD0 -> GND (direccion 0x68) o 3V3 (0x69, cambiar mpu.begin() abajo)
 *   MPU6050/GY-521 INT -> no se usa en este sketch
 *
 * Que hace:
 *   1. Verifica que el sensor responde en el bus I2C.
 *   2. Calibra el offset (bias) del giroscopio al arrancar -- MANTEN EL
 *      SENSOR QUIETO durante los primeros ~2 segundos tras cargar el sketch.
 *   3. Imprime por Serial (CSV, 115200 baudios): acelerometro y giro crudos,
 *      roll/pitch del filtro complementario, yaw solo-giro (para ver drift),
 *      y temperatura -- a ~50 Hz.
 */

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

// --- Filtro complementario ---
// Peso del giroscopio (0-1). Mas cerca de 1 = confia mas en el giro
// (responde rapido pero deriva); mas cerca de 0 = confia mas en el
// acelerometro (estable en reposo, pero ruidoso/lento ante movimiento brusco).
#define GYRO_WEIGHT 0.98f

float roll = 0, pitch = 0;
float yawGyroOnly = 0; // SOLO integracion de giro, sin correccion -- para ver el drift
unsigned long lastTime = 0;

// --- Calibracion de offset del giroscopio ---
float gyroBiasX = 0, gyroBiasY = 0, gyroBiasZ = 0;
const int CAL_SAMPLES = 200;

void calibrarGiro() {
  Serial.println("Calibrando giroscopio -- MANTEN EL SENSOR QUIETO...");
  double sumX = 0, sumY = 0, sumZ = 0;
  sensors_event_t a, g, temp;

  for (int i = 0; i < CAL_SAMPLES; i++) {
    mpu.getEvent(&a, &g, &temp);
    sumX += g.gyro.x;
    sumY += g.gyro.y;
    sumZ += g.gyro.z;
    delay(5);
  }

  gyroBiasX = sumX / CAL_SAMPLES;
  gyroBiasY = sumY / CAL_SAMPLES;
  gyroBiasZ = sumZ / CAL_SAMPLES;

  Serial.print("Offset giro (rad/s): x=");
  Serial.print(gyroBiasX, 5);
  Serial.print(" y=");
  Serial.print(gyroBiasY, 5);
  Serial.print(" z=");
  Serial.println(gyroBiasZ, 5);
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("=== Test IMU MPU6050 ===");

  Wire.begin(21, 22);

  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("ERROR: no se detecto el MPU6050. Revisar:");
    Serial.println(" - Alimentacion (VCC y GND)");
    Serial.println(" - SDA/SCL en los pines correctos");
    Serial.println(" - Direccion I2C (AD0 a GND=0x68, a 3V3=0x69 -- cambiar mpu.begin() si aplica)");
    while (1) { delay(1000); }
  }

  Serial.println("MPU6050 detectado correctamente.");

  // Rangos -- ajustar segun la amplitud de movimiento esperada en el ensayo
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(300);

  calibrarGiro();

  // Inicializar roll/pitch con el acelerometro, para no arrancar en (0,0) falso
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  roll  = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  pitch = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
  yawGyroOnly = 0;

  lastTime = millis();

  Serial.println("raw_ax,raw_ay,raw_az,raw_gx,raw_gy,raw_gz,roll,pitch,yaw_solo_giro,temp_C");
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0f;
  lastTime = now;

  // Giro con offset ya restado
  float gx = g.gyro.x - gyroBiasX;
  float gy = g.gyro.y - gyroBiasY;
  float gz = g.gyro.z - gyroBiasZ;

  // Angulo desde el acelerometro (referencia absoluta respecto a gravedad,
  // pero ruidoso y solo sirve para roll/pitch, no para yaw)
  float accelRoll  = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  float accelPitch = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;

  // Velocidad angular en grados/s
  float gyroRollRate  = gx * 180.0 / PI;
  float gyroPitchRate = gy * 180.0 / PI;
  float gyroYawRate   = gz * 180.0 / PI;

  // Filtro complementario: integra el giro (rapido, pero deriva) y lo
  // corrige lentamente con el acelerometro (lento, pero no deriva)
  roll  = GYRO_WEIGHT * (roll  + gyroRollRate  * dt) + (1.0f - GYRO_WEIGHT) * accelRoll;
  pitch = GYRO_WEIGHT * (pitch + gyroPitchRate * dt) + (1.0f - GYRO_WEIGHT) * accelPitch;

  // Yaw SOLO integrando el giro, sin ninguna correccion -- esto es
  // deliberadamente "mal" para que veas el drift acumularse con el tiempo,
  // incluso con el sensor quieto (ver conversacion sobre que es el drift).
  yawGyroOnly += gyroYawRate * dt;

  Serial.print(a.acceleration.x, 3); Serial.print(",");
  Serial.print(a.acceleration.y, 3); Serial.print(",");
  Serial.print(a.acceleration.z, 3); Serial.print(",");
  Serial.print(gx, 3); Serial.print(",");
  Serial.print(gy, 3); Serial.print(",");
  Serial.print(gz, 3); Serial.print(",");
  Serial.print(roll, 2); Serial.print(",");
  Serial.print(pitch, 2); Serial.print(",");
  Serial.print(yawGyroOnly, 2); Serial.print(",");
  Serial.println(temp.temperature, 1);

  delay(20); // ~50 Hz
}
