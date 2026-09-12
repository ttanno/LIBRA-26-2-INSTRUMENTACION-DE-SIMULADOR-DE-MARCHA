/*
 * Test envio de datos por WiFi (UDP) -- ESP32
 *
 * Es el mismo sensor y la misma logica que test_mpu6050.ino (filtro
 * complementario propio para roll/pitch, mas yaw_solo_giro para ver el
 * drift), pero en vez de mandar el CSV por el cable USB (Serial), lo manda
 * por WiFi como paquetes UDP a la IP de tu PC. Es la forma mas simple de
 * "desconectar el cable": no requiere instalar ningun servidor/broker en la
 * PC, solo que el ESP32 y la PC esten en la misma red WiFi.
 *
 * Conexionado del sensor: identico a test_mpu6050.ino (I2C, direccion 0x68)
 *   MPU6050/GY-521 VCC -> ESP32 3V3
 *   MPU6050/GY-521 GND -> ESP32 GND
 *   MPU6050/GY-521 SDA -> ESP32 GPIO21
 *   MPU6050/GY-521 SCL -> ESP32 GPIO22
 *   MPU6050/GY-521 AD0 -> GND (direccion 0x68)
 *
 * ANTES DE CARGAR: cambiar WIFI_SSID, WIFI_PASSWORD y PC_IP mas abajo.
 * PC_IP es la IP local de tu laptop en esa misma red -- el visor_python
 * (visor_wifi_udp.py) la imprime apenas lo corres, para copiarla aca.
 *
 * Librerias requeridas (Arduino IDE > Administrar bibliotecas):
 *   - Adafruit MPU6050, Adafruit Unified Sensor, Adafruit BusIO (igual que
 *     test_mpu6050.ino)
 *   - WiFi.h y WiFiUdp.h ya vienen incluidas en el core de ESP32, no hay
 *     que instalar nada aparte.
 *
 * Que hace:
 *   1. Se conecta a la red WiFi indicada (se ve el progreso por Serial,
 *      util solo para depurar -- el dato real ya no depende del cable).
 *   2. Calibra el giroscopio igual que test_mpu6050.ino (sensor quieto
 *      ~2 s al arrancar).
 *   3. Cada ~20 ms arma la misma linea CSV que test_mpu6050.ino y la manda
 *      por UDP a PC_IP:UDP_PORT. Tambien la imprime por Serial como
 *      respaldo para depurar sin abrir el visor.
 *
 * Limitacion importante de UDP (a diferencia de Serial o de TCP): no hay
 * confirmacion de entrega ni orden garantizado -- si se pierde algun
 * paquete por interferencia de WiFi, simplemente no llega (no se reintenta,
 * no se cae el programa). Para sensado continuo esto es aceptable (es
 * exactamente el mismo riesgo que ya existe con Serial si se satura el
 * buffer), pero si mas adelante se necesita mandar comandos de vuelta al
 * ESP32 con confirmacion, o centralizar varios sensores/ESP32 en un solo
 * canal, el siguiente paso natural es MQTT (ver INSTRUCCIONES.md).
 */

#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// ------------------- CONFIGURAR ANTES DE CARGAR -------------------
const char* WIFI_SSID     = "TU_RED_WIFI";
const char* WIFI_PASSWORD = "TU_PASSWORD";
const char* PC_IP         = "192.168.1.100";  // IP de la PC -- la imprime visor_wifi_udp.py al arrancar
const uint16_t UDP_PORT   = 4210;
// --------------------------------------------------------------------

Adafruit_MPU6050 mpu;
WiFiUDP udp;

#define GYRO_WEIGHT 0.98f

float roll = 0, pitch = 0;
float yawGyroOnly = 0;
unsigned long lastTime = 0;

float gyroBiasX = 0, gyroBiasY = 0, gyroBiasZ = 0;
const int CAL_SAMPLES = 200;

void conectarWifi() {
  Serial.print("Conectando a WiFi \"");
  Serial.print(WIFI_SSID);
  Serial.print("\"");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi conectado. IP del ESP32: ");
  Serial.println(WiFi.localIP());
  Serial.print("Mandando datos a ");
  Serial.print(PC_IP);
  Serial.print(":");
  Serial.println(UDP_PORT);
}

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
  Serial.println("Calibracion lista.");
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("=== Test WiFi UDP (MPU6050) ===");

  conectarWifi();

  Wire.begin(21, 22);

  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("ERROR: no se detecto el MPU6050. Revisar alimentacion y SDA/SCL.");
    while (1) { delay(1000); }
  }
  Serial.println("MPU6050 detectado correctamente.");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(300);
  calibrarGiro();

  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  roll  = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  pitch = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
  yawGyroOnly = 0;

  lastTime = millis();

  udp.begin(UDP_PORT);  // no hace falta para SOLO enviar, pero deja el socket listo por si mas adelante se quiere recibir comandos de vuelta

  Serial.println("raw_ax,raw_ay,raw_az,raw_gx,raw_gy,raw_gz,roll,pitch,yaw_solo_giro,temp_C");
}

void loop() {
  // Reconexion simple si se cae el WiFi -- bloqueante, aceptable para un sketch de prueba.
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, reintentando...");
    conectarWifi();
  }

  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0f;
  lastTime = now;

  float gx = g.gyro.x - gyroBiasX;
  float gy = g.gyro.y - gyroBiasY;
  float gz = g.gyro.z - gyroBiasZ;

  float accelRoll  = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  float accelPitch = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;

  float gyroRollRate  = gx * 180.0 / PI;
  float gyroPitchRate = gy * 180.0 / PI;
  float gyroYawRate   = gz * 180.0 / PI;

  roll  = GYRO_WEIGHT * (roll  + gyroRollRate  * dt) + (1.0f - GYRO_WEIGHT) * accelRoll;
  pitch = GYRO_WEIGHT * (pitch + gyroPitchRate * dt) + (1.0f - GYRO_WEIGHT) * accelPitch;
  yawGyroOnly += gyroYawRate * dt;

  char buf[160];
  int len = snprintf(buf, sizeof(buf),
                      "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.1f",
                      a.acceleration.x, a.acceleration.y, a.acceleration.z,
                      gx, gy, gz, roll, pitch, yawGyroOnly, temp.temperature);

  // Mismo dato, dos salidas: UDP (el que importa) y Serial (solo para depurar).
  udp.beginPacket(PC_IP, UDP_PORT);
  udp.write((const uint8_t*)buf, len);
  udp.endPacket();

  Serial.println(buf);

  delay(20); // ~50 Hz
}
