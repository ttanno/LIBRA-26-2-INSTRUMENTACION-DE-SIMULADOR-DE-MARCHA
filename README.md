# LIBRA — Instrumentación de Simulador de Marcha

**Plataforma móvil instrumentada para simulador de marcha**, orientada a la validación de prótesis transtibiales mediante sensórica embebida (IMU + celda de carga) y adquisición de datos sincronizada.

| | |
|---|---|
| **Curso** | DPB4 — Proyecto de Investigación |
| **Institución** | Pontificia Universidad Católica del Perú (PUCP) |
| **Alumno** | Alessandro Jesus Felix Tello |
| **Asesor** | Dante Angel Elias Giordano |
| **Estado** | En curso — Semana 4: pruebas de firmware de IMU (BNO055/MPU6050) y prototipos de referencia de posición absoluta (homing) para la plataforma |

---

## Índice

- [Descripción del proyecto](#descripción-del-proyecto)
- [Objetivos específicos](#objetivos-específicos)
- [Alcance](#alcance)
- [Nota de prioridad (Semana 3)](#nota-de-prioridad-semana-3)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Estado del arte](#estado-del-arte)
- [Reportes semanales](#reportes-semanales)
- [Requerimientos técnicos derivados](#requerimientos-técnicos-derivados)

---

## Descripción del proyecto

En el laboratorio ya existe una plataforma mecánica de simulación de marcha (traslación horizontal por riel + cadena, traslación vertical por husillo y motor paso a paso, y un punto de flexo-extensión en el soporte de la prótesis), construida en un proyecto anterior. Este proyecto parte de esa base ya construida para **integrar sensores** (IMU y celda de carga), su electrónica de adquisición y un software de registro sincronizado, con el fin de validar prótesis transtibiales bajo cargas y cinemática trazables a normas ISO. El diseño mecánico puede implicar tanto soportes/adaptadores externos como modificaciones a la estructura existente, según lo que requiera la integración final de los sensores.

## Objetivos específicos

1. **Diseño mecánico** — Diseñar los soportes/adaptadores (y, de ser necesario, modificaciones a la estructura ya existente) para montar la IMU y la celda de carga, preservando la cinemática de la plataforma.
2. **Sistema electrónico** — Seleccionar e integrar sensores de bajo costo (IMU MEMS, celda de carga) dimensionados según las cargas de referencia de ISO 10328.
3. **Software** — Implementar adquisición continua y sincronizada (I2C/SPI para IMU, ADC dedicado para la celda de carga) con registro, visualización y almacenamiento.
4. **Validación** — Definir un protocolo de calibración y validación cruzada (IMU vs. encoder de la plataforma) anclado a ISO 7500-1 e ISO 22675.

## Alcance

La plataforma **sensa de forma continua** (registro/visualización) durante el uso de la prótesis en la simulación. **No** implementa un lazo de control en tiempo real (p. ej. un PID que retroalimente al simulador con los datos del sensor); esto queda como trabajo futuro. Esta distinción simplifica los requerimientos de software: no se exige baja latencia de lazo cerrado, solo sensado sincronizado y confiable.

## Estructura del repositorio

```
LIBRA/
├── Firmware/                           Sketches ESP32 (Arduino) y visores Python de prueba, por sensor/subsistema
│   ├── test_bno055/                    Prueba I2C + sobremuestreo del IMU BNO055, con visor en tiempo real
│   ├── test_mpu6050/                   Prueba del IMU MPU6050 con filtro complementario propio
│   ├── homing_absoluto/                Prototipo de cero absoluto del pivote por acelerómetro (persistente en flash)
│   └── homing_husillo_hall/            Prototipo de homing del eje del husillo con sensor Hall + imán
├── Estado-del-arte/                    Fichas de lectura, fuentes primarias (PDF) y la síntesis bibliográfica
│   ├── ISO/                            Normas y ensayos estructurales de prótesis
│   ├── REFERENCIA DE POSICION ABSOLUTA/  Arquitecturas de referencia absoluta sin goniómetro (CNC, robótica, laboratorios de marcha)
│   ├── SENSORES DE FUERZA/
│   │   ├── PYLON/                      Celda de carga en la interfaz pylon-plataforma: strain gauge, sensor magnético, comparativa de candidatas
│   │   └── GRF-AMTI/                   Plataforma de fuerza AMTI BP400600 (manuales, pinout, integración)
│   ├── SIMULADOR DE MARCHA/            Diseño mecánico de plataformas y bancos de prueba
│   ├── SOFTWARE/                       Arquitecturas de software embebido multi-sensor
│   ├── Revision bibliografica - Semana 1-2.md   Revisión bibliográfica consolidada (40 referencias, formato IEEE)
│   └── Sensores-LIBRA-Presentacion.pptx         Comparativa de sensores de fuerza, distancia y ángulo (soporte visual)
├── Evidencias/                         Fotos propias del equipo de laboratorio (no bibliográficas, reutilizables entre semanas)
│   ├── simulador/                      Simulador físico existente y método de marcadores M1-M4
│   ├── pruebas-imu-S4/                 Fotos de las pruebas de IMU (banco de protoboard) y del montaje sobre el pylon real (S4)
│   └── arquitectura-sensores-AMTI-S2.png   Diagrama de arquitectura de sensores por DOF (Semana 2)
├── Reportes-Semanales/                 Informes y reportes de avance, por semana
│   ├── S1/
│   │   ├── S1 - Informe Semanal...     Informe semanal (formato PUCP)
│   │   ├── S1 - Reporte de Avance...   Reporte de avance (formato PUCP)
│   │   └── Pendientes.md               Lista de trabajo de la S1 (cerrada; ítems abiertos trasladados a S3)
│   ├── S2/
│   │   ├── S2 - Informe Semanal...
│   │   ├── S2 - Reporte de Avance...
│   │   └── Resumen-Semana2.md          Resumen narrativo de la S2 (arquitectura por DOF, integración AMTI)
│   ├── S3/
│   │   └── Pendientes.md               Lista de trabajo de la S3 (cerrada; ítems abiertos trasladados a S4)
│   └── S4/
│       ├── Resumen-Semana4.md          Resumen narrativo de la S4 (pruebas de IMU y prototipos de homing)
│       └── Pendientes.md               Lista de trabajo activa (se actualiza semana a semana)
├── Plan de trabajo 1_DPB4 - Proyecto Simulador de marcha (2).pdf
└── README.md
```

## Estado del arte

La [revisión bibliográfica](./Estado-del-arte/Revision%20bibliografica%20-%20Semana%201-2.md) consolida el estado del arte en:

- Simuladores de marcha con sensórica embebida
- Concordancia entre IMU y sistemas ópticos de captura de movimiento
- Calibración y validación de IMU de bajo costo
- Celdas de carga y sensores fuerza-torque en prótesis y bancos de prueba
- Protocolos de calibración de instrumentación en sistemas robóticos/mecatrónicos
- Normas ISO de ensayo estructural de prótesis (ISO 10328, ISO 22675, ISO 7500-1)
- Arquitecturas de software para adquisición sincronizada multi-sensor
- Diseño mecánico de plataformas móviles y bancos de prueba
- Arquitectura electrónica de referencia y ubicación del sensor de fuerza (interfaz pylon–plataforma)
- Taxonomía de principios físicos de sensado de fuerza (strain gauge, magnético, capacitivo, FSR, piezoeléctrico, F/T comercial)

Cada referencia está trazada a su fuente y marcada según su nivel de verificación (confirmada por fuente primaria, corroboración cruzada, o pendiente de verificar). El documento incluye además una síntesis por objetivo específico y la brecha que justifica el proyecto.

Las fuentes originales (PDF y fichas en Markdown) están organizadas por tema en [`Estado-del-arte/`](./Estado-del-arte).

## Reportes semanales

En [`Reportes-Semanales/`](./Reportes-Semanales) se archivan, por semana, el informe de avance y el reporte semanal del proyecto (formato PUCP: resumen ejecutivo, actividades realizadas, planificado vs. ejecutado, dificultades, lecciones aprendidas y próximos pasos).

## Requerimientos técnicos derivados

Resumen de los requerimientos definidos a partir del estado del arte (detalle completo en la [revisión bibliográfica](./Estado-del-arte/Revision%20bibliografica%20-%20Semana%201-2.md#10-requerimientos-técnicos-derivados-cierre-de-semana-2)):

| Componente | Requerimiento orientativo |
|---|---|
| **IMU** | Sensor MEMS de bajo costo (MPU6050 / ICM-20948), muestreo ≥100 Hz, error objetivo <5° con calibración automática sensor-a-segmento |
| **Celda de carga (pylon)** | Rango dimensionado sobre ISO 10328 nivel P5 (≤100 kg): proof load 2240 N, ultimate 4480 N; no linealidad objetivo <8%. Ubicación: interfaz pylon–plataforma (no socket, no suelo), 1 eje axial. La candidata inicial (TAL107F-10kg) resultó subdimensionada — ver comparativa actualizada en [`Estado-del-arte/SENSORES DE FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md`](./Estado-del-arte/SENSORES%20DE%20FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md) |
| **Plataforma GRF (AMTI)** | AMTI BP400600 ya disponible en el laboratorio; lectura en tiempo real por salida analógica DB25S (Fx,Fy,Fz,Mx,My,Mz) hacia el mismo ADC (ADS1256), en paralelo a la celda de carga |
| **Software** | Adquisición continua por timestamp compartido, I2C/SPI + ADC dedicado, arquitectura modular para agregar sensores sin rediseño |
| **Validación** | Calibración estática/dinámica trazable (ISO 7500-1) + validación cruzada IMU vs. encoder de la plataforma, referenciada a ISO 22675 |
</content>
