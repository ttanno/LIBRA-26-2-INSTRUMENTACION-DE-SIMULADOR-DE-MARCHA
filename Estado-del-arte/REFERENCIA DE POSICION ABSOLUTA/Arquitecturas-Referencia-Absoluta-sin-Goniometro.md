# Arquitecturas de referencia de posición/ángulo absoluto sin goniómetro

**Fecha:** 27/08/2026
**Contexto:** complementa el pendiente "Referencia de posición absoluta de la plataforma" en `Reportes-Semanales/S3/Pendientes.md` y el prototipo `Firmware/homing_absoluto/`. Objetivo: investigar cómo sistemas ya existentes (fuera del ámbito de sensores MEMS) resuelven el mismo problema — establecer un cero físico absoluto y repetible — sin depender de medirlo a mano con un goniómetro/transportador.

Patrón común encontrado en los cuatro casos: **ninguno mide el ángulo para encontrar el cero.** Todos usan un evento físico repetible (un tope, un marca, una referencia externa fija) que *define* el cero por construcción — el ángulo se mide *después*, relativo a ese evento, no al revés.

---

## 1. Homing por switch / pulso de índice (CNC, impresoras 3D, motion control)

**Mecanismo:** cada eje se mueve lentamente hacia un extremo hasta que dispara un switch físico (mecánico, óptico o magnético) montado en una posición fija de la estructura. En el instante del disparo, el controlador asigna esa posición como el origen de coordenadas (`HOME_OFFSET` en LinuxCNC). Algunos sistemas usan además el **pulso de índice** de un encoder incremental (una marca única por vuelta) para afinar el cero con mayor precisión que el switch solo.

**Por qué es repetible:** el punto de disparo del switch es mecánicamente el mismo siempre — no importa si la máquina se apagó, se movió, o se reinició; al re-homear, el eje vuelve a tocar el mismo punto físico y el software reconstruye las mismas coordenadas, sin medición manual ni herramienta externa.

**Aplicabilidad directa a LIBRA:** esto es exactamente lo que ya habíamos anotado como alternativa al acelerómetro — un switch de fin de carrera (óptico, mecánico o magnético/Hall) en el riel/husillo de traslación. Es la arquitectura más barata y directamente portable a un microcontrolador (ESP32 + un switch + una rutina de homing al encender).

---

## 2. "Mastering" de robots industriales (FANUC, KUKA, ABB)

**Mecanismo:** cada articulación del robot trae **marcas de referencia mecanizadas de fábrica** (líneas o muescas de "0°" en la carcasa del eslabón y su base) o, en robots más grandes, agujeros para insertar **pines de mastering** que solo encajan cuando la articulación está exactamente en su posición cero mecánica. El técnico alinea visualmente las marcas (o inserta el pin), y en ese momento el controlador graba el valor del encoder de esa articulación como referencia absoluta en su memoria (`$REF_POS` / `$MASTER_COUN` en FANUC).

**Por qué es repetible:** la marca/pin es una referencia geométrica fija de la pieza mecánica misma — no depende de gravedad, nivelación del entorno, ni de ningún sensor externo. Una vez hecho el mastering, el robot recuerda el cero permanentemente (se pierde solo si se reemplaza el motor/encoder o se golpea el eje).

**Aplicabilidad a LIBRA:** este es el equivalente "de bajo costo, hazlo tú mismo" a un encoder absoluto industrial — en vez de comprar un encoder absoluto caro, se puede maquinar/marcar una muesca física de referencia en el pivote de flexo-extensión (ej. una perforación pasante que solo alinea en la posición cero, donde insertas un pin de alineación al hacer el homing). Combinado con el AS5600 (que ya da ángulo relativo de alta resolución), esto le daría una referencia absoluta sin depender del acelerómetro ni de nivelar la plataforma.

---

## 3. Referencia láser-gravedad en alineación protésica: Ottobock L.A.S.A.R. Posture

**Mecanismo:** el nombre es literal — **L.A.S.A.R. = Laser Assisted Static Alignment Reference**. El paciente se para sobre dos plataformas de fuerza integradas en el dispositivo; el sistema calcula el centro de presión (línea de carga) a partir de las fuerzas medidas, y proyecta esa línea como un **rayo láser vertical visible** sobre el cuerpo/prótesis del paciente. El protesista alinea la prótesis visualmente contra esa línea láser en vez de medir ángulos con un goniómetro.

**Por qué es repetible:** la línea de carga (vertical que pasa por el centro de presión) es una referencia física real, no una convención — se recalcula en vivo a partir de fuerzas medidas, así que no depende de que el paciente esté "perfectamente derecho" según el ojo del técnico.

**Aplicabilidad a LIBRA:** es la versión profesional de la idea que ya estaban explorando con el acelerómetro (usar gravedad/verticalidad como referencia física), pero usando fuerza en vez de inclinación — combina bien con la celda de carga del pylon que ya están evaluando. No es una arquitectura barata de replicar tal cual (el dispositivo es un producto comercial), pero confirma que "gravedad como referencia física visible/medible" es un principio válido y usado en la práctica clínica real de prótesis, no solo una idea de laboratorio.

**Nota de verificación:** no pude acceder al datasheet/manual técnico completo del dispositivo (varias páginas de Ottobock bloquearon el acceso automatizado); la descripción del mecanismo se basa en el nombre del producto (que es autoexplicativo) y en los títulos/resúmenes de los estudios de validación encontrados — recomendable revisar el manual técnico directamente si se cita esto en el informe.

