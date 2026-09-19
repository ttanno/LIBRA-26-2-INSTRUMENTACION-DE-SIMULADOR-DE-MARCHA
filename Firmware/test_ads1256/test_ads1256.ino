/*
 * Driver de prueba para el ADC ADS1256 (24 bits, 8 canales, SPI)
 * Plataforma: ESP32 (SPI)
 * Uso en LIBRA: lectura de la celda de carga del pylon (interfaz
 * pylon-plataforma). Este es el ADC ya elegido en la comparativa de
 * sensores de fuerza (ver Estado-del-arte/SENSORES DE FUERZA/PYLON/
 * Comparativa-Sensores-Fuerza-Axial-Pylon.md): se prefirio frente al
 * HX711 porque el ADS1256 tiene 8 canales y se planea COMPARTIRLO con
 * los 6 canales analogicos de la plataforma AMTI (Fx,Fy,Fz,Mx,My,Mz),
 * mientras que el HX711 es un ADC dedicado de 1-2 canales, sin margen
 * para esa expansion (ver Reportes-Semanales/S4/Pendientes.md, seccion
 * "plataforma AMTI": "Disenar la interfaz de lectura de los 6 canales
 * de la AMTI con el ADS1256" sigue pendiente -- este sketch NO lo
 * resuelve todavia, solo deja el MUX listo para extenderse).
 *
 * CONEXION DE LA CELDA -- SIN amplificador externo (INA818): la celda de
 * carga se conecta DIRECTO al ADS1256, usando su PGA interno a x64 en vez
 * de un amplificador de instrumentacion externo. Se decidio asi porque a
 * x64 el rango de entrada (Vref/64 ~ 39mV con Vref=2.5V) ya encaja bien con
 * la señal tipica de un puente de Wheatstone (unos pocos mV/V), y el ruido
 * propio del ADS1256 en esa configuracion (~0.17uV RMS, ~17 bits libres de
 * ruido segun el datasheet) sobra para una celda de carga. Si mas adelante
 * se ve mucho ruido o el cable a la celda es largo, ahi se puede sumar un
 * INA818 entre la celda y el ADS1256 (ver comparativa de sensores) -- pero
 * no hace falta para arrancar a probar.
 *
 * Por eso este sketch lee un canal DIFERENCIAL (AIN0 = señal+ de la celda,
 * AIN1 = señal- de la celda), no single-ended contra AINCOM como en la
 * primera version de este sketch.
 *
 * IMPORTANTE -- estado de la celda de carga: al momento de escribir esto
 * la celda de carga final todavia NO esta elegida (ver Pendientes S4,
 * "Seleccion de sensor de fuerza del pylon"). Este sketch por lo tanto
 * NO puede traer un factor de escala de fabrica: implementa tara +
 * calibracion con una masa patron conocida (rutina tipo "poner un peso
 * conocido y decirle al firmware cuanto pesa"), igual que harias con
 * cualquier celda + HX711. Cuando se elija la celda final, esta misma
 * rutina de calibracion sigue sirviendo.
 *
 * Conexionado real (modulo generico tipo "Teyleten Robot"/HiLetgo/JESSINIE,
 * la placa roja de 24 bits/8 canales, + conversor de nivel logico
 * bidireccional 4 canales tipo Naylamp/SparkFun BSS138 en el medio, + celda
 * de carga DIRECTO sin INA818 -- ver conversacion de calibracion del
 * hardware real de este proyecto):
 *
 *   ESP32 GPIO23 -- LV1/HV1 (shifter) -- DIN  (modulo ADS1256)
 *   ESP32 GPIO18 -- LV2/HV2 (shifter) -- SCLK (modulo ADS1256)
 *   ESP32 GPIO19 -- LV3/HV3 (shifter) -- DOUT (modulo ADS1256)
 *   ESP32 GPIO4  -- LV4/HV4 (shifter) -- DRDY (modulo ADS1256)
 *   ESP32 3.3V   -- LV      (shifter)
 *   Fuente 5V    -- HV      (shifter) -- 5V (modulo ADS1256)
 *   GND comun a ESP32 + shifter + modulo ADS1256
 *
 *   ADS1256 CS   -> GND directo (NO pasa por el shifter ni por el ESP32:
 *                   es el unico dispositivo SPI del bus, asi que se deja
 *                   permanentemente seleccionado). Por eso este sketch YA
 *                   NO controla un pin de CS por software.
 *   ADS1256 PDWN -> 5V del modulo (siempre encendido)
 *   ADS1256 RESET -> no expuesto en este modulo (ver ADS1256_USE_RESET_PIN)
 *
 *   Celda de carga (4 hilos, DIRECTO al ADS1256, sin INA818):
 *     Rojo  (EXC+) -> 5V del modulo ADS1256
 *     Negro (EXC-) -> GND
 *     Verde (SIG+) -> AIN0
 *     Blanco(SIG-) -> AIN1
 *
 * *** OJO -- NIVELES LOGICOS ***: el modulo ADS1256 generico se alimenta a
 * 5V fijos (no se encontro version con jumper a 3.3V) -- por eso el
 * conversor de nivel logico de 4 canales de arriba, con las 4 señales que
 * cambian de estado (DIN/SCLK/DOUT/DRDY) pasando por el. CS no lo necesita
 * porque quedo fijo a GND en vez de conmutado por software.
 *
 * Este sketch asume Vref = 2.5V (la referencia a bordo de estos modulos
 * genericos, tipico ADR03) y que el modulo ya trae el cristal de CLKIN
 * montado de fabrica.
 *
 * Libreria requerida: NINGUNA externa -- el protocolo del ADS1256 (SPI +
 * registros) esta implementado directo en este sketch porque no hay una
 * libreria estandar en el Library Manager de Arduino para este chip
 * (a diferencia del BNO055/MPU6050). Preferences.h ya viene en el core ESP32.
 *
 * Comandos por Serial (escribe y Enter en el Monitor Serie):
 *   t        -> Tara: promedia la lectura actual (celda SIN carga) y la
 *               guarda como el cero. Se persiste en flash (NVS).
 *   k<masa>  -> Calibra: con una masa patron conocida YA puesta sobre la
 *               celda, escribe por ejemplo "k5.0" (5.0 kg) y Enter.
 *               Promedia la lectura actual y calcula el factor N/V contra
 *               la tara. Se persiste en flash.
 *               Ejemplo de secuencia completa: celda sin carga -> "t" ->
 *               poner masa patron -> "k2.0" -> listo, factor calibrado.
 *   r        -> Resetea (borra) la tara y la calibracion guardadas.
 *
 * Salida CSV por Serial (115200 baudios), a la tasa de datos configurada
 * (ADS1256_DRATE_CODE, 100 SPS por defecto):
 *   raw_code,voltage_V,force_N,tared,calibrated
 *     raw_code   : codigo crudo de 24 bits con signo que entrega el ADC.
 *     voltage_V  : raw_code convertido a voltios en la entrada del ADS1256
 *                  (con el Vref y la ganancia configurados), SIN restar tara.
 *     force_N    : (voltage_V - tara) * factor_escala, en Newtons. Si
 *                  todavia no se calibro (comando k), se imprime 0.0 y la
 *                  columna "calibrated" queda en 0 -- NO tomar ese valor
 *                  como fuerza real todavia.
 *     tared      : 1 si ya se hizo "t" (o se cargo una tara guardada), 0 si no.
 *     calibrated : 1 si ya se hizo "k<masa>" (o se cargo una calibracion
 *                  guardada), 0 si no.
 */

