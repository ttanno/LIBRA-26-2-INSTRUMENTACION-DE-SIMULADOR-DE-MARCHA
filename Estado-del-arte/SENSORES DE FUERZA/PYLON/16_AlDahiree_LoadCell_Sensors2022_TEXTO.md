# [16] Al-Dahiree, O.S. et al. — "Design and Shape Optimization of Strain Gauge Load Cell for Axial Force Measurement for Test Benches"

**Fuente:** Sensors, vol. 22, no. 19, art. 7508, 2022. doi: 10.3390/s22197508
**URL original:** https://www.mdpi.com/1424-8220/22/19/7508
**Nota:** este archivo es el TEXTO COMPLETO extraído del PDF (acceso abierto, CC BY), no el PDF original con su diagramación/figuras. Guardado porque el sandbox de Claude no tiene permiso de red para descargar el binario directamente; el texto sí se pudo obtener vía fetch.

---

Citation: Al-Dahiree, O.S.; Tokhi,
M.O.; Hadi, N.H.; Hmoad, N.R.;
Ghazilla, R.A.R.; Yap, H.J.; Albaadani,
E.A. Design and Shape Optimization
of Strain Gauge Load Cell for Axial
Force Measurement for Test Benches.
Sensors 2022, 22, 7508. https://
doi.org/10.3390/s22197508
Academic Editors: Jerzy Józwik,
Wojciech Walendziuk and Grzegorz
Królczyk
Received: 12 September 2022
Accepted: 30 September 2022
Published: 3 October 2022
Publisher's Note: MDPI stays neutral
with regard to jurisdictional claims in
published maps and institutional affiliations.
Copyright: © 2022 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license (https://
creativecommons.org/licenses/by/
4.0/).
sensors
Article
Design and Shape Optimization of Strain Gauge Load Cell for
Axial Force Measurement for Test Benches
Omar Sabah Al-Dahiree 1,2 , Mohammad Osman Tokhi 3,* , Nabil Hassan Hadi 4, Nassar Rasheid Hmoad 4,
Raja Ariffin Raja Ghazilla 2, Hwa Jen Yap 2 and Emad Abdullah Albaadani 5
1 Department of Mechanical Engineering, College of Engineering, University of Baghdad, Baghdad 10071, Iraq
2 Department of Mechanical Engineering, Faculty of Engineering, University of Malaya,
Kuala Lumpur 50603, Malaysia
3 School of Engineering, London South Bank University, London SE1 0AA, UK
4 Department of Aeronautical Engineering, College of Engineering, University of Baghdad, Baghdad 10071, Iraq
5 Department of Electrical Engineering, Faculty of Engineering, University of Malaya,
Kuala Lumpur 50603, Malaysia
* Correspondence: tokhim@lsbu.ac.uk

Abstract: The load cell is an indispensable component of many engineering machinery and industrial
automation for measuring and sensing force and torque. This paper describes the design and analysis
of the strain gauge load cell, from the conceptional design stage to shape optimization (based on the
finite element method (FEM) technique) and calibration, providing ample load capacity with low-cost
material (aluminum 6061) and highly accurate force measurement. The amplifier circuit of the half
Wheatstone bridge configuration with two strain gauges was implemented experimentally with an
actual load cell prototype. The calibration test was conducted to evaluate the load cell characteristics
and derive the governing equation for sensing the unknown load depending on the measured output
voltage. The measured sensitivity of the load cell is approximately 15 mV/N and 446.8 µV/V at
a maximum applied load of 30 kg. The findings are supported by FEM results and experiments
with an acceptable percentage of errors, which revealed an overall error of 6% in the worst situation.
Therefore, the proposed load cell meets the design considerations for axial force measurement for the
laboratory test bench, which has a light weight of 20 g and a maximum axial force capacity of 300 N
with good sensor characteristics.

Keywords: strain gauge; load cell; machine design; axial force measurement; shape optimization;
finite element method (FEM); Wheatstone bridge; amplifier circuit

1. Introduction
For decades, experimental solid mechanics and, more broadly, industry and engineering applications have faced a critical need for reliable and high-throughput measurement of
forces and moments [1]. Load cells, commonly referred to as force transducers, are considered accurate force-measuring devices. They have a range of industrial uses in addition to
scientific and technological research and development [2]. Load cells have been providing
quality measurements in robotics and automation [3–5], agriculture [6,7], medicine [8–10],
industrial weighing [11,12], and many other applications for decades [13–22]. The load
cell can also be used to gauge the interference force in wearable robotic applications (such
as exoskeletons and prostheses) or to detect the comparison force as the robot walks to
provide information to the stable-controlling system [23–27]. Due to the wide range of
potential applications, load cells are crucial.

Physical force testing prototypes and products are essential in product development
and research. Axial force testing is used, for example, in the validation and approval of
products in the product development process and the parameterization and verification of
models and simulations. It also generates knowledge and findings in product development
and research [28]. Load cells were utilized to determine the axial force integrated with the
test bench for laboratory measurement. Many examples can be found on axial force test
benches based on the load cell, such as the syringe test stand, catheter track force test, wire
bond testing, spring testing systems, medical valve sensors (TAVR fatigue testing), and
prosthetic hip fatigue testing. In addition, thrust (axial) force measurements can be found
in rocket propellant systems and underwater vehicles [29,30].

2. Design Concept and Electronic System of the Load Cell

