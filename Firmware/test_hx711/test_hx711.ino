/*
 * Driver de prueba para el modulo HX711 (ADC de 24 bits + amplificador,
 * dedicado a celdas de carga/puente de Wheatstone)
 * Plataforma: ESP32 (2 pines digitales, protocolo propio del HX711, sin SPI)
 *
 * POR QUE PROBAR EL HX711 ADEMAS DEL ADS1256: el ADS1256 sigue siendo el ADC
 * elegido para LIBRA a largo plazo (ver comparativa de sensores, se prefirio
 * porque tiene 8 canales para compartir despues con la plataforma AMTI -- ver
 * Firmware/test_ads1256/INSTRUCCIONES.md, Secc. "Por que ADS1256 y no
 * HX711"). Este sketch NO reemplaza esa decision: es una via rapida y en
 * paralelo para verificar si la celda de carga y su cableado estan bien,
 * aislado del ADS1256 -- util mientras se sigue diagnosticando el ruido tipo
 * diente de sierra que aparece con el ADS1256 (si con el HX711 la lectura
 * sale limpia, el problema esta mas del lado del ADS1256/su cableado que de
 * la celda en si).
 *
 * A diferencia del ADS1256 (sin libreria en el Library Manager), el HX711 SI
 * tiene una libreria estandar y muy usada: "HX711" de Bogdan Necula
 * (https://github.com/bogde/HX711). Instalarla desde el Library Manager del
 * Arduino IDE (Herramientas > Administrar Bibliotecas > buscar "HX711" >
 * instalar la de Bogdan Necula) antes de compilar este sketch.
 *
 * CONEXIONADO (modulo generico HX711, placa chica con capacitores, la que
 * casi siempre se vende junto con celdas de carga tipo "barra"/"balanza"):
 *
 *   Modulo HX711      ESP32          Notas
 *   ------------      -----          -----
 *   VCC / VDD    ->   3.3V           ver aviso de niveles logicos abajo
 *   GND          ->   GND            comun con la celda y el resto del circuito
 *   DT (DOUT/DAT)->   GPIO32         salida de datos (entrada para el ESP32)
 *   SCK (CLK)    ->   GPIO33         reloj (salida del ESP32 hacia el modulo)
 *   E+ (rojo)    ->   (interno, ya conectado a VCC del modulo)
 *   E- (negro)   ->   (interno, ya conectado a GND del modulo)
 *   A+ (verde)   ->   señal + de la celda (canal A, ganancia 128 por defecto)
 *   A- (blanco)  ->   señal - de la celda
 *   B+ / B-      ->   libres (canal B, ganancia fija en 32 -- para una
 *                      segunda celda si hiciera falta, no se usa aca)
 *
 * *** NIVELES LOGICOS -- por que ESTE modulo NO necesita level shifter ***
 * El HX711 acepta alimentacion (VCC/VDD) entre 2.6V y 5.5V (fuente: hoja de
 * datos del modulo GroundStudio/generico, y articulo tecnico de
 * microcontrollerslab.com -- ver fuentes en INSTRUCCIONES.md). Alimentandolo
 * con el 3.3V del propio ESP32 (en vez de una fuente de 5V separada, como
 * SI hace falta con el modulo ADS1256 generico), sus pines digitales (DT de
 * salida, SCK de entrada) quedan directamente en logica de 3.3V --
 * compatibles con el ESP32 sin ningun conversor de nivel logico en el medio.
 *
 * Contrapartida: la excitacion de la celda (E+/E-) tambien queda a 3.3V en
 * vez de 5V (el modulo ata E+ al mismo VCC), asi que la señal de salida de
 * la celda (mV/V) sale un poco mas chica que alimentando a 5V. Para una
 * prueba/comparacion rapida no deberia ser problema. Si mas adelante hace
 * falta el maximo rango con 5V, ahi SI hay que volver a cuidar los niveles
 * logicos: DT saldria en 5V (el ESP32 no lo tolera) y SCK necesitaria
 * ~0.7*5V=3.5V para registrar HIGH de forma confiable (el 3.3V del ESP32
 * queda justo por debajo) -- por eso se recomienda arrancar con 3.3V.
 *
 * Tasa de muestreo: fija por hardware segun el pin RATE del modulo -- la
 * gran mayoria de los breakouts genericos lo dejan fijo en 10 SPS (algunos
 * traen un puente/jumper para 80 SPS). No se controla desde este sketch.
 *
 * Comandos por Serial (escribe y Enter en el Monitor Serie) -- mismo
 * esquema que test_ads1256.ino:
 *   t        -> Tara: promedia la lectura actual (celda SIN carga) y la
 *               guarda como el cero (en cuentas crudas). Se persiste en
 *               flash (NVS).
 *   k<masa>  -> Calibra: con una masa patron conocida YA puesta sobre la
 *               celda, escribe por ejemplo "k5.0" (5.0 kg) y Enter.
 *               Promedia la lectura actual y calcula el factor N/cuenta
 *               contra la tara. Se persiste en flash.
 *   r        -> Resetea (borra) la tara y la calibracion guardadas.
 *
 * Salida CSV por Serial (115200 baudios):
 *   raw_code,force_N,tared,calibrated
 *     raw_code   : cuenta cruda de 24 bits con signo que entrega el HX711
 *                  (SIN restar tara). A diferencia del ADS1256, el HX711 no
 *                  tiene una referencia de voltaje bien definida y publica,
 *                  asi que no se convierte a voltios -- se calibra directo
 *                  de cuentas crudas a Newtons.
 *     force_N    : (raw_code - tara) * factor_escala, en Newtons. Si
 *                  todavia no se calibro (comando k), se imprime 0.0 y la
 *                  columna "calibrated" queda en 0.
 *     tared      : 1 si ya se hizo "t" (o se cargo una tara guardada), 0 si no.
 *     calibrated : 1 si ya se hizo "k<masa>" (o se cargo una calibracion
 *                  guardada), 0 si no.
 */