#include <SPI.h>
#include <Preferences.h>

// ---------------------------------------------------------------------
// Pines (ajustar si tu cableado es distinto al de la tabla de arriba)
// ---------------------------------------------------------------------
#define PIN_SCLK  18
#define PIN_MISO  19  // DOUT del ADS1256
#define PIN_MOSI  23  // DIN del ADS1256
#define PIN_DRDY   4
// No hay PIN_CS: el CS del modulo ADS1256 esta cableado directo a GND
// (unico dispositivo SPI del bus), no se controla por software.

#define ADS1256_USE_RESET_PIN 0   // 0 = modulos genericos sin pin RESET expuesto (Teyleten/HiLetgo/etc, ver nota arriba). Poner en 1 solo si tu breakout SI trae RESET.
#define PIN_RESET  2

// ---------------------------------------------------------------------
// Configuracion electrica/de medicion -- revisar contra tu hardware real
// ---------------------------------------------------------------------
#define ADS1256_VREF        2.5f   // Voltios. Cambiar si usan una referencia externa distinta.
#define ADS1256_SPI_HZ       500000UL  // 500 kHz -- conservador para cableado de prototipo/protoboard

// Ganancia del PGA interno del ADS1256. Sin INA818 externo, toda la
// ganancia la pone el PGA -- x64 deja el rango de entrada (Vref/64) bien
// ajustado a la señal tipica de un puente de Wheatstone (pocos mV/V).
//   codigo: 000=x1 001=x2 010=x4 011=x8 100=x16 101=x32 110=x64
#define ADS1256_PGA_CODE     0x06  // x64
#define ADS1256_PGA_GANANCIA 64.0f  // debe coincidir con ADS1256_PGA_CODE de arriba