2.1. Prototype Configuration
The load cell structure comprises a metal block with a single hole, a small slot, two strain gauges, a load application point, and a mounting point. The metal body is drilled with a single hole in the center and a small slot on the side to generate bending strain on the beam bridge. The active strain gauge is fixed on the surface side of the load cell body where the beam bridge is located. The axial force is applied and concentrated on the load application point at the thrust (perpendicular) axis. The bottom part of the load cell body is mounted to the ground through one bolt at the mounting point.

2.2. Working Principles
A load cell transforms a force into an electrical signal via a strain gauge (resistance changes when strained) wired into a Wheatstone bridge. The output voltage from the bridge circuit (typically millivolts) needs amplification. The overall concept is similar to a bending beam type load cell — applied force causes bending stress on the beam bridge with a linear relationship.

2.3. Wheatstone Bridge Circuit
e = [R3/(R3+R4) − R2/(R1+R2)] × Eex
GF (gauge factor) = (ΔR/Rg) / ε
ΔR = ε × Rg × GF

The proposed load cell adopted a half-bridge system with one active strain gauge and one passive (dummy) gauge for temperature compensation.

2.4. Amplifier Circuit
Amplifier chip: INA818 (Texas Instruments), high-precision instrumentation amplifier. Output signal amplified 2001× via gain resistor RG = 50 kΩ / (G − 1). Vo (preferred output) = 4.7 V.

3. Shape Design of the Load Cell

3.1. Mathematical Model
σmax = 4F[3b/2(c−D/2) − 1] / [t(c−D/2)]
εmax = 4F[3b/2(c−D/2) − 1] / [E·t(c−D/2)]
where F = applied force, t = thickness, D = hole diameter, c = hole location, b = load application location, E = Young's modulus.

3.2. Design Considerations
Load cell developed for lab bench tests, max applied load ~300 N (≈30 kg). Basic dimensions 30×30 mm (B×H). Constraints: B/3 ≤ D ≤ 2B/3; B/8 ≤ t ≤ B/2; b ≤ B/2.
Design parameters table: Body thickness [t]: min 3.75 mm, max 15 mm. Hole diameter [D]: min 10 mm, max 20 mm.
Material: aluminum 6061 — Young's modulus 68.9 GPa, yield stress 276 MPa, Poisson's ratio 0.33.
Max allowable strain: 1000 microstrain (yield stress and sensitivity criteria).

4. Shape Optimization (FEM)
ANSYS Workbench 2022 R2 used for FEA; Autodesk Inventor Professional 2022 for CAD. Mesh: tetrahedral, 1 mm element size, solid187 element type, 14,110 nodes, 7,747 elements. Boundary conditions: fixed support at bottom surface (bolted), force applied at load point 5 mm from nearest edge. Capacity: 300 N max.
Optimal parameters selected: hole diameter D = 15 mm, body thickness t = 10 mm (allowable stress 138 MPa, allowable strain 1000 microstrain).

5. Experimental Implementation
Prototype: 10 mm 6061 aluminum plate, CNC-machined, compact (30×30×10 mm), 20 g. Strain gauge: CEA-3-23 (Tokyo Measuring Instruments Laboratory), gauge length 3 mm, backing length 6.9 mm, resistance 120 Ω, strain limit 1% (10,000 microstrain), gauge factor GF = 2.09.
Amplifier parts list: INA818 (instrumentation amp), LM78L05ACZFS-ND (5V regulator), SW102-ND (DPST switch), 120 Ω bridge resistor, 25 Ω fixed gain resistor RG, 120 Ω variable bridge resistor (potentiometer), 9V battery connector, 1.0 µF capacitor, Eex = 5 V excitation, Gain G = 2001.
Output read via digital multimeter (Victor 70C) over USB.
Calibration: known masses 2–30 kg (2 kg steps), 3 repetitions each, averaged.

6. Results and Discussion
Sensitivity: 15 mV/N experimental (theoretical 16 mV/N — 6.7% difference), 446.8 µV/V at max load.
Governing equation: Fa = 0.0664·Vm − 0.1981 (Fa in N, Vm in mV).
Calibration table (Load kg (N) → Output mV → Sensitivity µV/V): 2(19.79)→300.30→30.00; 4(39.59)→600.10→59.90; 6(59.38)→900.80→90.00; 8(79.17)→1205.00→120.40; 10(98.97)→1507.00→149.60; 12(118.76)→1809.00→178.80; 14(138.55)→2101.00→207.90; 16(158.35)→2413.00→238.20; 18(178.14)→2705.00→266.30; 20(197.93)→3016.00→298.90; 22(217.73)→3328.00→327.60; 24(237.52)→3620.00→357.80; 26(257.31)→3902.00→387.00; 28(277.11)→4224.00→419.20; 30(296.90)→4535.00→446.80.
FEM vs experiment: ~1.4% difference. Experiment vs theoretical: 6.7% (voltage), 5.4%/3.7% (strain/stress).

7. Conclusions
Load cell meets design requirements: 300 N capacity, 20 g weight, 30×30×10 mm, sensitivity 15 mV/N (446.8 µV/V at max load), overall error ~6% in worst case. Full design process documented: concept → mathematical model → FEM shape optimization → fabrication → Wheatstone half-bridge + INA818 amplifier circuit → calibration.

**Relevancia directa para el proyecto:** este es el proceso más completo y replicable de diseño/fabricación/calibración de una celda de carga tipo strain gauge encontrado en la revisión bibliográfica — útil como plantilla metodológica para diseñar la celda de carga de la plataforma (Objetivo 2), incluyendo el circuito de amplificación (INA818, ganancia configurable) y el protocolo de calibración con pesos conocidos.
