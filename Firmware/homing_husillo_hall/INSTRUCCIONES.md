# Homing del eje del motor con imán + sensor Hall

Pieza física + firmware para dar al motor paso a paso del husillo un **cero repetible y preciso**, sin goniómetro y sin depender de contar pasos (que se puede perder si el motor patina). Está inspirado directamente en el patrón "mastering con marca física" e "índice magnético" que quedó documentado en `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/Arquitecturas-Referencia-Absoluta-sin-Goniometro.md`.

## Qué SÍ resuelve y qué NO (importante, leer antes de armarlo)

Esto da el cero **del eje del motor**, una vez por vuelta — repetible con precisión sub-paso. **No** te dice por sí solo en qué vuelta estás dentro de todo el recorrido del riel (el husillo da muchas vueltas para mover la plataforma de un extremo a otro). Para el cero absoluto de **todo el recorrido**, esto se combina con un límite físico en el carro/riel (switch mecánico, óptico o Hall — ver la comparativa de arquitecturas ya guardada): primero se lleva el carro hasta ese extremo (grueso), y después se usa este índice magnético del eje para afinar el punto exacto de parada (fino). Si quieren, arme también esa versión combinada — este sketch cubre la parte del eje del motor, que es lo que pediste.

A diferencia del homing con acelerómetro (`homing_absoluto.ino`), **este no necesita guardarse en memoria flash** — se vuelve a hacer en cada encendido, exactamente como hace una impresora 3D o una CNC al prenderse. No es una limitación, es cómo funciona este tipo de homing (el evento físico —encontrar el imán— está siempre disponible, no depende de que un humano lo confirme).

## Pieza física a imprimir

Un collarín/disco que se monta en el eje del motor:

- **Diámetro del eje**: mídelo con calibre (en NEMA17 suele ser 5 mm, pero verifícalo — no lo asumas).
- **Cuerpo del collarín**: diámetro exterior ~15–20 mm, espesor ~5–6 mm, con un agujero central prisionero mediante un tornillo M3 perpendicular al eje (permite reajustar el ángulo si el homing sale desalineado, sin tener que reimprimir la pieza).
- **Cavidad para el imán**: un bolsillo cerca del borde exterior del disco, dimensionado para un **imán de neodimio pequeño** (común y barato: ~4 mm de diámetro × 2 mm de espesor, se consigue en cualquier tienda de electrónica/hobby). Orientar el imán con el polo hacia afuera (hacia donde va a pasar el sensor).
- **Soporte del sensor**: un pequeño bracket atornillado al chasis del motor (o impreso también) que sostenga el sensor Hall a 2–4 mm del disco, alineado en el radio donde pasa el imán.

Si prefieren, puedo armarles el diseño paramétrico en OpenSCAD (fácil de ajustar medidas y volver a exportar STL) — solo dime el diámetro real del eje y confirmamos.

## Sensor y cableado

- **Sensor Hall digital** (tipo interruptor, ej. A3144 o similar — 3 pines: VCC, GND, OUT).
- VCC → 3V3 (o 5V si tu módulo específico lo requiere), GND → GND, OUT → `HALL_PIN` (GPIO34 en el sketch, con pull-up interno activado — `INPUT_PULLUP`). La salida es de colector abierto: se activa en BAJO cuando el imán está cerca, que es lo que asume el código.
- Los pines `STEP_PIN`/`DIR_PIN`/`ENABLE_PIN` del sketch son genéricos para cualquier driver STEP/DIR (A4988, DRV8825, TMC2209) — ajústalos a como esté cableado tu driver real.

## Cómo funciona el homing (dos etapas, igual que una CNC)

1. **Aproximación rápida**: el motor gira hasta el primer disparo del sensor.
2. **Retroceso** unos pasos.
3. **Aproximación lenta**: se vuelve a acercar despacio al mismo punto, dando un disparo mucho más repetible y preciso que con una sola pasada rápida (la velocidad afecta la precisión del punto de disparo — por eso CNC/impresoras 3D siempre hacen esto en dos tiempos).
4. Se fija `posicionPasos = 0` en ese punto.

Comandos por Serial: `h` para re-homear manualmente, `p` para imprimir la posición actual en pasos.

## Antes de correrlo en el simulador real

Hay un límite de seguridad (`MAX_PASOS_BUSQUEDA`) para que el motor no gire indefinidamente si el sensor o el imán fallan, pero **no reemplaza un límite mecánico real** — prueben primero con el motor desacoplado del husillo (girando libre) para confirmar que el sensor dispara de forma consistente, antes de conectarlo al mecanismo real donde un giro descontrolado podría chocar contra algo.
