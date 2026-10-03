# Pendientes — Semana 9

## Sensor de fuerza del pylon — protección contra cizalla (30/09/2026)

- [ ] **Sugerencia recibida:** la celda de carga (fuelle QILICHUANGAN, 220 lb ≈ 978 N, 3×M4) puede sufrir esfuerzos de **cizalla** (cargas laterales/momentos) que no mide y que le meten error o la dañan. Propuesta: poner **barras en los laterales** que **concentren/absorban las fuerzas de cizalla**, pero que queden **libres en el eje axial** para no absorber tracción ni compresión (así toda la Fz pasa por la celda).
  - Implementación a evaluar: barras guía con bujes/rodamientos lineales (desliza en Z, bloquea X/Y y momentos).
  - **Sujeción de las barras:** fijas a una de las partes (bloque superior o inferior) mediante **anillos de retención** (seegers/circlips en ranura), y libres para deslizar en la otra parte, de modo que no se transmita carga axial por ellas.
    - Cuidar que los anillos solo ubiquen la barra (no la precarguen axialmente) y que el lado libre tenga recorrido suficiente para la deflexión de la celda + tolerancias.
  - Cuidar: la fricción de las guías en Z pasa a ser error de medición (bujes de baja fricción, ajuste con juego mínimo, lubricación); alineación de las barras con el eje de la celda para que no se traben.
  - Límite lateral de la celda no está en la ficha → preguntar al vendedor (junto con la duda "Push-Pull") o medirlo; mientras tanto asumir ≲10 % de la nominal (~100 N) como criterio conservador propio.
  - Verificar en Fusion (Static Stress) que el cortante lo tomen las barras y no los 3 pernos M4 de la celda.
