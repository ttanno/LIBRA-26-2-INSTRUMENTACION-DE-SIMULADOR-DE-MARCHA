/*
 * Homing del eje del motor paso a paso (husillo) con iman + sensor Hall
 * Plataforma: ESP32 + driver de motor paso a paso (A4988/DRV8825/TMC2209,
 *             cualquiera con interfaz STEP/DIR estandar)
 *
 * IDEA: pegar un iman pequeño en un disco/colllarin que se monta en el eje
 * del motor, y fijar un sensor Hall en el chasis del motor -- una vez por
 * vuelta, el iman pasa frente al sensor y dispara una señal digital. Ese
 * es un punto FISICO, repetible y exacto del eje -- no depende de contar
 * pasos (que se puede perder si el motor patina/pierde pasos) ni de
 * gravedad/nivelacion (a diferencia del homing con acelerometro que ya
 * probamos para el pivote).
 *
 * PIEZA FISICA A IMPRIMIR (ver notas de diseño en INSTRUCCIONES.md):
 *   - Un collarin/disco que se ajusta al eje del motor (con tornillo
 *     prisionero M3 para fijarlo, permite reajustar el angulo si hace falta).
 *   - Una cavidad para un iman de neodimio pequeño (ej. 4mm dia x 2mm,
 *     comun y barato) cerca del borde del disco.
 *   - Un sensor Hall digital (ej. A3144 o similar) atornillado al chasis
 *     del motor, a unos pocos mm del disco, alineado para que el iman
 *     pase justo frente a el en cada vuelta.
 *
 * IMPORTANTE -- que SI resuelve y que NO:
 *   - Esto da un CERO REPETIBLE Y PRECISO DEL EJE DEL MOTOR, una vez por
 *     vuelta. No requiere guardar nada en flash (a diferencia del homing
 *     con el acelerometro): se re-hace en cada encendido, exactamente
 *     igual que una impresora 3D o maquina CNC que "hommea" cada vez que
 *     se prende. Es intencional, no una limitacion.
 *   - NO te dice por si solo en que vuelta estas dentro del recorrido
 *     completo del riel/husillo (el eje da muchas vueltas para mover la
 *     plataforma de un extremo a otro). Para el CERO ABSOLUTO DE TODO EL
 *     RECORRIDO, este indice magnetico se debe combinar con un limite
 *     fisico en un extremo del riel (switch mecanico/optico/Hall en el
 *     carro, no en el eje del motor) -- ver
 *     `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/`. El indice
 *     magnetico del eje sirve para afinar ese punto con precision
 *     sub-paso una vez que ya sabes en que extremo estas.
 *
 * Conexionado del sensor Hall (ej. A3144, salida en colector abierto):
 *   VCC -> ESP32 3V3 (o 5V si el sensor lo requiere -- revisar tu modelo)
 *   GND -> ESP32 GND
 *   OUT -> ESP32 GPIO definido en HALL_PIN, con pull-up (interno o una
 *          resistencia externa de ~10k a 3V3) -- se activa en BAJO cuando
 *          el iman esta cerca (logica tipica de estos sensores).
 *
 * Conexionado del driver del motor: revisar tu driver especifico -- este
 * sketch asume una interfaz STEP/DIR/ENABLE generica.
 */

#include <Arduino.h>

// --- Pines -- AJUSTAR segun el cableado real de tu driver y sensor ---
#define STEP_PIN    26
#define DIR_PIN     27
#define ENABLE_PIN  25   // activo en BAJO en la mayoria de drivers (A4988/DRV8825/TMC2209)
#define HALL_PIN    34   // entrada digital, con pull-up

// --- Parametros de homing ---
#define DIR_HOMING          HIGH   // sentido de giro para buscar el iman -- AJUSTAR
#define STEP_DELAY_US_FAST  800    // velocidad de aproximacion rapida (menor = mas rapido)
#define STEP_DELAY_US_SLOW  3000   // velocidad de aproximacion fina (mas lento = mas preciso)
#define PASOS_RETROCESO     40     // pasos que retrocede antes de la aproximacion fina
#define MAX_PASOS_BUSQUEDA  4000   // limite de seguridad: si no encuentra el iman en
                                   // esta cantidad de pasos, aborta (evita que el motor
                                   // gire sin parar si el sensor/iman fallan)

long posicionPasos = 0; // posicion relativa al cero establecido por el homing

bool hallActivo() {
  // La mayoria de sensores Hall tipo interruptor son activos en BAJO
  // (colector abierto que se tira a GND cuando detecta el iman).
  return digitalRead(HALL_PIN) == LOW;
}

void unPaso(int delayMicros) {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(delayMicros);
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(delayMicros);
}

// Homing en dos etapas (igual que hace una CNC/impresora 3D): aproximacion
// rapida hasta el primer disparo, retroceso, y aproximacion lenta para un
// punto de disparo mucho mas repetible y preciso que con una sola pasada.
bool homingEjeMotor() {
  Serial.println("Iniciando homing del eje (buscando el iman)...");
  digitalWrite(DIR_PIN, DIR_HOMING);

  // --- Etapa 1: aproximacion rapida ---
  long pasosDados = 0;
  while (!hallActivo()) {
    unPaso(STEP_DELAY_US_FAST);
    pasosDados++;
    if (pasosDados > MAX_PASOS_BUSQUEDA) {
      Serial.println("ERROR: no se detecto el iman dentro del limite de pasos. Revisar sensor/iman/cableado.");
      return false;
    }
  }
  Serial.print("Iman detectado (aproximacion rapida) tras ");
  Serial.print(pasosDados);
  Serial.println(" pasos.");

  // --- Retroceder para volver a aproximarse desde el mismo lado, lento ---
  digitalWrite(DIR_PIN, !DIR_HOMING);
  for (int i = 0; i < PASOS_RETROCESO; i++) {
    unPaso(STEP_DELAY_US_FAST);
  }

  // --- Etapa 2: aproximacion lenta para precision ---
  digitalWrite(DIR_PIN, DIR_HOMING);
  pasosDados = 0;
  while (!hallActivo()) {
    unPaso(STEP_DELAY_US_SLOW);
    pasosDados++;
    if (pasosDados > PASOS_RETROCESO * 3) {
      Serial.println("ERROR: no se re-detecto el iman en la aproximacion lenta.");
      return false;
    }
  }

  Serial.println("Homing completo -- cero del eje establecido.");
  posicionPasos = 0;
  return true;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT_PULLUP);

  digitalWrite(ENABLE_PIN, LOW); // habilita el driver (activo en bajo en la mayoria)

  Serial.println("=== Homing del husillo con iman + sensor Hall ===");
  Serial.println("Comandos: 'h' + Enter = re-homear | 'p' + Enter = imprimir posicion actual");

  homingEjeMotor();
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'h' || c == 'H') {
      homingEjeMotor();
    } else if (c == 'p' || c == 'P') {
      Serial.print("Posicion actual (pasos desde el cero): ");
      Serial.println(posicionPasos);
    }
  }

  // Aca iria el resto del control normal del husillo (mover a una posicion
  // objetivo, etc.), incrementando/decrementando posicionPasos en cada
  // paso real que se de, igual que en cualquier control de stepper en
  // lazo abierto -- este sketch solo cubre el homing en si.
}