// Tasa de datos (DRATE). 100 SPS es un buen balance ruido/velocidad para
// una celda de carga estatica/cuasi-estatica (no hace falta 30 kSPS aca).
// Tabla completa de codigos en la hoja de datos del ADS1256, Table 13:
//   0xF0=30000SPS 0xE0=15000 0xD0=7500 0xC0=3750 0xB0=2000 0xA1=1000
//   0x92=500 0x82=100 0x72=60 0x63=50 0x53=30 0x43=25 0x33=15 0x23=10
//   0x13=5   0x03=2.5
#define ADS1256_DRATE_CODE   0x82  // 100 SPS

const unsigned long DRDY_TIMEOUT_MS = 500;  // timeout de una lectura individual en loop()
const int N_MUESTRAS_TARA = 20;             // muestras promediadas al hacer "t" o "k<masa>"
const float G_GRAVEDAD = 9.80665f;          // m/s^2, para convertir masa patron (kg) a fuerza (N)

// ---------------------------------------------------------------------
// Registros y comandos del ADS1256 (hoja de datos, Tables 15 y 23)
// ---------------------------------------------------------------------
#define REG_STATUS 0x00
#define REG_MUX    0x01
#define REG_ADCON  0x02
#define REG_DRATE  0x03

#define CMD_SDATAC  0x0F
#define CMD_RDATA   0x01
#define CMD_WREG    0x50
#define CMD_RREG    0x10
#define CMD_SELFCAL 0xF0

// MUX: AIN0(+) vs AIN1(-) -- par DIFERENCIAL para la señal cruda de la
// celda de carga (SIG+ a AIN0, SIG- a AIN1), sin pasar por un amplificador
// externo. Los otros 6 canales del ADS1256 (AIN2-AIN7) quedan libres para
// cuando se implemente la lectura de los 6 canales de la AMTI
// (Fx,Fy,Fz,Mx,My,Mz) -- ver Pendientes S4, todavia sin resolver.
#define ADS1256_MUX_CELDA_CARGA 0x01  // AINP=AIN0(0000), AINN=AIN1(0001)

Preferences prefs;
const char* NVS_NAMESPACE = "libra_ads1256";

float taraVoltage = 0.0f;
bool taraSet = false;
float escalaNporV = 0.0f;  // Newtons por Voltio, calculado en la calibracion
bool calibrado = false;

// =======================================================================
// Capa de protocolo ADS1256 (SPI + registros)
// =======================================================================

// CS del ADS1256 cableado directo a GND (ver nota de conexionado arriba) --
// no hay pin que controlar por software, asi que estas funciones ya no
// tocan ningun GPIO. Se dejan como funciones vacias (en vez de borrar todas
// las llamadas) por si en el futuro se agrega un segundo dispositivo SPI al
// bus y hay que volver a controlar CS por software.
inline void csLow()  {}
inline void csHigh() {}

void ads1256_sendCmd(uint8_t cmd) {
  SPI.transfer(cmd);
  delayMicroseconds(5);
}

void ads1256_writeReg(uint8_t reg, uint8_t value) {
  SPI.transfer(CMD_WREG | reg);
  SPI.transfer(0x00);  // n-1 = 0 -> escribe un solo registro
  SPI.transfer(value);
  delayMicroseconds(5);
}

// Espera a que DRDY baje (dato listo). Devuelve false si se agoto el timeout
// (probable problema de cableado/alimentacion -- revisar CS/DRDY/CLKIN).
bool ads1256_waitDRDY(unsigned long timeoutMs) {
  unsigned long inicio = millis();
  while (digitalRead(PIN_DRDY) == HIGH) {
    if (millis() - inicio > timeoutMs) return false;
  }
  return true;
}

