# Driver de prueba 2x VL53L1X — sensores de distancia ToF (ESP32)

Sketch de prueba para los dos sensores de distancia ToF VL53L1X de la placa
superior. Verifica el cableado I2C, la secuencia de reasignación de
dirección (necesaria porque los dos sensores comparten el mismo bus y la
misma dirección de fábrica) y la lectura básica de distancia — ver el
pinout completo y su justificación en
[`../PCB_placa_superior_PINOUT.md`](../PCB_placa_superior_PINOUT.md) (Secc. 2-4).

## 1. Conexionado

| Señal | ESP32 | Notas |
|---|---|---|
| I2C SDA (compartido, ambos sensores) | GPIO21 | pin I2C por defecto del ESP32 |
| I2C SCL (compartido, ambos sensores) | GPIO22 | pin I2C por defecto del ESP32 |
| SHUT / XSHUT ToF1 (U3) | GPIO25 | activo en bajo, imprescindible un GPIO independiente por sensor |
| SHUT / XSHUT ToF2 (U2) | GPIO26 | ídem |
| INT (ambos) | sin conectar (NC) | este sketch lee por *polling*, no usa interrupciones |
| VCC / GND (ambos) | 3.3V / GND | común con el resto del circuito |

## 2. Por qué hace falta reasignar dirección I2C

Los dos VL53L1X vienen de fábrica con la **misma dirección fija (0x29)**, así
que no se pueden diferenciar en el mismo bus solo por dirección. El sketch
resuelve esto con el pin **SHUT** de cada uno:

1. Mantiene a **ambos** en reset (SHUT en bajo).
2. Saca a **ToF1** del reset (queda en 0x29, el otro sigue apagado) y le
   asigna la dirección **0x30** con `setAddress()`.
3. Recién ahí saca a **ToF2** del reset — como ToF1 ya se movió a 0x30, ToF2
   puede arrancar en su dirección de fábrica (0x29) sin chocar.

Por eso el orden importa: si se sacara a los dos del reset al mismo tiempo,
ambos responderían en 0x29 y el bus quedaría en conflicto.

## 3. Software (Arduino IDE)

1. Instalar la librería **"VL53L1X" de Pololu**
   ([github.com/pololu/vl53l1x-arduino](https://github.com/pololu/vl53l1x-arduino))
   desde el Library Manager: Herramientas > Administrar Bibliotecas > buscar
   `VL53L1X` > instalar la de Pololu.
2. Abrir `test_tof.ino` como sketch independiente (misma estructura que los
   demás sketches de `Firmware/`).
3. Revisar los pines (`PIN_I2C_SDA`, `PIN_I2C_SCL`, `PIN_SHUT_TOF1`,
   `PIN_SHUT_TOF2`) contra tu cableado real antes de cargar.
4. Cargar y abrir el Monitor Serie a **115200 baudios**.

## 4. Calibración

**Este sketch no tiene comandos de calibración por Serial ni persiste nada
en flash.** A diferencia del HX711 (celda de carga, necesita tara + factor
de escala definidos por el usuario — ver
[`../test_hx711/INSTRUCCIONES.md`](../test_hx711/INSTRUCCIONES.md)) o del
BNO055 (cero absoluto de orientación), el VL53L1X ya viene calibrado de
fábrica: el chip ST hace su propia compensación interna de offset/crosstalk
y entrega la distancia en mm directamente. No hay ningún dato de
calibración de este sketch que se pueda perder — es independiente y no
toca la calibración guardada del HX711 en `test_hx711.ino` (namespaces NVS
distintos, y este sketch ni siquiera usa `Preferences`).

## 5. Qué esperar

Al arrancar, el sketch imprime la secuencia de inicialización y un escaneo
del bus I2C — deberías ver dos dispositivos: **0x29** (ToF2) y **0x30**
(ToF1, reasignado). Si solo aparece uno o ninguno, revisar alimentación y
cableado SHUT/SDA/SCL antes de seguir.

Luego, salida CSV continua: `dist1_mm,status1,dist2_mm,status2`

- `dist1_mm` / `dist2_mm`: distancia medida en milímetros por ToF1 y ToF2.
- `status1` / `status2`: código de estado de la librería Pololu — **0 =
  lectura válida** (`RangeValid`); cualquier otro valor indica una lectura
  no confiable (objeto fuera de rango, señal muy débil, etc.) y no debe
  tomarse como distancia real.

Si ves `ERROR: timeout esperando datos de ToF1/ToF2`, el sketch no está
recibiendo respuesta de ese sensor — lo más común es un problema de
alimentación, cableado SDA/SCL, o que el SHUT correspondiente no llegó a
sacarlo del reset.

## 6. Visor en tiempo real (Python)

Igual que con el HX711, hay un visor gráfico en `visor_python/visor_tof.py`
que lee el puerto serial y grafica la distancia de ambos sensores en vivo.

```
cd visor_python
pip install -r requirements.txt
python visor_tof.py --port COM5
```

## 7. Siguiente paso

- Con ambos sensores respondiendo y dando distancias razonables, definir el
  soporte/orientación mecánica final de cada ToF en la plataforma y, si
  hace falta, migrar la lectura de *polling* a interrupción (usar el pin
  INT de cada sensor) una vez integrado al firmware principal.