#include <HX711.h>
#include <Preferences.h>

// ---------------------------------------------------------------------
// Pines (ajustar si tu cableado es distinto al de la tabla de arriba)
// ---------------------------------------------------------------------
#define PIN_HX711_DT   32  // DOUT/DAT del modulo -> entrada del ESP32
#define PIN_HX711_SCK  33  // SCK/CLK del modulo  -> salida del ESP32

// ---------------------------------------------------------------------
// Configuracion de medicion
// ---------------------------------------------------------------------
#define HX711_GANANCIA  128  // Canal A, ganancia 128 (default de fabrica). 64 = canal A ganancia 64.
const unsigned long HX711_TIMEOUT_MS = 1000;  // a 10 SPS una lectura tarda ~100ms; timeout generoso
const int N_MUESTRAS_TARA = 20;               // muestras promediadas al hacer "t" o "k<masa>"
const float G_GRAVEDAD = 9.80665f;            // m/s^2, para convertir masa patron (kg) a fuerza (N)

HX711 balanza;

Preferences prefs;
const char* NVS_NAMESPACE = "libra_hx711";

long  taraOffsetRaw = 0;
bool  taraSet = false;
float escalaNporCount = 0.0f;  // Newtons por cuenta cruda, calculado en la calibracion
bool  calibrado = false;

// =======================================================================
// Inicializacion
// =======================================================================

void hx711_begin() {
  balanza.begin(PIN_HX711_DT, PIN_HX711_SCK, HX711_GANANCIA);
  if (!balanza.wait_ready_timeout(2000)) {
    Serial.println("ERROR: el HX711 no respondio. Revisar:");
    Serial.println(" - Alimentacion (VCC/GND del modulo)");
    Serial.println(" - Cableado DT/SCK");
    Serial.println(" - Que la celda este conectada a E+/E-/A+/A-");
  } else {
    Serial.println("HX711 inicializado correctamente.");
  }
}

// =======================================================================
// Tara / calibracion (persistidas en flash, igual que test_ads1256.ino /
// homing_absoluto.ino)
// =======================================================================

void cargarCalibracionDesdeFlash() {
  prefs.begin(NVS_NAMESPACE, true);  // solo lectura
  taraSet = prefs.getBool("tara_set", false);
  taraOffsetRaw = prefs.getLong("tara_raw", 0);
  calibrado = prefs.getBool("cal_set", false);
  escalaNporCount = prefs.getFloat("escala", 0.0f);
  prefs.end();
}