---

## 4. Prueba estática de calibración en laboratorios de marcha: Vicon Plug-in Gait

**Mecanismo:** antes de cada sesión de captura dinámica, el sujeto se para quieto en una posición neutra de referencia durante una **prueba estática** (unos segundos). El software promedia los ángulos medidos durante esa ventana estática y los guarda como **offset de calibración** — a partir de ahí, todos los ángulos de las pruebas dinámicas posteriores se reportan relativos a ese offset, no en términos absolutos del sensor/marcador.

**Por qué es repetible:** no depende de que el sujeto esté en una postura geométricamente perfecta — solo de que esté quieto y en una postura consistente, y el propio sistema define matemáticamente esa postura como el "cero" de ahí en adelante.

**Aplicabilidad a LIBRA:** esto es, literalmente, el mismo patrón que ya implementamos en `homing_absoluto.ino` (promediar unas muestras en una posición de referencia y guardar el offset) — la diferencia es que en un laboratorio de marcha esto se repite en cada sesión con cada sujeto (porque el "cero" es anatómico, cambia de persona a persona), mientras que en LIBRA el cero es mecánico (el mismo simulador), por lo que tiene más sentido que sea persistente (como ya lo hicimos con la memoria flash) en vez de repetirse cada vez.

---

## 5. Variante barata combinando 1 y 4: sensor Hall + imán fijo (recomendación práctica)

No es un caso de la industria, pero es la combinación que mejor encaja con el presupuesto y las herramientas ya usadas en LIBRA (I2C, ESP32, impresión 3D/mecanizado simple):

- Un imán pequeño fijo en un punto conocido de la estructura (ej. en el riel, en la posición mecánica que define "cero" de traslación).
- Un sensor Hall digital (ej. A3144, o el mismo principio que ya usa el AS5600 pero como interruptor simple, no como encoder) montado en la parte móvil.
- Rutina de homing: al encender, mover el eje lentamente hasta que el sensor Hall detecte el imán → ese es el cero físico, sin contacto mecánico (sin desgaste, a diferencia de un switch mecánico), y sin depender de nivelación ni de gravedad (a diferencia del acelerómetro).

Esto resolvería el eje de traslación (que el acelerómetro no puede resolver) con el mismo nivel de presupuesto/complejidad que ya manejan para el resto del proyecto.

---

## Síntesis comparativa

| Arquitectura | Referencia física | Depende de gravedad/nivelación | Costo | Aplica a traslación | Aplica a rotación |
|---|---|---|---|---|---|
| Switch/pulso de índice (CNC) | Punto mecánico fijo (switch) | No | Bajo (US$1–10) | Sí — directo | Sí |
| Mastering con marca/pin (robots industriales) | Muesca/pin mecanizado | No | Bajo si se maquina propio; alto si es de fábrica | Posible pero menos natural | Sí — directo |
| L.A.S.A.R. Posture (protésica) | Línea de carga (fuerza + gravedad) | Sí | Muy alto (equipo comercial) | No aplica tal cual | Sí, indirecto (vía fuerza) |
| Prueba estática (Vicon Plug-in Gait) | Postura promediada, definida por software | Depende del sensor usado | Ya lo tienen (software) | No aplica tal cual | Sí — ya implementado |
| Hall + imán fijo (recomendación) | Punto magnético fijo | No | Muy bajo (US$1–5) | Sí — directo | Sí |

**Recomendación para LIBRA:** para el eje de rotación, seguir con el homing por acelerómetro que ya está prototipado (`homing_absoluto.ino`) — es válido y barato — pero considerar agregar una muesca/pin de referencia mecánica (arquitectura 2) como respaldo si la nivelación de la plataforma resulta ser un problema real en la práctica. Para el eje de traslación, que el acelerómetro no puede resolver, la combinación switch/Hall + imán (arquitecturas 1 y 5) es la más barata, robusta y coherente con el resto del stack de sensores I2C/ESP32 ya elegido — y no depende de gravedad ni de que la plataforma esté nivelada, a diferencia de todo lo basado en acelerómetro.

---

## Fuentes consultadas

- [Homing Configuration — LinuxCNC](https://linuxcnc.org/docs/html/config/ini-homing.html)
- [FANUC Procedure - Quick Mastering Procedure — DIY Robotics](https://diy-robotics.com/tutorials/fanuc-mastering-procedure-quick-mastering-procedure/)
- [Recalibrating Zero Position of KUKA Robot Joint — Infoneva](https://infoneva.com/en/knowledge/recalibrate-zero-position-kuka-robot)
- [3D L.A.S.A.R. Posture — Ottobock](https://www.ottobock.com/en-ex/product/743L500-64057)
- [Reproducibility and validity of the 3D L.A.S.A.R. posture — Prosthetics and Orthotics International](https://journals.lww.com/poijournal/fulltext/9900/reproducibility_and_validity_of_the_3d_l_a_s_a_r_.386.aspx)
- [The 3D L.A.S.A.R. – A New Generation of Static Analysis for Optimising Prosthetic and Orthotic Alignment — Semantic Scholar](https://www.semanticscholar.org/paper/The-3D-L.A.S.A.R.-%E2%80%93-A-New-Generation-of-Static-for-Bellmann-Blumentritt/95a3025cc874ce0d6cad02dea22a07edb103f58e)
- [PLUG-IN GAIT REFERENCE GUIDE — Vicon Help](https://help.vicon.com/download/attachments/406490967/Plug-in%20Gait%20Reference%20Guide.pdf)