// Lee una conversion de 24 bits (con signo) ya lista (llamar SOLO despues
// de confirmar DRDY=LOW, con ads1256_waitDRDY).
int32_t ads1256_readData() {
  SPI.transfer(CMD_RDATA);
  delayMicroseconds(10);  // t6 de la hoja de datos: espera minima antes de leer
  uint32_t b2 = SPI.transfer(0x00);  // MSB
  uint32_t b1 = SPI.transfer(0x00);
  uint32_t b0 = SPI.transfer(0x00);  // LSB

  uint32_t raw = (b2 << 16) | (b1 << 8) | b0;
  if (raw & 0x00800000UL) raw |= 0xFF000000UL;  // extension de signo 24->32 bits
  return (int32_t)raw;
}

float ads1256_codeToVoltage(int32_t code) {
  // Formula de la hoja de datos: Codigo = 2^23 * Vin / (Vref/Ganancia)
  return ((float)code / 8388608.0f) * (ADS1256_VREF / ADS1256_PGA_GANANCIA);
}

void ads1256_begin() {
  pinMode(PIN_DRDY, INPUT);

#if ADS1256_USE_RESET_PIN
  pinMode(PIN_RESET, OUTPUT);
  digitalWrite(PIN_RESET, LOW);
  delay(2);
  digitalWrite(PIN_RESET, HIGH);
  delay(2);
#endif

  // Sin pin de CS que declarar: esta fijo a GND en el hardware (ver nota
  // de conexionado arriba).
  SPI.begin(PIN_SCLK, PIN_MISO, PIN_MOSI);
  SPI.beginTransaction(SPISettings(ADS1256_SPI_HZ, MSBFIRST, SPI_MODE1));

  ads1256_sendCmd(CMD_SDATAC);  // asegura que no quede en modo lectura continua
  delay(1);

  ads1256_writeReg(REG_STATUS, 0x06);  // ACAL=1, BUFEN=1, ORDER=0 (MSB primero)
  ads1256_writeReg(REG_MUX, ADS1256_MUX_CELDA_CARGA);
  ads1256_writeReg(REG_ADCON, 0x20 | ADS1256_PGA_CODE);  // CLK=CLKIN, SDCS=off
  ads1256_writeReg(REG_DRATE, ADS1256_DRATE_CODE);

  ads1256_sendCmd(CMD_SELFCAL);
  if (!ads1256_waitDRDY(2000)) {
    Serial.println("ERROR: el ADS1256 no respondio tras SELFCAL. Revisar:");
    Serial.println(" - Alimentacion (AVDD/DVDD/AGND/DGND)");
    Serial.println(" - Cableado SPI (DIN/DOUT/SCLK/CS) y DRDY");
    Serial.println(" - CLKIN (la mayoria de breakouts necesitan su cristal montado)");
  } else {
    Serial.println("ADS1256 inicializado y autocalibrado correctamente.");
  }
}

// =======================================================================
// Tara / calibracion (persistidas en flash, igual que homing_absoluto.ino)
// =======================================================================

void cargarCalibracionDesdeFlash() {
  prefs.begin(NVS_NAMESPACE, true);  // solo lectura
  taraSet = prefs.getBool("tara_set", false);
  taraVoltage = prefs.getFloat("tara_v", 0.0f);
  calibrado = prefs.getBool("cal_set", false);
  escalaNporV = prefs.getFloat("escala", 0.0f);
  prefs.end();
}

void guardarTaraEnFlash(float v) {
  prefs.begin(NVS_NAMESPACE, false);
  prefs.putFloat("tara_v", v);
  prefs.putBool("tara_set", true);
  prefs.end();
}

void guardarEscalaEnFlash(float s) {
  prefs.begin(NVS_NAMESPACE, false);
  prefs.putFloat("escala", s);
  prefs.putBool("cal_set", true);
  prefs.end();
}

void borrarCalibracionEnFlash() {
  prefs.begin(NVS_NAMESPACE, false);
  prefs.clear();
  prefs.end();
}

// Promedia N_MUESTRAS_TARA lecturas de voltaje, bloqueando (usar solo desde
// los comandos por Serial, no en el loop principal de streaming).
float leerVoltajePromedio(int n) {
  double suma = 0;
  int ok = 0;
  for (int i = 0; i < n; i++) {
    if (ads1256_waitDRDY(DRDY_TIMEOUT_MS)) {
      suma += ads1256_codeToVoltage(ads1256_readData());
      ok++;
    }
  }
  if (ok == 0) return NAN;
  return (float)(suma / ok);
}