void guardarTaraEnFlash(long raw) {
  prefs.begin(NVS_NAMESPACE, false);
  prefs.putLong("tara_raw", raw);
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

// Promedia N_MUESTRAS_TARA lecturas crudas, bloqueando (usar solo desde los
// comandos por Serial, no en el loop principal de streaming). Devuelve NAN
// si no se pudo leer ninguna muestra (HX711 no responde).
double leerPromedioRaw(int n) {
  double suma = 0;
  int ok = 0;
  for (int i = 0; i < n; i++) {
    if (balanza.wait_ready_timeout(HX711_TIMEOUT_MS)) {
      suma += balanza.read();
      ok++;
    }
  }
  if (ok == 0) return NAN;
  return suma / ok;
}

void procesarComandoSerial(String linea) {
  linea.trim();
  if (linea.length() == 0) return;

  char c = linea.charAt(0);

  if (c == 't' || c == 'T') {
    Serial.println("Tarando... manten la celda SIN carga.");
    double raw = leerPromedioRaw(N_MUESTRAS_TARA);
    if (isnan(raw)) {
      Serial.println("ERROR: no se pudo leer el HX711 (timeout).");
      return;
    }
    taraOffsetRaw = (long)round(raw);
    taraSet = true;
    guardarTaraEnFlash(taraOffsetRaw);
    Serial.print("Tara guardada: ");
    Serial.print(taraOffsetRaw);
    Serial.println(" cuentas");

  } else if (c == 'k' || c == 'K') {
    float masaKg = linea.substring(1).toFloat();
    if (masaKg <= 0.0f) {
      Serial.println("Uso: k<masa_kg>, ej. k5.0  (masa patron > 0)");
      return;
    }
    if (!taraSet) {
      Serial.println("ADVERTENCIA: todavia no hiciste tara ('t'). Calibrando igual contra 0 cuentas.");
    }
    Serial.print("Calibrando con masa patron de ");
    Serial.print(masaKg, 3);
    Serial.println(" kg puesta sobre la celda...");
    double raw = leerPromedioRaw(N_MUESTRAS_TARA);
    if (isnan(raw)) {
      Serial.println("ERROR: no se pudo leer el HX711 (timeout).");
      return;
    }
    double deltaRaw = raw - (double)taraOffsetRaw;
    if (fabs(deltaRaw) < 10.0) {
      Serial.println("ERROR: la lectura casi no cambio respecto a la tara -- revisa que la masa este puesta y el cableado de la celda (A+/A-).");
      return;
    }
    float fuerzaN = masaKg * G_GRAVEDAD;
    escalaNporCount = (float)(fuerzaN / deltaRaw);
    calibrado = true;
    guardarEscalaEnFlash(escalaNporCount);
    Serial.print("Calibracion guardada: ");
    Serial.print(escalaNporCount, 8);
    Serial.println(" N/cuenta");

  } else if (c == 'r' || c == 'R') {
    borrarCalibracionEnFlash();
    taraSet = false;
    taraOffsetRaw = 0;
    calibrado = false;
    escalaNporCount = 0.0f;
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

  Serial.println("=== Driver de prueba HX711 (celda de carga, LIBRA) ===");

  hx711_begin();
  cargarCalibracionDesdeFlash();

  if (taraSet) {
    Serial.print("Tara cargada de flash: ");
    Serial.print(taraOffsetRaw);
    Serial.println(" cuentas");
  }
  if (calibrado) {
    Serial.print("Calibracion cargada de flash: ");
    Serial.print(escalaNporCount, 8);
    Serial.println(" N/cuenta");
  }
  if (!taraSet || !calibrado) {
    Serial.println("Sin tara y/o calibracion completas todavia -- usa 't' y luego 'k<masa_kg>'.");
  }

  Serial.println("raw_code,force_N,tared,calibrated");
}

void loop() {
  if (Serial.available() > 0) {
    String linea = Serial.readStringUntil('\n');
    procesarComandoSerial(linea);
  }

  if (balanza.wait_ready_timeout(HX711_TIMEOUT_MS)) {
    long raw = balanza.read();
    float forceN = 0.0f;
    if (calibrado) {
      forceN = (raw - taraOffsetRaw) * escalaNporCount;
    }

    Serial.print(raw);
    Serial.print(",");
    Serial.print(forceN, 4);
    Serial.print(",");
    Serial.print(taraSet ? 1 : 0);
    Serial.print(",");
    Serial.println(calibrado ? 1 : 0);
  } else {
    Serial.println("ERROR: timeout esperando datos del HX711 (revisar cableado/alimentacion).");
  }
}
