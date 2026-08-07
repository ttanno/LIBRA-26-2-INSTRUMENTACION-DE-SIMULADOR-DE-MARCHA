# LIBRA — Instrumentación de Simulador de Marcha

**Plataforma móvil instrumentada para simulador de marcha**, orientada a la validación de prótesis transtibiales mediante sensórica embebida (IMU + celda de carga) y adquisición de datos sincronizada.

| | |
|---|---|
| **Curso** | DPB4 — Proyecto de Investigación |
| **Institución** | Pontificia Universidad Católica del Perú (PUCP) |
| **Alumno** | Alessandro Jesus Felix Tello |
| **Asesor** | Dante Angel Elias Giordano |
| **Estado** | En curso — revisión del estado del arte y definición de requerimientos |

---

## Índice

- [Descripción del proyecto](#descripción-del-proyecto)
- [Objetivos específicos](#objetivos-específicos)
- [Alcance](#alcance)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Estado del arte](#estado-del-arte)
- [Reportes semanales](#reportes-semanales)
- [Requerimientos técnicos derivados](#requerimientos-técnicos-derivados)

---

## Descripción del proyecto

En el laboratorio ya existe una plataforma mecánica de simulación de marcha (traslación horizontal por riel + cadena, traslación vertical por husillo y motor paso a paso, y un punto de flexo-extensión en el soporte de la prótesis), construida en un proyecto anterior. Este proyecto **no diseña esa plataforma desde cero**: la **instrumenta**, integrando sensores (IMU y celda de carga), su electrónica de adquisición y un software de registro sincronizado, con el fin de validar prótesis transtibiales bajo cargas y cinemática trazables a normas ISO.

## Objetivos específicos

1. **Diseño mecánico** — Diseñar los soportes/adaptadores para montar la IMU y la celda de carga sobre la estructura ya existente, sin alterar su cinemática.
2. **Sistema electrónico** — Seleccionar e integrar sensores de bajo costo (IMU MEMS, celda de carga) dimensionados según las cargas de referencia de ISO 10328.
3. **Software** — Implementar adquisición continua y sincronizada (I2C/SPI para IMU, ADC dedicado para la celda de carga) con registro, visualización y almacenamiento.
4. **Validación** — Definir un protocolo de calibración y validación cruzada (IMU vs. encoder de la plataforma) anclado a ISO 7500-1 e ISO 22675.

## Alcance

La plataforma **sensa de forma continua** (registro/visualización) durante el uso de la prótesis en la simulación. **No** implementa un lazo de control en tiempo real (p. ej. un PID que retroalimente al simulador con los datos del sensor); esto queda como trabajo futuro. Esta distinción simplifica los requerimientos de software: no se exige baja latencia de lazo cerrado, solo sensado sincronizado y confiable.

## Estructura del repositorio

```
LIBRA/
├── Estado-del-arte/                    Fichas de lectura y fuentes primarias (PDF) organizadas por tema
│   ├── ISO/                            Normas y ensayos estructurales de prótesis
│   ├── SENSORES DE FUERZA/             Celdas de carga, strain gauges, sensores magnéticos
│   ├── SIMULADOR DE MARCHA/            Diseño mecánico de plataformas y bancos de prueba
│   └── SOFTWARE/                       Arquitecturas de software embebido multi-sensor
├── Reportes-Semanales/                 Informes y reportes de avance semanales
│   ├── S1/
│   └── S2/
├── Plan de trabajo 1_DPB4 - Proyecto Simulador de marcha (2).pdf
├── Revision bibliografica - Semana 1-2.md   Revisión bibliográfica consolidada (39 referencias, formato IEEE)
└── README.md
```

## Estado del arte

La [revisión bibliográfica](./Revision%20bibliografica%20-%20Semana%201-2.md) consolida el estado del arte en:

- Simuladores de marcha con sensórica embebida
- Concordancia entre IMU y sistemas ópticos de captura de movimiento
- Calibración y validación de IMU de bajo costo
- Celdas de carga y sensores fuerza-torque en prótesis y bancos de prueba
- Protocolos de calibración de instrumentación en sistemas robóticos/mecatrónicos
- Normas ISO de ensayo estructural de prótesis (ISO 10328, ISO 22675, ISO 7500-1)
- Arquitecturas de software para adquisición sincronizada multi-sensor
- Diseño mecánico de plataformas móviles y bancos de prueba

Cada referencia está trazada a su fuente y marcada según su nivel de verificación (confirmada por fuente primaria, corroboración cruzada, o pendiente de verificar). El documento incluye además una síntesis por objetivo específico y la brecha que justifica el proyecto.

Las fuentes originales (PDF y fichas en Markdown) están organizadas por tema en [`Estado-del-arte/`](./Estado-del-arte).

## Reportes semanales

En [`Reportes-Semanales/`](./Reportes-Semanales) se archivan, por semana, el informe de avance y el reporte semanal del proyecto (formato PUCP: resumen ejecutivo, actividades realizadas, planificado vs. ejecutado, dificultades, lecciones aprendidas y próximos pasos).

## Requerimientos técnicos derivados

Resumen de los requerimientos definidos a partir del estado del arte (detalle completo en la [revisión bibliográfica](./Revision%20bibliografica%20-%20Semana%201-2.md#10-requerimientos-técnicos-derivados-cierre-de-semana-2)):

| Componente | Requerimiento orientativo |
|---|---|
| **IMU** | Sensor MEMS de bajo costo (MPU6050 / ICM-20948), muestreo ≥100 Hz, error objetivo <5° con calibración automática sensor-a-segmento |
| **Celda de carga** | Rango dimensionado sobre ISO 10328 nivel P5 (≤100 kg): proof load 2240 N, ultimate 4480 N; no linealidad objetivo <8% |
| **Software** | Adquisición continua por timestamp compartido, I2C/SPI + ADC dedicado, arquitectura modular para agregar sensores sin rediseño |
| **Validación** | Calibración estática/dinámica trazable (ISO 7500-1) + validación cruzada IMU vs. encoder de la plataforma, referenciada a ISO 22675 |
</content>