void procesarComandoSerial(String linea) {
  linea.trim();
  if (linea.length() == 0) return;

  char c = linea.charAt(0);

  if (c == 't' || c == 'T') {
    Serial.println("Tarando... manten la celda SIN carga.");
    float v = leerVoltajePromedio(N_MUESTRAS_TARA);
    if (isnan(v)) {
      Serial.println("ERROR: no se pudo leer el ADS1256 (timeout de DRDY).");
      return;
    }
    taraVoltage = v;
    taraSet = true;
    guardarTaraEnFlash(v);
    Serial.print("Tara guardada: ");
    Serial.print(v, 6);
    Serial.println(" V");

  } else if (c == 'k' || c == 'K') {
    float masaKg = linea.substring(1).toFloat();
    if (masaKg <= 0.0f) {
      Serial.println("Uso: k<masa_kg>, ej. k5.0  (masa patron > 0)");
      return;
    }
    if (!taraSet) {
      Serial.println("ADVERTENCIA: todavia no hiciste tara ('t'). Calibrando igual contra 0 V.");
    }
    Serial.print("Calibrando con masa patron de ");
    Serial.print(masaKg, 3);
    Serial.println(" kg puesta sobre la celda...");
    float v = leerVoltajePromedio(N_MUESTRAS_TARA);
    if (isnan(v)) {
      Serial.println("ERROR: no se pudo leer el ADS1256 (timeout de DRDY).");
      return;
    }
    float deltaV = v - taraVoltage;
    if (fabs(deltaV) < 1e-6f) {
      Serial.println("ERROR: la lectura no cambio respecto a la tara -- revisa que la masa este puesta y el cableado del puente/amplificador.");
      return;
    }
    float fuerzaN = masaKg * G_GRAVEDAD;
    escalaNporV = fuerzaN / deltaV;
    calibrado = true;
    guardarEscalaEnFlash(escalaNporV);
    Serial.print("Calibracion guardada: ");
    Serial.print(escalaNporV, 4);
    Serial.println(" N/V");

  } else if (c == 'r' || c == 'R') {
    borrarCalibracionEnFlash();
    taraSet = false;
    taraVoltage = 0.0f;
    calibrado = false;
    escalaNporV = 0.0f;
    Serial.println("Tara y calibracion borradas.");

  } else {
    Serial.println("Comandos: t (tara) | k<masa_kg> (calibrar) | r (resetear calibracion)");
  }
}

// =======================================================================
// setup() / loop()
// =======================================================================

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("=== Driver de prueba ADS1256 (celda de carga, LIBRA) ===");

  ads1256_begin();
  cargarCalibracionDesdeFlash();

  if (taraSet) {
    Serial.print("Tara cargada de flash: ");
    Serial.print(taraVoltage, 6);
    Serial.println(" V");
  }
  if (calibrado) {
    Serial.print("Calibracion cargada de flash: ");
    Serial.print(escalaNporV, 4);
    Serial.println(" N/V");
  }
  if (!taraSet || !calibrado) {
    Serial.println("Sin tara y/o calibracion completas todavia -- usa 't' y luego 'k<masa_kg>'.");
  }

  Serial.println("raw_code,voltage_V,force_N,tared,calibrated");
}

void loop() {
  if (Serial.available() > 0) {
    String linea = Serial.readStringUntil('\n');
    procesarComandoSerial(linea);
  }

  if (ads1256_waitDRDY(DRDY_TIMEOUT_MS)) {
    int32_t code = ads1256_readData();
    float voltage = ads1256_codeToVoltage(code);
    float forceN = 0.0f;
    if (calibrado) {
      forceN = (voltage - taraVoltage) * escalaNporV;
    }

    Serial.print(code);
    Serial.print(",");
    Serial.print(voltage, 6);
    Serial.print(",");
    Serial.print(forceN, 4);
    Serial.print(",");
    Serial.print(taraSet ? 1 : 0);
    Serial.print(",");
    Serial.println(calibrado ? 1 : 0);
  } else {
    Serial.println("ERROR: timeout esperando DRDY del ADS1256 (revisar cableado/alimentacion).");
  }
}
