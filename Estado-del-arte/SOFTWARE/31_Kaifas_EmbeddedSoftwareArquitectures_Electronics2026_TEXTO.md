# [31] Kaifas, T. — "A Review of Embedded Software Architectures for Multi-Sensor Wearable Devices: Sensor Fusion Techniques and Future Research Directions"

**Fuente:** Electronics, vol. 15, no. 2, art. 295, 2026. doi: 10.3390/electronics15020295
**URL original:** https://www.mdpi.com/2079-9292/15/2/295
**Nota:** este archivo es el TEXTO COMPLETO extraído del PDF (acceso abierto, CC BY), no el PDF original con su diagramación/figuras. Guardado automáticamente porque el sandbox de Claude no tiene permiso de red para descargar el binario directamente; el texto sí se pudo obtener vía fetch.

---

Academic Editors: Simin Masihi and
Lina Sawalha
Received: 1 December 2025
Revised: 4 January 2026
Accepted: 7 January 2026
Published: 9 January 2026
Copyright: © 2026 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license.
Review
A Review of Embedded Software Architectures for Multi-Sensor
Wearable Devices: Sensor Fusion Techniques and Future
Research Directions
Michail Toptsis, Nikolaos Karkanis , Andreas Giannakoulas and Theodoros Kaifas *
Department of Electrical and Computer Engineering, Democritus University of Thrace, 67100 Xanthi, Greece
* Correspondence: tkaifas@ee.duth.gr
Abstract
The integration of embedded software in multi-sensor wearable devices has revolutionized
real-time monitoring across health, fitness, industrial, and environmental applications.
This paper presents a comprehensive approach to designing and implementing embedded
software architectures that enable efficient, low-power, and high-accuracy data acquisition
and processing from heterogeneous sensor arrays. We explore key challenges such as
synchronization of sensor data streams, real-time operating system (RTOS) integration,
power management strategies, and wireless communication protocols. The reviewed
framework supports modular scalability, allowing for seamless incorporation of additional
sensors or features without significant system overhead. Future research directions of the
embedded software include Hardware-in-the-Loop and real-world validation, on-device
machine learning and edge intelligence, adaptive sensor fusion, energy harvesting and
power autonomy, enhanced wireless communications and security, standardization and
interoperability, as well as user-centered design and personalization. By adopting this
focus, we can highlight the potential of the embedded software to support proactive
decision-making and user feedback through edge-level intelligence, paving the way for
next-generation wearable monitoring systems.
Keywords: embedded software; multi-sensor wearable devices; real-time monitoring;
adaptive sensor fusion; real-time operating system; hardware-in-the-loop; on-device
machine learning; user-centered design
1. Introduction
The landscape of real-time monitoring is undergoing a significant transformation,
driven by the rapid evolution of embedded software and the widespread adoption of
multi-sensor wearable devices. These technologies are moving beyond simple fitness
tracking to become integral tools in health and industrial safety, paving the way for a future
of proactive and personalized data-driven insights. The integration of multiple sensors
into a single wearable device, however, presents a complex set of challenges that require
sophisticated embedded software solutions for effective real-time data acquisition and
processing. Wearable devices have seamlessly integrated into daily life, revolutionizing
how we interact with technology and monitor our personal data. This continuous stream of
data is empowering individuals to take a more robust approach to their health and wellness
while also enabling new examples in remote patient monitoring and athletic performance
optimization. The ability to track vital signs, sleep patterns, and physical activity provides
invaluable insights for both personal well-being and clinical assessment [1–5].
Electronics 2026, 15, 295 https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 2 of 29
The drive to incorporate multiple sensors into wearable devices stems from the need
for more accurate, reliable, and, contextually, aware data. While a single sensor can provide
a specific metric, a fusion of data from multiple sensors offers a more holistic and robust
understanding of the user’s state and interaction with the environment. For example,
by combining data from an accelerometer, gyroscope, and magnetometer, it is possible
to achieve a much more precise and reliable measurement of movement and orientation
than with any single sensor alone. This multi-sensor approach is crucial for advanced
applications such as fall detection for the elderly, detailed biomechanical analysis for
athletes, and monitoring the vital signs of workers in hazardous environments. The ability
to process and synthesize this complex data at the device level, or the “edge,” is a key
driver for innovation in embedded software, as it enables real-time feedback and reduces
latency and privacy concerns associated with cloud-based processing [1–3,6].
Despite the immense potential of multi-sensor wearable devices, their development
and widespread adoption are hindered by several significant challenges that must be
addressed through intelligent embedded software design. These challenges include the
following [2,4]:
• Signal dropout: The integrity of data collected from wearable sensors can be compromised by factors such as poor skin contact, motion artifacts, and environmental
interference, leading to incomplete or inaccurate data sets [5,7].
• Sensor drift and calibration: The accuracy of sensors can degrade over time, a phenomenon known as “drift,” which necessitates periodic recalibration to ensure the
reliability of the collected data. This process can be unwieldy for the user and requires
revolutionary software solutions for automatic and seamless calibration [8].
• Power constraints and battery life: The continuous operation of multiple sensors, coupled with the computational demands of data processing and wireless communication,
places a significant strain on the limited battery capacity of small, lightweight wearable
devices. Energy-efficient hardware and intelligent power management software are
therefore significant for extending battery life and enhancing the user experience [3,4].
• Real-time processing demands: The aggregation and fusion of data from multiple
sensors in real time require significant computational power. Embedded systems in
wearable devices are typically resource-constrained, making it a challenge to perform
complex data processing tasks without introducing unacceptable latency. This necessitates the development of highly efficient algorithms and software architectures that
can operate within these constraints [3,4].
These challenges motivate a system-level review that jointly considers sensor fusion algorithms, embedded software architectures, communication protocols, and power
management strategies under real-world wearable constraints.
This paper reviews robust solutions to the challenges of multi-sensor wearable systems
by detailing several key contributions of the field. These advancements aim to provide a
practical and efficient foundation for the next generation of real-time monitoring applications.
To effectively address the complexities of real-time monitoring, this paper focuses on
the following noteworthy issues:
• Embedded software framework: A comprehensive embedded software framework
tailored for multi-sensor data processing can allow the device to reach excellent levels
of performance. The framework is designed to manage the intricacies of collecting
and preparing data from various sensors in a resource-constrained environment [3,4].
• Sensor performance evaluation: A thorough evaluation of sensor performance is
presented, analyzing the outputs of sensors both individually and when their data
streams are fused. This analysis validates the benefits of sensor fusion in improving
data accuracy and reliability [3,6].
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 3 of 29
• Real-Time synchronization and fusion: This paper details the implementation of realtime synchronization and data fusion using efficient embedded techniques. This
is critical for ensuring low-latency processing and immediate feedback, which are
essential for real-world applications [6].
The remainder of this paper is structured as follows: Section 2 reviews embedded
system constraints in wearable devices, focusing on processing, memory, and real-time
requirements. Section 3 analyzes wired and wireless communication protocols for multisensor wearables. Section 4 surveys sensor fusion techniques, from lightweight complementary filters to Kalman-based methods, emphasizing embedded deployment suitability.
Section 5 evaluates embedded software architectures, comparing bare-metal and RTOSbased designs. Section 6 discusses power management strategies and energy-harvesting
approaches for wearable systems. Section 7 addresses practical deployment challenges,
including scalability, reliability, user experience, privacy, and security. Section 8 provides
a comparative synthesis of the literature and identifies open research challenges, while
Section 9 concludes this review and outlines future research directions.
Tables 1 and 2 present representative multi-sensor systems reported in the literature,
focusing on fusion levels, sensor types, sensor configurations, feature domains, fusion
strategies, classifiers/algorithms, application areas, and performance metrics. This comparison illustrates the diversity of design choices in wearable systems; for example, Atallah
et al. [9] employ cooperative feature-level fusion across multiple accelerometers for activity
recognition, while Liu et al. [10] and Bicocchi et al. [11] use different combinations of
sensor types, fusion strategies, and classifiers for physical activity estimation and activity
recognition. Presenting these systems side-by-side highlights variations in sensor configuration, evaluation datasets, and performance, revealing gaps in scalability and real-time
applicability that systematic studies aim to address.
Table 1. State-of-the-art table of systems in multi-sensors.
Reference/System Fusion Level Sensor Types
Used
Sensor
Configuration
Feature
Domain
Fusion
Strategy
Classifier/
Algorithm
Application
Area
Atallah et al. [9] Feature-level Accelerometer
(×3)
Wrist, Waist,
Ankle Time domain Cooperative k-NN (k = 1) ActivityRecognition
Liu et al. [10] Feature-level Accelerometer Wrist, Waist Time and
frequency Complementary SVM, DT
Physical
Activity
Estimation
Bicocchi et al. [11] Decision-level Accelerometer Pocket (Mobile
Phone) Time domain Cooperative Instance-based,k-NN
Activity
Recognition
Pärkkä et al. [12] Feature-level
Accelerometer
+ Physio
sensors
Wrist Time domain Complementary SVM Activity
Monitoring
Table 2. Detailed description of multi-sensor systems.
Reference/System Accuracy (%) Data Window Size Evaluation Dataset
Atallah et al. [9] 91% 1 s window, 50% overlap Custom Dataset
Liu et al. [10] 93.2% 2 s window, 50% overlap Custom Dataset
Bicocchi et al. [11] ~75% 3 s window Real-Life Activity Dataset
Pärkkä et al. [12] N/A 2–5 s window Custom Dataset
Tables 1 and 2 provide a comparative overview of representative multi-sensor systems
reported in the literature, detailing fusion levels, sensor types, sensor configurations, feature
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 4 of 29
domains, fusion strategies, classifiers, application areas, and performance metrics such as
accuracy, data window size, and evaluation dataset.
This comparison highlights the diversity of design choices in multi-sensor wearable
systems; for example, Atallah et al. [9] and Liu et al. [10] use feature-level fusion with
accelerometers, while Bicocchi et al. [11] employ decision-level fusion with a mobile phone
sensor, illustrating trade-offs in sensor placement and algorithmic complexity. Accuracy
varies across systems (e.g., 93.2% for Liu et al. [10] vs. ~75% for Bicocchi et al. [11]),
reflecting differences in dataset characteristics and evaluation strategies.
Analyzing these tables reveals gaps in scalability, real-time applicability, and standardization, which underscore the importance of systematic comparative studies for informing
design decisions in multi-sensor wearable platforms.
Scope and Contributions of This Review
This review focuses on embedded sensor fusion systems for wearable applications,
with particular emphasis on embedded software architectures, real-time constraints, communication protocols, and power management strategies. Unlike existing reviews that
primarily address algorithmic aspects of sensor fusion or application-specific case studies, this work provides a system-level perspective that integrates hardware constraints,
software design choices, and deployment considerations. The main contributions of this
review are as follows: (i) a comparative analysis of sensor fusion techniques with respect
to embedded deployment constraints, (ii) a structured evaluation of communication and
software architectures used in multi-sensor wearables, and (iii) an assessment of current
technological maturity, practical limitations, and open research challenges.
This review systematically evaluates embedded software architectures and sensor
fusion techniques in multi-sensor wearable devices. Unlike prior reviews that focus on
individual sensor modalities or a single application domain, this work synthesizes findings across multiple studies to provide a comparative analysis of algorithmic trade-offs,
energy efficiency, real-time performance, and practical deployment considerations. Key
contributions of this review include the following:
1. Critical comparison of sensor fusion strategies highlighting accuracy, computational
cost, and suitability for different wearable applications.
2. Evaluation of embedded software architectures, emphasizing scalability, maintainability, and power-aware design.
3. Analysis of practical challenges, including energy management, hardware limitations,
and system integration issues.
4. Identification of gaps in the existing literature and recommendations for future research directions, guiding both academic and industrial practitioners.
2. Embedded System Constraints in Wearable Devices
In the current section, we elaborate and review issues related to fusion strategy,
embedded software architecture, real-time data acquisition, buffering and synchronization,
communication protocols and power optimization techniques.
Wearable embedded systems operate under strict constraints related to processing
capability, memory availability, and real-time responsiveness. Microcontrollers used in
wearable platforms typically offer limited clock frequencies and memory resources, which
directly influence algorithm selection and software architecture. Real-time constraints arise
from the need to sample multiple sensors synchronously, execute fusion algorithms within
fixed deadlines, and ensure deterministic system behavior. These constraints strongly affect
the feasibility of advanced fusion techniques and motivate lightweight implementations
tailored to embedded platforms.
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 5 of 29
Processing, Memory and Real-Time Constraints
An effective real-time data pipeline is fundamental to the performance of the system,
ensuring that data from heterogeneous sensors is captured, temporarily stored, and timealigned accurately before being passed to the fusion algorithms. We note here that a
structured approach that leverages the features of the RTOS is employed to manage this
process efficiently and prevent data loss or timing errors [13].
The acquisition of sensor data is managed by dedicated, high-priority RTOS tasks,
with a separate task assigned to each sensor. To minimize latency, data acquisition is
interrupt-driven. Hardware interrupt is generated by the sensor or a timer peripheral
when new data is available. This interrupt triggers the high-priority acquisition task, which
reads the sensor data immediately. This ensures that data capture is prioritized over all
lower-priority processes, satisfying the system’s real-time processing demands [14].
To decouple the high-frequency, time-critical data acquisition tasks from the more
computationally intensive and potentially slower fusion task, a buffering mechanism is implemented. Each sensor’s acquisition task writes its incoming data into a dedicated circular
buffer (or ring buffer). This First-In First-Out (FIFO) structure is highly efficient in memory
usage and processing overhead. The use of buffers provides essential resilience against
transient peaks in processor load, preventing data loss (signal dropout) and ensuring that
the fusion algorithm always has a consistent stream of data to process [13,15].
The synchronization of sensor data streams is one of the most critical challenges. Since
sensors operate at different sampling rates and on independent clocks, their data must be
accurately aligned in time before fusion. A system should achieve this through two key
techniques [16]:
1. High-resolution time stamping: Immediately upon acquisition within the highpriority task, each data sample from every sensor is tagged with a timestamp from
a common, high-resolution hardware timer. This establishes a unified time base
across all sensor data streams, which is essential for the fusion algorithm to correlate
measurements correctly [17].
2. RTOS synchronization primitives: The RTOS is used to manage the temporal alignment of data for processing. The main data fusion task waits on an RTOS synchronization object (such as an event flag or semaphore). The individual sensor acquisition
tasks signal this object after placing new, time stamped data into their respective
buffers. The fusion task is only activated to run when a complete and temporally
consistent set of measurements is available from all required sensors [14,17].
To illustrate the differences between various real-time data pipeline architectures,
Table 3 compares traditional, RTOS-based, and middleware approaches across key aspects
such as data capture, buffering, and synchronization.
Table 3 summarizes state-of-the-art real-time data pipeline approaches in embedded
sensor systems. It compares traditional polling-based pipelines (e.g., Extended Kalman
Filter (EKF fuse)), RTOS-driven ring buffer pipelines, and middleware-based approaches
(e.g., µRT or DDS frameworks) across key aspects such as data capture triggering, buffer
structure, time stamping, synchronization, resilience to processing load, and maturity.
The table highlights the trade-offs among simplicity, determinism, and scalability:
traditional pipelines are simple but susceptible to buffer overflows; RTOS-based pipelines
provide predictable, high-priority acquisition and decoupled buffers; middleware-based
approaches enable flexible publish–subscribe architectures but are still emerging in embedded wearable systems. This comparison allows practitioners to select the appropriate
pipeline architecture based on workload, latency, and real-time performance requirements.
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 6 of 29
Table 3. State-of-the-art table for real-time data pipelines.
Aspect Traditional (e.g., EKF Fuse) RTOS + Ring Buffer
Pipeline Middleware (µRT, etc.)
1. Data Capture
Triggering Polling, periodic tasks Interrupt-driven,high-priority acquisition
ISR → topic publish
(ring buffer enqueued)
2. Buffer Structure Fixed buffers, double-buffer Circular FIFO per sensor Ring buffers in
publish–subscribe topics
3. Timestamping Often software layer High-resolution hardware
timer at acquisition task
Timestamp at publish
based on message info
time
4. Synchronization
Mechanism
Manual polling or
heuristics
RTOS semaphores/events
combining all sensors
Topic subscriber
triggered when all
timestamps align
5. Resilience to
Processing Load
Minimal: buffer overflows
possible
Buffers decouple fusion; ISR
always handles capture
Topic logic drops or
reschedules based on
buffer age
6. Maturity/Usage
Widely deployed in
avionics/UAVs (EKF
pipelines)
Common in embedded
sensor systems (FreeRTOS,
VxWorks)
Emerging in µRT and
DDS frameworks
Overall, these constraints favor lightweight, deterministic processing pipelines and
limit the practical deployment of computationally intensive fusion and middleware solutions in wearable systems.
3. Communication Protocols for Multi-Sensor Wearables
3.1. Wired Communication Interfaces (SPI, I2C, UART)
Nowadays, a framework can rely on a tiered communication strategy to manage both
the on-board interfacing with sensors and the external transmission of processed data. The
selection of protocols is driven by the requirements for data throughput, power efficiency,
and implementation complexity within the embedded environment.
For communication between the central microcontroller and the various sensors within
the wearable device, industry-standard serial protocols are employed. The choice depends
on the specific sensor’s interface and data rate requirements:
• Serial Peripheral Interface (SPI): This is a synchronous serial communication protocol
used for high-throughput sensors like accelerometers and gyroscopes. Its full-duplex,
high-speed capabilities ensure that data can be read from sensors with minimal latency,
which is essential for real-time applications [18,19].
• Inter-Integrated Circuit (I2C): This two-wire protocol is used for sensors that require
lower data bandwidth, such as magnetometers or environmental sensors. Its primary
advantage is the ability to connect multiple slave devices to the same bus, reducing
pin count and simplifying the hardware layout [18,20].
• Universal Asynchronous Receiver-Transmitter (UART): While primarily used for
debugging and console output, UART can also be utilized for interfacing with specific
modules, such as some GPS receivers, that use a serial stream for data output [18,20,21].
For transmitting the fused sensor data from the wearable device to an external entity
like a smartphone or a data-logging gateway, relative systems utilize Bluetooth Low Energy
(BLE). BLE is the ideal choice for embedded software applications due to its extremely low
power consumption, which is a critical factor for extending the battery life of wearable
devices. Its architecture is optimized for sending small, intermittent bursts of data, which
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 7 of 29
perfectly aligns with the needs of real-time monitoring applications. The integration
of a BLE stack, managed by a dedicated low-priority RTOS task, allows the system to
wirelessly send alerts, summary statistics, or raw data streams for further analysis and user
feedback [21–27].
Figure 1 summarizes common wired communication interfaces used in wearable
sensor integration, highlighting trade-offs between throughput, wiring complexity, and
power consumption.
Figure 1. Serial communication protocols (SPI, I2C, and UART), highlighting throughput, wiring
complexity, and suitability for multi-sensor wearable systems.
Collectively, Figure 1 supports the selection of appropriate communication interfaces
based on throughput requirements, hardware simplicity and system power constraints,
ensuring reliable data exchange across the wearable monitoring platform.
Table 4 summarizes the characteristics of SPI, I2C, UART, and BLE protocols, detailing
their use cases, target devices, advantages, latency/throughput, and wiring requirements.
This comparison highlights the complementary roles of these protocols in multi-sensor
embedded systems: SPI is suitable for high-speed motion sensors, I2C for multi-device
setups, UART for debugging, and BLE for low-power wireless transmission. Understanding
these trade-offs is essential for designing efficient communication interfaces in real-time
wearable systems.
Table 4. Comparative overview of sensor communication interfaces.
Protocol Use Case Device Advantages Latency/Throughput Wiring
SPI High-speed
motion sensors
Accelerometer,
gyroscope
Full-duplex, low
latency ≥10 Mbps 4 wires
I
2C
Mid/low
bandwidth sensors
Magnetometer,
temperature,
pressure
Multi-slave, 2-wire
simplicity 100 kbps–5 Mbps 2 wires
UART Serial modules
and debugging GPS, console Simple P2P,minimal hardware ≤1 Mbps 2 wires
BLE Wireless data
transmission
Gateway,
smartphone
Ultra-low power,
burst transfers 100 kbps–1 Mbps Wireless
3.2. Wireless Communication Interfaces (BLE and Related Protocols)
Improving wireless communication and security for wearables is one of the highest priorities. Thus, the research and the adoption of advanced protocols (BLE, UWB, LoRaWAN)
and strong encryption/authentication mechanisms is highly important.
The evolution of wearable embedded systems increasingly relies on advanced wireless
communication and robust security mechanisms. As wearables become more sophisticated,
they generate larger volumes of sensor data, often transmitted in real time for health monitoring, industrial safety, or sports analytics. Traditional low-power Bluetooth protocols
and simple encryption methods may no longer meet the requirements of high-throughput,
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 8 of 29
low-latency, and secure data exchange. Therefore, future research is focused on integrating next-generation wireless technologies such as Bluetooth 5.3, Ultra-Wideband (UWB),
LoRaWAN, and 5G, alongside end-to-end security solutions to protect sensitive data and
ensure operational reliability [4,27].
Efficient, low-latency, and long-range wireless communication is crucial for continuous, real-time wearable monitoring and remote analytics. Bluetooth 5.3 offers enhanced
throughput, improved energy efficiency, and extended range compared to previous versions. Future wearables could leverage adaptive channel selection, low-energy modulation
schemes, and multi-device synchronization to maintain reliable connectivity in complex
environments. Research could focus on dynamic topology management, interference
mitigation, and coexistence with other wireless protocols in dense environments [16].
Higher data rates, improved range, and energy efficiency allow wearables to communicate more reliably with smartphones, gateways, and cloud systems. Ultra-Wideband
(UWB) is emerging as a key technology for precise localization, proximity detection, and
secure communications. Future research may explore integration of UWB with wearable
networks, low-power ranging protocols, and privacy-preserving localization algorithms,
enabling applications such as indoor navigation, asset tracking, and social distancing alerts
in crowded environments [27].
UWB enables centimeter-level localization accuracy, low-latency communication, and
secure proximity sensing for wearables. LoRaWAN and other long-range, low-power
wide-area network (LPWAN) protocols offer the potential for remote monitoring of health
or environmental parameters without relying on local gateways or smartphones. Future
studies could examine hybrid connectivity strategies, where wearables intelligently switch
between short-range (Bluetooth, UWB) and long-range (LoRa, NB-IoT) communication
based on context, data urgency, and energy availability [16].
Low-power, long-range networks allow for continuous monitoring in remote or industrial settings with minimal energy consumption. Security is a critical future direction.
Wearables often transmit highly sensitive health or biometric data, which makes them
prime targets for cyber-attacks. Research must focus on end-to-end encryption, secure boot,
authentication protocols, and lightweight cryptography suitable for low-power embedded
devices. Advanced methods, such as homomorphic encryption and blockchain-based
authentication, could allow for secure data processing in cloud or edge systems without
compromising privacy [28].
Protecting wearable data against unauthorized access and tampering is essential,
especially in healthcare, finance, and industrial applications. Adaptive security mechanisms
are a promising research direction. Wearables could dynamically adjust encryption levels,
authentication steps, or network protocols based on risk assessment, energy availability, or
user activity, ensuring both robust protection and power efficiency [29].
Security protocols that adjust dynamically can balance privacy, latency, and energy
consumption in real time. Interference management and coexistence are also critical.
Wearables often operate in crowded frequency bands with Wi-Fi, cellular, and other IoT
devices. Future research can focus on smart spectrum sensing, dynamic frequency hopping,
and cognitive radio techniques to minimize communication errors and maintain reliable
data transfer [16].
Cognitive frequency selection and adaptive channel management ensure consistent
connectivity in dense wireless environments. Another emerging trend is edge-assisted
communication, where wearable devices offload computation to edge nodes or nearby gateways, reducing latency and power requirements. Future research may explore optimized
data routing, cooperative edge-wearable processing, and compression-aware protocols to
maximize efficiency without compromising performance [29].
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 9 of 29
Offloading computation to edge nodes reduces latency and energy use, and improves
real-time data analysis. Integration with AI-driven network management is another promising avenue. Machine learning can predict network congestion, optimize packet scheduling,
and detect anomalous communication patterns, improving both performance and security. Future work could investigate reinforcement learning for dynamic communication
management and anomaly detection in multi-wearable networks [30].
Machine learning enables predictive network optimization, energy-efficient routing,
and early detection of security threats. Finally, future wearables may adopt multi-protocol
and multi-band architectures, allowing for seamless switching between Bluetooth, UWB,
LoRaWAN, Wi-Fi, and 5G, depending on latency requirements, energy constraints, and
environmental conditions. This flexibility will be essential for wearables that operate in
diverse scenarios, from home-based health monitoring to industrial safety systems [31].
Flexible communication architectures allow wearables to adapt dynamically, balancing
energy, latency, and reliability across various networks. In conclusion, enhanced wireless
communication and security are fundamental to the future of wearable embedded systems. By integrating next-generation wireless protocols, adaptive security, AI-assisted
network management, and multi-protocol architectures, wearables can achieve reliable,
secure, and energy-efficient data exchange, enabling new applications in healthcare, sports,
industrial monitoring, and beyond. Research in low-power secure communication, hybrid networks, and intelligent edge-assisted processing will drive the next generation of
connected, trustworthy, and autonomous wearables [29].
3.3. Comparative Discussion and Design Implications
From a system design perspective, the selection of communication protocols represents
a trade-off between data throughput, power consumption, scalability, and implementation
complexity. Wired interfaces such as SPI and I2C are well suited for short-range, highreliability sensor interconnections, whereas wireless protocols like BLE enable flexible data
transmission to external devices at the cost of increased energy consumption and latency.
The maturity of these protocols makes them reliable for commercial deployment; however,
challenges remain in coordinating multiple communication interfaces while maintaining
low power consumption in wearable systems.
In practice, wearable systems adopt hybrid communication architectures, combining high-speed wired links for sensing with low-power wireless transmission for
external connectivity.
4. Sensor Fusion Techniques for Wearable Systems
4.1. Levels of Sensor Fusion (Data, Feature, Decision)
To address the challenges of signal dropout and sensor drift in multi-sensor wearable
platforms, a robust sensor fusion strategy is essential. Sensor fusion combines data from
heterogeneous sensor arrays to produce more accurate, reliable, and comprehensive information than any single sensor can provide alone. The choice of fusion algorithm is critical
and represents a trade-off between estimation accuracy and the computational demands
placed on the embedded system. This review considers two primary fusion strategies: the
complementary filter and the Extended Kalman Filter (EKF) [32].
Sensor fusion can be performed at different abstraction levels, commonly categorized
as data-level, feature-level, and decision-level fusion. Data-level fusion combines raw
sensor measurements and typically provides high accuracy but requires precise synchronization and increased computational resources. Feature-level fusion operates on extracted
features, reducing data dimensionality while preserving essential information. Decisionlevel fusion integrates outputs from independent processing modules and offers robustness
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 10 of 29
at the expense of reduced granularity. The choice of fusion level significantly impacts
computational load, latency, and suitability for embedded wearable platforms.
4.2. Complementary and Heuristic Filters
The complementary filter is a frequency-domain filtering technique that offers a
computationally efficient method for sensor fusion, making it highly suitable for realtime applications with significant power constraints. It operates by combining two or
more sensor measurements of the same physical quantity. For instance, in orientation
tracking, it fuses the high-frequency data from a gyroscope (which is reliable for short-term
rotational changes but prone to drift) with the low-frequency data from an accelerometer
and magnetometer (which are stable over the long term but noisy). The filter applies a highpass filter to the gyroscope data and a low-pass filter to the accelerometer/magnetometer
data, effectively “complementing” each other to produce a stable and accurate orientation
estimate. Its simplicity and low overhead make it an excellent choice for foundational
fusion tasks [3,32].
Figure 2 illustrates the basic structure of a complementary filter used in orientation
estimation.
(a) (b) 
Figure 2. Diagrams for the complementary filter, illustrating the operational principles of this sensor
fusion technique tailored for resource-constrained wearable devices. (a) Nonlinear complementary
filter flowchart [32] (b) Complementary filter structure [32]. Captions emphasize real-time orientation
estimation for wearable applications.
4.3. Kalman-Based Fusion Methods
For applications demanding higher accuracy and the ability to integrate a wider array
of sensor inputs, the EKF provides a more sophisticated, model-based approach. EKF is
an optimal state estimator for nonlinear systems. It operates in a two-step predict-update
cycle [33]:
1. Prediction: The filter predicts the system’s next state based on a predefined motion
model.
2. Update: It corrects the predicted state using the actual measurements from the sensors,
weighing the correction based on the relative uncertainty of the prediction and the
measurement [34].
EKF can seamlessly fuse data from multiple sources (e.g., accelerometers, gyroscopes,
magnetometers, and even physiological sensors) to estimate a single, coherent state vector.
While more computationally intensive than a complementary filter, its key advantages
include superior accuracy, robustness to noise, and the ability to provide an estimate of
its own uncertainty. This makes it indispensable for complex tasks such as precise motion
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 11 of 29
tracking and navigation in GPS-denied environments while achieving high-accuracy data
processing [3,34,35].
Figure 3 illustrates the modular framework for fusing multi-sensor odometry within a
robotic navigation system. The diagram is structured into four primary components that
collectively enable robust and continuous state estimation.
Figure 3. Mobile robot state estimation pipeline, showing how sensor fusion integrates multiple
inputs to improve motion tracking accuracy, relevant for wearable system algorithms.
On the left, Input Features are categorized into three types: Visual Feature Quality
Metrics (e.g., key point count and reprojection error), Motion Parameters (e.g., linear and
angular velocities) and Wheel Velocity Data. These inputs provide the raw observables
required for motion inference.
The center of the diagram presents the Estimation Core, which employs an Error-State
Kalman Filter (ESKF). This core operates through a cyclic Prediction–Observation process
that facilitates Continuous State Refinement, ensuring that incremental errors are corrected
in real time.
On the right, Odometry Sources are listed, including Inertial Orientation (from an
IMU), Wheel-Based Motion (from encoders), and Visual Frame Alignment (from a camera).
These sources are fused to produce a cohesive motion estimate.
Finally, the bottom section outlines the Process Flow, which follows a sequential
loop: Initialize → Predict → Observe → Correct → Reset. This flow emphasizes the
recursive nature of the filter, where each iteration reduces uncertainty and enhances
localization accuracy.
Together, this figure clarifies how heterogeneous sensor data is integrated within
an error-state formulation to achieve precise and reliable mobile robot pose estimation,
balancing accuracy with computational efficiency in dynamic environments.
A comparative analysis of the reviewed sensor fusion techniques reveals clear tradeoffs between computational cost, energy consumption, and estimation accuracy. Kalmanfilter-based methods offer the highest accuracy and robust performance under nonlinear
dynamics but require higher processing power and memory, which can limit adoption
in low-power or resource-constrained wearable devices. Complementary and heuristic
filters provide lower accuracy but demonstrate superior real-time responsiveness and
energy efficiency, making them more suitable for low-power wearable systems. Cascaded
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 12 of 29
or hybrid methods provide intermediate solutions, balancing accuracy, responsiveness and
energy use.
Table 5 compares sensor fusion methods in terms of computational cost, maturity,
key strengths, limitations and typical applications. The analysis shows that Kalman-filterbased methods are highly mature and widely used in industry-grade systems but present
adoption barriers due to computational and energy demands. Complementary filters are
also highly mature for low-power applications, with fewer integration challenges, while
cascaded and hybrid methods are moderately mature, often requiring empirical tuning and
careful calibration.
Table 5. Comparative analysis of sensor fusion methods.
Fusion Method Computational
Cost Maturity Level Key Strength TypicalApplications Main Limitation
Linear
Complementary
Filter
Low High (widely
deployed)
Low computational
overhead and minimal
power consumption,
simple
implementation
Basic orientation
tracking, excellent
for low-power
wearables
Limited accuracy
in highly dynamic
or nonlinear
motion
Cascaded
CF ([32]) Medium Medium
Improved drift
compensation without
heavy computation
Robust attitude
estimation in
wearables/robots,
good for mid-range
devices
Requires empirical
tuning, limited
adaptivity
Extended Kalman
Filter High High(industry-grade)
High accuracy,
uncertainty modeling,
sensor redundancy
handling
Navigation, motion
capture, GPS-denied
environments,
suitable for high-end
wearables
High
computational
complexity and
increased power
consumption
This critical comparison highlights practical deployment considerations, including
hardware constraints, power budgets, and system scalability, and identifies research gaps:
the development of adaptive or hybrid fusion techniques that combine high accuracy
with low computational cost, and standardized benchmarks for evaluating trade-offs in
wearable sensor fusion.
4.4. Comparative Analysis and Deployment Suitability
From an embedded deployment perspective, a comparative evaluation of fusion techniques reveals that no single approach is universally optimal for wearable applications.
Complementary filters are computationally efficient and robust, making them suitable
for low-power, real-time systems. In contrast, Kalman-based methods provide higher
estimation accuracy but require greater computational resources and careful tuning. Deployment suitability therefore depends on application-specific requirements, including
accuracy, power budget, and system complexity.
When operating independently, each sensor in the wearable array demonstrated characteristic vulnerabilities that limit its effectiveness for robust, real-time applications. For
instance, accelerometers are excellent for tracking dynamic movements but are susceptible
to gravitational and motion-related noise, which can corrupt the data. Gyroscopes provide
stable orientation information but suffer from inherent drift over time, leading to accumulating errors in continuous monitoring scenarios. Similarly, magnetometers are useful
for absolute heading but are easily distorted by nearby metallic objects or magnetic fields,
making them unreliable in many real-world environments [36–38].
In contrast, the fused data stream, which combines inputs from these heterogeneous
sensors using an EKF, improves estimation accuracy and robustness. The analysis shows
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 13 of 29
that the fusion algorithm effectively compensates for the weaknesses of individual sensors. For example, the gyroscope’s short-term stability is leveraged to counteract the
accelerometer’s noise, while the accelerometer and magnetometer data are used to correct
the gyroscope’s long-term drift [32,35,39,40].
This synergistic relationship results in a data stream that is not only more accurate than
any single sensor output but also more robust to the challenges of real-world deployment.
The fused data provides a stable and accurate representation of the user’s state, essential
for physiological monitoring and motion tracking applications where erroneous data could
lead to incorrect assessments or alerts. The enhanced performance of the fused data stream
is a clear testament to the advantages of implementing intelligent sensor fusion algorithms
within the embedded software of wearable devices [41–44].
Figures 4 and 5 present two complementary filtering architectures for sensor fusion
and orientation estimation within the wearable monitoring system.
Figure 4. Visual–inertial fusion pipeline highlighting the integration of IMU and camera measurements for wearable orientation estimation and improved motion tracking accuracy.
Figure 5. Quaternion-based orientation estimation with complementary filtering [32], demonstrating
real-time computation suitable for low-power wearable devices.
Together, these figures contrast the EKF’s rigorous, high-accuracy state estimation
with the complementary filter’s lightweight, efficient orientation tracking, clarifying the
design rationale for selecting each method based on application-specific requirements in
real-time health and motion monitoring.
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 14 of 29
Table 6 compares four commonly used sensor fusion algorithms in embedded realtime applications, highlighting trade-offs between computational complexity, accuracy, and
robustness to sensor noise.
Table 6. State-of-the-art table of different algorithm types.
Algorithm Type Pros Cons Typical Error
1. EKF (a + g + m)
Long-term drift correction;
widely used, balance of
accuracy/compute
Nonlinear model; requires
tuning Jacobians ~2–4◦ orientation
2. Complementary
filter + bias
Computationally efficient,
robust
Less flexible to complex
dynamics <3–4◦ peak error
3. UKF/SR-UKF Better nonlinear handling,
more accuracy
Higher compute requirement Slightly better accuracy
4. Particle filter (PF) Handles non-Gaussian
noise well Highest computational cost Comparable
EKFs provide high accuracy and long-term drift correction but require careful tuning of
model parameters and higher computational resources, making them moderately suitable
for real-time embedded implementations. Complementary filters are computationally
efficient and robust to transient sensor disturbances, offering excellent suitability for lowpower, real-time wearable systems, albeit with slightly lower accuracy. Unscented Kalman
filters (UKF/SR-UKF) improve nonlinear handling and accuracy at the cost of increased
computational load, while particle filters offer strong noise rejection and robustness in
non-Gaussian scenarios but impose the highest computational requirements.
This analysis illustrates that lightweight, model-based techniques (EKF, complementary filter) dominate current wearable implementations due to their balance of accuracy,
robustness, and real-time viability. At the same time, more advanced methods, including UKF and particle filters, present opportunities for future development as embedded
hardware continues to improve.
These figures illustrate two distinct sensor fusion frameworks for state estimation in
navigation and tracking systems.
Figure 6 presents an Underwater Navigation Sensor Fusion architecture, which integrates data from primary sensors, including an Inertial Measurement Unit, acoustic
positioning, velocity measurement and depth sensing, to perform error-state estimation
and multi-sensor fusion. The processing pipeline transforms raw sensor inputs into corrected position and attitude estimates along with associated error bounds, emphasizing robustness in challenging environments where traditional positioning systems may
be unreliable.
Figure 7 outlines a Sequential State Estimation process structured around a recursive
predict–update cycle. The workflow begins with initialization of state and uncertainty,
proceeds through a prediction phase based on motion modeling, and culminates in an
update phase where multi-sensor measurements are integrated to refine the state estimate.
The depicted sensor suite, including inertial, wheel-based, visual, and distance sensors,
supports a versatile fusion strategy applicable to ground and aerial robotic platforms.
Together, these figures demonstrate complementary fusion methodologies: one tailored for underwater navigation with explicit error-state correction, and another designed
for general sequential estimation with phased prediction and update operations. Both
highlight the importance of structured sensor integration in achieving accurate, reliable
pose estimation across diverse operational domains.
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 15 of 29
Figure 6. Underwater navigation sensor fusion, illustrating multi-sensor integration principles
applicable to complex embedded wearable systems.
Figure 7. Sequential state estimation workflow, showing initialization, prediction, and update phases
relevant for wearable sensor fusion algorithms.
Table 7 summarizes representative sensor fusion approaches reported in the literature,
highlighting the diversity of fusion methods, sensor combinations, and application domains
in wearable and embedded systems. The selected studies illustrate how different fusion
strategies—ranging from generic multi-sensor integration to Kalman and particle filtering
techniques—are employed to address challenges such as sensor noise, motion artifacts, and
unreliable measurements.
A clear trend emerges toward probabilistic and model-based fusion methods, such
as Extended Kalman Filters and particle filters, which provide robustness and improved
estimation accuracy when sensor models and noise characteristics are well understood. At
the same time, simpler fusion schemes remain attractive for wearable applications due to
their lower computational requirements and ease of real-time implementation.
This comparative perspective demonstrates that current wearable systems balance
robustness and accuracy against computational complexity, reinforcing the continued
relevance of lightweight fusion techniques while highlighting opportunities for future
work on adaptive and hybrid fusion strategies.
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 16 of 29
Table 7. Representative sensor fusion methods used in wearable and embedded applications.
Reference Fusion Method Sensor Set Key Benefits
A Review on Multisensor
Data Fusion for Wearable
Health Monitoring [3]
Generic multi-sensor
fusion
accelerometer, gyroscope,
magnetometer, physiological
sensors
Robustness to sensor faults,
compensates unreliable
input
Extended Kalman Filter for
Real-Time Indoor
Localization by Fusing WiFi
and Smartphone Inertial
Sensors [40]
EKF fusion gyroscope + accelometer +
magnetometer + Wi-Fi RSSI
Corrects drift, high
orientation and positional
accuracy
Robust Extended Kalman
Filtering for Systems with
Measurement Outliers [45]
EKF variant IMU data with outlier
detection
Enhanced robustness to
disturbances and sensor
anomalies
Particle Filtering and Sensor
Fusion for Robust Heart Rate
Monitoring Using Wearable
Sensors [46]
Particle filter + fusion PPG + IMU motion data
Excellent noise rejection,
reliable heart-rate
estimation
Multimodal Fusion for
Robust Respiratory Rate
Estimation in Wearable
Sensing [47]
Sequential fusion respiratory + motion sensors
Smooth output stream,
reduced noise for clean
physiological features
This comparison indicates that fusion method selection in wearables is driven less
by theoretical optimality and more by embedded feasibility, power budget, and realtime determinism.
5. Embedded Software Architectures for Wearables
5.1. Bare-Metal Architectures
The choice of the underlying software architecture is a critical design decision that
directly impacts a wearable system’s ability to meet real-time, low-power, and scalability
requirements. In bare-metal architectures, firmware executes directly on the microcontroller
hardware without the support of a commercial or open-source operating system. This
approach offers minimal memory footprint and very low processor overhead, making it
attractive for ultra-low-power and resource-constrained wearable devices [48,49].
However, implementing complex multi-sensor systems in a bare-metal environment
presents significant challenges. Concurrency is typically managed using a super-loop
structure combined with interrupt service routines, which can become difficult to maintain
as system complexity increases. Ensuring precise timing, deterministic behavior, and
reliable synchronization across multiple heterogeneous sensor data streams requires careful
manual design and extensive testing. As a result, bare-metal implementations often suffer
from limited scalability and increased risk of timing inconsistencies that are unacceptable
in real-time monitoring applications [48–50].
5.2. RTOS-Based Architectures
To address the limitations of bare-metal designs, many multi-sensor wearable systems
adopt a Real-Time Operating System (RTOS) as their software foundation. An RTOS is
a lightweight operating system that provides essential services for developing complex
real-time embedded applications, including task scheduling, inter-task communication,
and power management support [29,49].
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 17 of 29
A key advantage of RTOS-based architectures is the availability of a preemptive,
priority-based scheduler, which allows system functionality to be decomposed into independent tasks. Separate tasks can be dedicated to sensor data acquisition, sensor fusion,
power management, and wireless communication, ensuring that time-critical operations
meet strict real-time deadlines. In addition, RTOSs provide synchronization and communication mechanisms such as semaphores, mutexes, and message queues, which are essential
for safely sharing data and synchronizing events among concurrent tasks in multi-sensor
fusion systems [29,48,49,51].
The task-based nature of RTOSs also promotes modularity and scalability, enabling
additional sensors or system features to be incorporated with minimal redesign. Furthermore, modern RTOSs often include hooks for power management, such as tickless idle
modes, allowing the system to enter low-power states when tasks are inactive, an essential
capability for extending battery life in wearable devices [29].
Figure 8 presents a three-tiered system architecture commonly employed in embedded
and wearable monitoring systems. The model is organized hierarchically into User Level,
System Level, and Hardware Level, each representing a distinct functional layer.
Figure 8. System architecture layers, detailing user, system, and hardware levels to clarify modular
design considerations in multi-sensor wearable systems.
The User Level encompasses Applications and Software, which define system functionality and user interaction. This layer is supported by the System Level, responsible
for Resource Management, including Task Coordination, Memory Allocation, and Device
Control. The lowest tier, the Hardware Level, comprises Physical Components such as Processing Units, Storage Devices, and Peripheral Interfaces, which execute the computational
and I/O operations.
This layered approach promotes modularity, scalability, and maintainability, enabling
efficient management of system resources and seamless integration of additional sensors or
software modules, key requirements for wearable and embedded systems.
5.3. Comparative Analysis and Long-Term Deployment Implications
Table 8 presents a comparative evaluation of bare-metal and RTOS-based architectures.
Bare-metal implementations minimize memory usage and overhead but are limited in
scalability, maintainability, and real-time task management, which can constrain adoption in
multi-sensor wearable systems. RTOS-based designs provide deterministic task scheduling,
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 18 of 29
modular expansion, and improved fault isolation, supporting more complex deployments,
but introduce additional complexity and slightly higher power consumption.
Table 8. Comparative evaluation of bare-metal and RTOS-based architectures.
Aspect Bare-Metal Super-Loop RTOS-Based Framework
Memory footprint Minimal (<2 KB) Small but larger (2–10 KB)
Task ordering Manual loop or interrupts Preemptive, priority-based scheduler
Real-time guarantees Manual timing, non-deterministic Deterministic scheduling
Concurrency handling ISR-heavy, complex scaling Native task synchronization
Modularity Code entangled High modularity via tasks
Scalability Poor beyond few sensors High, modular task expansion
Power management Sleep in loop, custom code Integrated (tickless idle, sleep hooks)
Maintainability Degrades rapidly with complexity High for long-term development
Overall suitability Prototyping, simple devices Recommended for deployable
multi-sensor wearables
In terms of maturity, bare-metal architectures are highly mature for simple prototypes, while RTOS-based frameworks are widely deployed and considered mature for
multi-sensor wearable applications. Cascaded or hybrid RTOS-lightweight approaches
remain moderately mature, often requiring careful configuration and tuning for resourceconstrained devices.
This analysis highlights practical deployment considerations: RTOS-based architectures are generally preferred for systems requiring extensibility, maintainability, and reliable
real-time performance. However, adoption barriers include the need for developer expertise, careful memory management, and system integration effort.
Research gaps include developing lightweight RTOS frameworks optimized for ultralow-power wearable devices, establishing standardized benchmarks for comparing architectural trade-offs, and creating guidelines for seamless migration from bare-metal to RTOS
platforms in energy-constrained environments.
6. Power Management and Energy Harvesting in Wearables
6.1. Low-Power Design and Scheduling Techniques
Low-power operation in wearable multi-sensor systems is primarily achieved through
software-level optimizations rather than hardware modifications. Common strategies
include duty cycling of sensors and peripherals, adaptive sampling based on activity
or signal dynamics, and the use of low-power operating modes supported by modern
microcontrollers. By selectively disabling inactive components and reducing sampling
rates during periods of low relevance, these techniques significantly reduce average power
consumption while preserving essential sensing performance.
Task scheduling also plays a critical role in energy efficiency. Event-driven and prioritybased scheduling allow time-critical sensing and fusion tasks to execute deterministically,
while non-critical processing is deferred or executed at lower frequencies. In RTOS-based
systems, tickless kernels and power-aware schedulers further minimize idle power consumption by allowing the processor to remain in sleep states for extended periods.
6.2. Energy-Harvesting Sources and Architectures
Energy harvesting and power-autonomous wearables represent an important research
direction aimed at mitigating battery limitations that constrain current wearable systems. By
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 19 of 29
capturing energy from the user or the surrounding environment, harvesting techniques can
extend operational lifetime and reduce charging frequency, although fully self-sustaining
operation remains challenging in practice.
In wearable systems, harvesting mechanisms are constrained by low available power
densities, intermittent energy availability, and strict form-factor requirements. As a result,
practical designs focus on harvesting sources that can be seamlessly integrated into bodyworn platforms while maintaining user comfort. Future research must also address material
biocompatibility, long-term durability and mechanical robustness to enable everyday use.
Mechanical energy harvesting, primarily based on piezoelectric and triboelectric
generators, exploits human motion such as walking, joint movement, or body vibrations.
Piezoelectric harvesters commonly employ materials such as lead zirconate titanate (PZT)
or flexible polymers like polyvinylidene fluoride (PVDF). While PZT offers higher energy
density, PVDF-based harvesters are more suitable for wearables due to their flexibility,
durability, and biocompatibility. Architecturally, these harvesters are typically implemented
as cantilever beams, stacked layers, or flexible patches integrated into footwear, straps,
or textiles. However, their output is highly dependent on user activity patterns, making
harvested power unpredictable.
Thermoelectric energy harvesting leverages the temperature gradient between human skin and the ambient environment using thermoelectric generators (TEGs). Wearable TEGs commonly rely on bismuth telluride (Bi2Te3)-based materials optimized for
low-temperature gradients. Although TEGs provide continuous energy generation independent of motion, the limited temperature difference in wearable scenarios restricts
achievable power levels to the microwatt range. System architectures often combine
TEGs with ultra-low-power DC–DC converters and energy buffers to compensate for low
voltage output.
Photovoltaic energy harvesting uses ambient or solar light through thin-film or flexible
photovoltaic cells. Amorphous silicon and organic photovoltaic materials are frequently
employed due to their flexibility and acceptable performance under indoor lighting conditions. While photovoltaic harvesting can deliver comparatively higher power densities in
outdoor environments, its effectiveness is strongly influenced by lighting conditions and
user behavior, limiting its reliability as a sole power source.
From an architectural perspective, most wearable systems adopt hybrid harvesting
configurations, combining multiple energy sources (e.g., motion and thermal) with a
primary battery. These architectures typically incorporate an energy management unit
responsible for rectification, voltage regulation, maximum power point tracking (MPPT),
and controlled energy storage.
A major component of power-autonomous wearables is intelligent energy management. Even with energy harvesting, available power is limited and fluctuating. Reported
approaches rely on adaptive duty cycling and energy-aware task scheduling to allocate
limited power resources efficiently. For example, high-power sensing or processing tasks
could be delayed until energy reserves are sufficient, while critical alerts are always prioritized [26]. Coordinating energy harvesting, low-power hardware, and adaptive software is
therefore essential to ensure continuous, efficient and reliable wearable operation.
In conclusion, energy harvesting offers a promising complement to conventional
battery-powered wearable systems, particularly when combined with intelligent energy
management and energy-aware algorithms. However, current harvesting technologies remain insufficient to support continuous multi-sensor operation without careful system-level
optimization, highlighting the need for further advances in materials, hybrid harvesting
strategies, and integrated hardware–software co-design [52].
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 20 of 29
6.3. Coordination of Multiple Energy Sources
Coordinating multiple energy sources in wearable systems introduces significant
system-level challenges that extend beyond hardware design. Hybrid power architectures
typically combine a rechargeable battery with one or more energy harvesting modules,
requiring intelligent control strategies to ensure stable and uninterrupted operation.
At the hardware level, power-path management circuits are employed to dynamically
select between harvested energy and battery power based on availability and load demand.
These circuits often include priority-based switching, voltage threshold detection, and energy buffering using supercapacitors or secondary micro-batteries. Such buffering mitigates
the intermittent nature of harvested energy but increases system size and complexity.
From a software perspective, energy-aware task scheduling plays a critical role. Embedded software can adapt sensing, processing, and communication workloads based on
current energy availability. For example, high-power operations such as wireless transmission or complex sensor fusion may be deferred when harvested energy is insufficient, while
low-power monitoring tasks remain active. This coordination requires tight integration
between the power management subsystem and the RTOS scheduler.
Despite promising experimental demonstrations, most multi-source energy coordination strategies remain at a research or prototype stage. Challenges include accurate energy
prediction, overhead introduced by control algorithms, and ensuring real-time guarantees
under fluctuating power conditions. Consequently, while hybrid energy architectures can
significantly extend device lifetime, their widespread adoption in commercial wearable
systems is still limited.
Overall, effective coordination of multiple energy sources requires a co-design approach, integrating harvesting hardware, power electronics, and adaptive embedded
software. Advancements in ultra-low-power control circuits and lightweight energy-aware
algorithms are essential to transition these architectures from laboratory prototypes to
reliable, real-world wearable deployments.
6.4. Practical Trade-Offs and Maturity Considerations
From a technology maturity standpoint, many power optimization techniques are
well established and commercially deployed, whereas energy-harvesting solutions remain
at an experimental or supplementary stage for most wearable applications. To address
the critical challenge of limited battery life in wearable devices, several software-based
power optimization strategies need to be considered. These techniques are designed to
minimize energy consumption without compromising the system’s real-time monitoring
capabilities. The power management strategy is deeply integrated with the RTOS and the
overall software architecture [23,29,48].
The primary power-saving technique is interrupt-driven processing combined with
processor sleep modes. Instead of continuously polling sensors for new data, the microcontroller is placed in a low-power sleep mode whenever possible. The RTOS automatically
manages this transition when no tasks are ready to run. The processor only wakes up in
response to hardware interrupts, such as a “data ready” signal from a sensor or a timer
event. This approach ensures that the CPU consumes significant power only when actively
processing data, drastically reducing the average power consumption [24,29,48].
Furthermore, the system employs intelligent peripheral and clock management:
• Dynamic frequency scaling: The microcontroller’s clock speed is adjusted based on
the current computational demand. During intensive processing, such as running the
fusion algorithm, the clock speed is maximized for performance. During periods of
lower activity, the clock speed is reduced to save power [25–27,29,52–55].
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 21 of 29
• Peripheral gating: The software selectively powers down communication peripherals
like SPI, I2C, and the BLE radio when they are not in active use. For instance, the BLE
module is kept in a low-power state between transmissions, and sensor communication
buses are only enabled when data is being actively sampled [29,53,56,57].
Finally, the RTOS task scheduler itself is leveraged for power efficiency. By carefully prioritizing tasks and scheduling data processing in batches rather than continuous
streams, the system maximizes the amount of time the processor can remain in a deep
sleep state. This minimizes the energy overhead associated with frequently waking and
sleeping the CPU, contributing directly to the goal of an efficient and low-power wearable
system [23,29,48,56].
Table 9 synthesizes prior studies on power optimization in embedded wearable systems, focusing on widely adopted techniques such as dynamic voltage and frequency
scaling (DVFS), peripheral shutdown, duty cycling, and low-power wireless communication strategies. Each entry summarizes the application domain, core techniques, and
key contributions, providing a structured comparison across software, hardware, and
system-level approaches.
Table 9. Comparative overview of power management techniques for embedded wearable systems.
Technique/Approach System Level Key Idea Advantages Limitations Technology
Maturity
Tickless RTOS Idle [29] Software (RTOS)
Suppresses
periodic OS ticks
during idle periods
Significant
reduction in idle
power
consumption, easy
RTOS integration
Limited benefit
under high task
activity
High
(commercially
deployed)
Duty Cycling [57] Software/System
Periodic activation/deactivation
of sensors and
peripherals
Simple to
implement,
effective for
low-duty
workloads
Can increase
latency and reduce
responsiveness
High
Dynamic Voltage and
Frequency Scaling
(DVFS/DVS) [53,54]
Hardware/Software
Adjusts CPU
voltage and
frequency based
on workload
Large energy
savings under
variable load
Requires hardware
support and
careful timing
analysis
Medium–High
Peripheral Power
Gating [55,56]
Hardware/Software
Shuts down
unused
peripherals and
buses
Reduces leakage
and dynamic
power
Reinitialization
overhead High
Energy-Aware Task
Scheduling Software (RTOS)
Schedules tasks
based on energy
constraints
Improves
system-wide
efficiency
Increased
scheduler
complexity
Medium
Event-Driven
Processing System
Activates
processing only on
relevant events
Minimizes
unnecessary
computation
Not suitable for
continuous sensing Medium
Energy Harvesting
Integration [52]
System wearables
Uses ambient
energy (motion,
thermal, solar)
Extends
operational
lifetime
Intermittent and
unpredictable
energy
Low–Medium
(experimental)
Multi-Source Power
Coordination System
Combines battery
and harvested
energy sources
Improved
resilience and
autonomy
Complex control
logic
Low (research
stage)
The comparison highlights that software-centric techniques, including tickless RTOS
operation, energy-aware task scheduling, and duty cycling, are highly mature and widely
deployed in commercial wearable devices, offering predictable energy savings and straighthttps://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 22 of 29
forward integration. In contrast, more aggressive approaches that combine adaptive
scheduling with energy harvesting remain experimental, with adoption barriers including
integration complexity, intermittent energy availability, and the need for sophisticated
control algorithms.
From a deployment perspective, this synthesis reveals a gap between laboratorydemonstrated power optimization methods and solutions suitable for reliable, large-scale
wearable deployment. While mature techniques are routinely integrated into current
platforms, emerging strategies require further validation to ensure robustness, predictability,
and long-term operational reliability.
Research gaps include developing energy management strategies that combine high
efficiency with low computational overhead, integrating multiple asynchronous energy
sources seamlessly, and establishing standardized evaluation benchmarks for comparing
power optimization techniques in multi-sensor wearable systems.
7. Practical Challenges, Gaps and Deployment Considerations
The findings from this study highlight a significant performance gap between data
streams from individual sensors and those processed through the sensor fusion framework.
This section will analyze these differences, focusing on the practical implications for realtime monitoring in wearable devices.
7.1. Manufacturing and Scalability Challenges
Manufacturing and scalability present significant challenges for wearable sensor fusion systems. Component variability, calibration requirements, and production tolerances
can affect system performance at scale. Furthermore, cost constraints often limit the adoption of advanced sensors or processing units, requiring trade-offs between performance
and affordability.
7.2. Reliability, Calibration and Long-Term Operation
Transitioning from a theoretical model to a functional wearable system requires addressing practical challenges. A framework will be better designed with these real-world
deployment aspects in mind, specifically focusing on hardware constraints, scalability, and
processing performance.
• Hardware constraints: A significant challenge in designing wearable devices is the
trade-off between functionality and the physical limitations of the hardware. The
primary constraint is managing power consumption to ensure reasonable battery life.
Typical embedded software architectures reported in the literature are designed with
an emphasis on low-power operation, utilizing efficient data buffering and poweraware processing techniques to meet the strict energy budgets of embedded systems.
This ensures that the device can perform continuous real-time monitoring without
frequent recharging, a critical factor for user adoption [58].
• Scalability to more sensors: Such frameworks were explicitly designed for modular
scalability. Software architecture allows for the straightforward integration of additional sensors without requiring a complete system overhaul. This is achieved through
a modular data acquisition and processing pipeline that can accommodate new data
streams with minimal overhead. This flexibility is a key advantage, as it allows the
platform to be adapted for more complex future applications, such as integrating
environmental sensors alongside physiological ones [30,59,60].
• Latency and throughput in embedded processing: For the system to be effective in
real-time monitoring, both latency and data throughput must be optimized. Reported
case studies in the literature, which involved physiological monitoring and motion
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 23 of 29
tracking, indicate that the system meets the demanding real-time processing demands
of these applications. The embedded software’s real-time data acquisition, buffering,
and synchronization mechanisms are efficient enough to process data from the entire
sensor array with minimal delay. This ensures that the system’s outputs are timely and
accurately reflect the user’s current state, which is crucial for applications requiring
immediate feedback or intervention [61].
Figure 9 illustrates the data flow and stakeholder communication system within the
wearable health monitoring platform. The architecture is structured around three core
nodes: the wearable device, which collects physiological and motion data via a local connection; the mobile device, which acts as a gateway for data aggregation and preliminary
processing before transmitting it over a network connection; and the cloud platform, which
provides secure storage, advanced analytics, and long-term trend analysis. Authorized
stakeholders, including medical practitioners, clinical researchers, and designated caregivers, access the processed data through secure interfaces, enabling remote monitoring,
clinical decision support, and personalized feedback. This integrated ecosystem supports
continuous health tracking while ensuring data privacy and scalable accessibility.
Figure 9. Wearable health monitoring ecosystem, highlighting the interaction of sensors, processing
units, and communication interfaces for real-world deployment.
Table 10 compares representative wearable health monitoring systems across key
embedded-system dimensions, including sensor coverage, power constraints, latency and
throughput requirements, scalability, and communication and computing architectures. The
comparison illustrates how earlier body area network-based solutions have progressively
evolved toward edge- and on-device processing paradigms to meet increasingly stringent
real-time and energy efficiency demands.
The analysis highlights that modular scalability and low-latency processing are common design goals across contemporary systems, while effective power management remains a central challenge. RTOS-based architectures and edge computing approaches
emerge as practical enablers for balancing real-time performance and energy efficiency,
reinforcing their suitability for real-world, long-duration wearable deployments.
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 24 of 29
Table 10. Comparative overview of wearable health-monitoring systems and their embedded
system constraints.
System Sensor Coverage Power Constrains Latency and
Throughput Scalability
Communication/
Compute
Architecture
Pantelopoulos &
Bourbakis (2010) [59]
Multiple
physiological
sensors (ECG,
SpO2)
High battery
efficiency,
low–power focus
Real-time vital
sign detection but
limited throughput
benchmarks
Modular wearable
prototypes
Early body area
network, simple
wireless
Remote Health
Monitoring for
Elderly (2023) [30]
Bio-sensors,
environmental,
actigraphy
Fog-enabled to
reduce power and
latency
Latency-sensitive
via edge/fog—
~140 ms sensing-toactuation latency
Easily extensible
gateway-based
systems
IoT-edge-cloud
layered
architecture
Adaptive Extreme
Edge Computing
(2021) [58]
Neuromorphic
sensor fusion
capabilities
Ultra-low power,
memristive/CMS
architectures
Designed for
minimal latency,
low footprint
Supports adaptive,
incremental sensor
additions
On-device edge
compute, minimal
offloading
7.3. User Experience, Privacy and Security
Sensor fusion techniques play a central role in embedded real-time wearable systems, balancing accuracy, computational load, and responsiveness. Each method presents
inherent trade-offs that affect system performance, robustness, and suitability for resourceconstrained platforms. Table 11 provides a comparative overview of commonly used fusion
techniques, highlighting these trade-offs and their implications for wearable deployment.
Table 11. Comparative overview of sensor fusion techniques for embedded real-time applications.
Method Accuracy Computation Real-Time
Viability Robustness EmbeddedSuitability
1. EKF High (modeldependent) Moderate–High Possibly
constrained
Sensitive to
model/data Moderate
2. Complementary
Filter Moderate Low Real-time viable Robust butless accurate Excellent
3. Deep Learning/
LSTM
Very high in
complex dynamic
environments
Very High
Poor for
real-time
embedded
Good
adaptability
Limited
embedded
readiness
Table 11 compares widely used sensor fusion techniques for embedded real-time
applications across key criteria, including accuracy, computational complexity, real-time
viability, robustness, and suitability for resource-constrained platforms. The comparison
highlights the inherent trade-offs between estimation accuracy and computational demand,
which are central to embedded system design.
This comparative analysis underscores why lightweight model-based fusion techniques dominate current wearable deployments.
The future of wearable embedded systems relies heavily on user-centered design
(UCD) and human factor integration. While technical performance, such as sensor accuracy, communication reliability, and power efficiency, is essential, long-term adoption
depends on usability, comfort, and user engagement. Incorporating systematic user feedback, ergonomic evaluation, and adaptive interfaces can ensure wearables meet functional
requirements while enhancing satisfaction, compliance, and trust in daily life. Intelligent
adaptation can further enhance comfort, usability, and engagement over time [2,62].
In conclusion, user-centered design and human factor integration are critical for
wearable embedded systems. By prioritizing ergonomics, adaptive feedback, accessibility
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 25 of 29
and AI-driven personalization, wearables can achieve higher adoption, sustained use
and meaningful impact across healthcare, fitness, industrial and everyday applications.
Technical performance alone is insufficient for successful deployment without parallel
attention to usability, privacy, and long-term user acceptance [58].
8. Comparative Synthesis of the Literature
This section synthesizes the reviewed literature from a system-level perspective, comparing sensor fusion techniques, software architectures, communication protocols and
power management strategies. Rather than evaluating individual technologies in isolation,
it highlights cross-cutting trade-offs, maturity levels and deployment constraints, providing
guidance for researchers and practitioners designing embedded wearable systems.
Wearable embedded systems face challenges in interoperability due to proprietary
protocols, heterogeneous data formats, and diverse application interfaces. Middleware
platforms, standardized APIs, and common data schemas provide abstraction layers that
enable consistent data interpretation, cross-platform analytics, and device-agnostic applications. Integration with edge and cloud infrastructures allows for distributed computation and real-time analytics while maintaining compatibility across devices. Security
and privacy frameworks, including standardized encryption, authentication, and access
control, are essential to ensure data protection and trustworthiness in multi-vendor environments [21,56,59,61,63].
Semantic interoperability, ontology-based data models, and modular architectures
support consistent interpretation of sensor data, enable plug-and-play devices, and allow
for scalable integration into large IoT ecosystems. Compliance with standards ensures
reliability and trustworthiness, particularly in regulated industries such as healthcare and
industrial monitoring [59,61,63].
In conclusion, standardization and interoperability are pivotal for wearable embedded
systems. Across the literature, trade-offs between computational complexity, energy efficiency, real-time performance, and usability are evident. Establishing common middleware,
APIs, semantic models, and security frameworks supports multi-device collaboration,
efficient data exchange, and scalable deployment. Persistent gaps include the need for
standardized benchmarking, long-term reliability evaluation, and integrated optimization
of energy, accuracy, and usability, providing guidance for researchers and practitioners
designing future embedded wearable systems.
9. Conclusions and Future Research Directions
Successful wearable sensor fusion solutions require careful balancing of accuracy,
power consumption and system complexity. Lightweight fusion algorithms, RTOS-based
software architectures and mature communication protocols collectively support reliable
and scalable deployments, while integration feasibility and long-term maintainability
remain critical considerations.
9.1. Key Takeaways for System Designers
Effective embedded software development for wearable devices hinges on integrating
robust RTOS architectures, carefully selected sensor fusion algorithms, and efficient power
management. Future directions point toward on-device intelligence, leveraging adaptive
algorithms and lightweight machine learning models to enable real-time analytics without
compromising battery life. Co-optimizing computational performance, energy efficiency,
and user-centric design is essential for transitioning wearables from passive data loggers to
proactive, reliable tools across healthcare, industrial, and daily life applications.
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 26 of 29
9.2. Key Open Research Challenges and Future Directions
This section summarizes key future research directions in embedded software for
multi-sensor wearable devices. It discusses key challenges and representative directions related to issues such as Hardware-in-the-Loop testing, on-device machine learning and edge
intelligence, adaptive sensor fusion architectures, energy harvesting and power autonomy,
enhanced wireless communication and security, standardization and interoperability, and
user-centered design and human factor integration.
Hardware-in-the-Loop (HIL) testing and real-world validation provide a critical
methodology for evaluating wearable embedded systems. HIL integrates physical sensors, microcontrollers, and communication modules with simulated user or environmental
conditions, enabling assessment of latency, synchronization, and fault tolerance. This
approach ensures that algorithms, software architectures, and adaptive fusion strategies
are robust, reliable, and ready for deployment across healthcare, sports, and industrial
applications [17,39,64].
On-device machine learning and edge intelligence are critical for enabling real-time
activity recognition, anomaly detection, and context-aware adaptive decision-making.
Lightweight ML models, optimized for embedded platforms using techniques like quantization or pruning, allow for local inference that reduces latency, preserves privacy, and
supports energy-efficient operation. These methods facilitate personalized and adaptive
wearables capable of interpreting and responding to user-specific physiological or activity
patterns [24,43,51].
Adaptive sensor fusion architectures dynamically balance computational load, energy
consumption, and accuracy by adjusting processing strategies based on sensor reliability,
user activity, and environmental context. Event-driven processing and machine-learningassisted fusion optimize resource usage while maintaining high-fidelity monitoring. These
architectures also support distributed multi-node fusion for coordinated wearable networks,
enhancing system robustness and scalability [26,32,45,58,60,65,66].
Collectively, future research should focus on HIL validation, on-device ML, adaptive
sensor fusion, energy harvesting, wireless communication optimization, standardization,
interoperability, and user-centered design. Addressing these areas will enable wearable embedded systems that are reliable, energy-efficient, context-aware, and capable of providing
actionable insights in real-world applications.
Funding: This research received no external funding.
Data Availability Statement: Data are contained within the article.
Conflicts of Interest: The authors declare no conflict of interest.
References
1. Haghi, M.; Thurow, K.; Stoll, R. Wearable Devices in Medical Internet of Things: Scientific Research and Commercially Available
Devices. Healthc. Inform. Res. 2017, 23, 4–15. [CrossRef] [PubMed] [PubMed Central]
2. Adeghe, E.P.; Okolo, C.A.; Ojeyinka, O.T. A review of wearable technology in healthcare: Monitoring patient health and enhancing
outcomes. Open Access Res. J. Multidiscip. Stud. 2024, 7, 142–148. [CrossRef]
3. Gravina, R.; Alinia, P.; Ghasemzadeh, H.; Fortino, G. Multi-sensor fusion in body sensor networks: State-of-the-art and research
challenges. Inf. Fusion 2017, 35, 68–80. [CrossRef]
4. Seneviratne, S.; Hu, Y.; Nguyen, T.; Lan, G.; Khalifa, S.; Thilakarathna, K.; Hassan, M.; Seneviratne, A. A Survey of Wearable
Devices and Challenges. IEEE Commun. Surv. Tutor. 2017, 19, 2573–2620. [CrossRef]
5. Khan, Y.; Ostfeld, A.E.; Lochner, C.M.; Pierre, A.; Arias, A.C. Monitoring of Vital Signs with Flexible and Wearable Medical
Devices. Adv. Mater. 2016, 28, 4373–4395. [CrossRef] [PubMed]
6. King, R.C.; Villeneuve, E.; White, R.J.; Sherratt, R.S.; Holderbaum, W.; Harwin, W.S. Application of data fusion techniques and
technologies for wearable health monitoring. Med. Eng. Phys. 2017, 42, 1–12. [CrossRef] [PubMed]
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 27 of 29
7. Shcherbina, A.; Mattsson, C.M.; Waggott, D.; Salisbury, H.; Christle, J.W.; Hastie, T.; Wheeler, M.T.; Ashley, E.A. Accuracy in
Wrist-Worn, Sensor-Based Measurements of Heart Rate and Energy Expenditure in a Diverse Cohort. J. Pers. Med. 2017, 7, 3.
[CrossRef]
8. Stisen, A.; Blunck, H.; Bhattacharya, S.; Prentow, T.S.; Kjærgaard, M.B.; Dey, A.; Sonne, T.; Jensen, M.M. Smart Devices are Different:
Assessing and MitigatingMobile Sensing Heterogeneities for Activity Recognition. In Proceedings of the 13th ACM Conference on
Embedded Networked Sensor Systems (SenSys ‘15), Seoul, Republic of Korea, 1–4 November 2015; Association for Computing Machinery:
New York, NY, USA, 2015; pp. 127–140. [CrossRef]
9. Atallah, L.; Lo, B.; King, R.; Yang, G.-Z. Sensor Positioning for Activity Recognition Using Wearable Accelerometers. IEEE Trans.
Biomed. Circuits Syst. 2011, 5, 320–329. [CrossRef]
10. Liu, S.; Gao, R.X.; Freedson, P.S. Computational methods for estimating energy expenditure in human physical activities. Med.
Sci. Sports Exerc. 2012, 44, 2138–2146. [CrossRef] [PubMed] [PubMed Central]
11. Bicocchi, N.; Mamei, M.; Zambonelli, F. Detecting activities from body-worn accelerometers via instance-based algorithms.
Pervasive Mob. Comput. 2010, 6, 482–495. [CrossRef]
12. Parkka, J.; Ermes, M.; Korpipaa, P.; Mantyjarvi, J.; Peltola, J.; Korhonen, I. Activity classification using realistic data from wearable
sensors. IEEE Trans. Inf. Technol. Biomed. 2006, 10, 119–128. [CrossRef] [PubMed]
13. Laplante, P.A.; Ovaska, S.J. Real-Time Systems Design and Analysis: Tools for the Practitioner, 4th ed.; John Wiley & Sons: Hoboken,
NJ, USA, 2012; pp. 79–82, 109–110.
14. Cooling, J. Real-Time Operating Systems: Book 1—The Theory; Lindentree Associates: Burford, UK, 2017; pp. 37–75, 280–285.
15. White, E. Making Embedded Systems: Design Patterns for Great Software; O’Reilly Media: Sebastopol, CA, USA, 2011; pp. 176–182.
16. Hasan, K.F.; Wang, C.; Feng, Y.; Tian, Y.-C. Time synchronization in vehicular ad-hoc networks: A survey on theory and practice.
Veh. Commun. 2018, 14, 39–51. [CrossRef]
17. Schöpping, T.; Kenneweg, S.; Hesse, M.; Rückert, U. µRT: A lightweight real-time middleware with integrated validation of
timing constraints. Front. Robot. AI 2023, 10, 1081875. [CrossRef]
18. Leens, F. An introduction to I2C and SPI protocols. IEEE Instrum. Meas. Mag. 2009, 12, 8–13. [CrossRef]
19. Liao, C.-W.; Yu, H.-C.; Liao, Y.-C. Verification of SPI Protocol Using Universal Verification Methodology for Modern IoT and
Wearable Devices. Electronics 2025, 14, 837. [CrossRef]
20. Kher, R.K.; Patel, D.M. A comprehensive review on wearable health monitoring systems. Open Biomed. Eng. J. 2021, 15, 213–225.
[CrossRef]
21. Baiense, J.; Zdravevski, E.; Coelho, P.; Pires, I.M.; Velez, F.J. Driving Healthcare Monitoring with IoT and Wearable Devices: A
Systematic Review. ACM Comput. Surv. 2025, 57, 294. [CrossRef]
22. Koulouras, G.; Katsoulis, S.; Zantalis, F. Evolution of Bluetooth Technology: BLE in the IoT Ecosystem. Sensors 2025, 25, 996.
[CrossRef] [PubMed]
23. Villa, M.; Casilari, E. Wearable Fall Detectors Based on Low Power Transmission Systems: A Systematic Review. Technologies 2024,
12, 166. [CrossRef]
24. Ghasemzadeh, H.; Amini, N.; Saeedi, R.; Sarrafzadeh, M. Power-aware computing in wearable sensor networks: An optimal
architecture design. IEEE Trans. Mob. Comput. 2015, 14, 800–812. [CrossRef]
25. Gao, M.; Yao, Y.; Wang, Y.; Wang, B.; Wang, P.; Wang, Y.; Dai, J.; Liu, S.; Torres, J.F.; Cheng, W.; et al. Wearable power management
system enables uninterrupted battery-free data-intensive sensing and transmission. Nano Energy 2023, 107, 108107. [CrossRef]
26. Majumder, S.; Mondal, T.; Deen, M.J. Wearable Sensors for Remote Health Monitoring. Sensors 2017, 17, 130. [CrossRef]
27. Shaikh, F.K.; Zeadally, S. Energy harvesting in wireless sensor networks and internet of things: A review. Renew. Sustain. Energy
Rev. 2016, 55, 1041–1054. [CrossRef]
28. Luna, R.; Islam, S.A. Security and Reliability of Safety-Critical RTOS. SN Comput. Sci. 2021, 2, 356. [CrossRef]
29. Rault, T.; Bouabdallah, A.; Challal, Y. Energy Efficiency in Wireless Sensor Networks: A Top-Down Survey. Comput. Netw. 2014,
67, 104–122. [CrossRef]
30. Ahmed, S.; Irfan, S.; Kiran, N.; Masood, N.; Anjum, N.; Ramzan, N. Remote Health Monitoring Systems for Elderly People: A
Survey. Sensors 2023, 23, 7095. [CrossRef]
31. Luo, R.C.; Yih, C.-C.; Su, K.L. Multisensor fusion and integration: Approaches, applications, and future research directions. IEEE
Sens. J. 2002, 2, 107–119. [CrossRef]
32. Narkhede, P.; Poddar, S.; Walambe, R.; Ghinea, G.; Kotecha, K. Cascaded Complementary Filter Architecture for Sensor Fusion in
Attitude Estimation. Sensors 2021, 21, 1937. [CrossRef] [PubMed]
33. Feng, S.; Li, X.; Zhang, S.; Jian, Z.; Duan, H.; Wang, Z. A review: State estimation based on hybrid models of Kalman filter and
neural network. Syst. Sci. Control Eng. 2023, 11, 2173682. [CrossRef]
34. Kok, M.; Hol, J.D.; Schön, T.B. Using Inertial Sensors for Position and Orientation Estimation. Found. Trends Signal Process. 2017,
11, 1–153. [CrossRef]
35. Hall, D.L.; Llinas, J. An introduction to multisensor data fusion. Proc. IEEE 1997, 85, 6–23. [CrossRef]
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 28 of 29
36. García-de-Villa, S.; Casillas-Pérez, D.; Jiménez-Martín, A.; García-Domínguez, J.J. Inertial sensors for human motion analysis: A
comprehensive review. IEEE Trans. Instrum. Meas. 2023, 72, 4006439. [CrossRef]
37. Kok, M.; Schön, T.B. A fast and robust algorithm for orientation estimation using inertial sensors. IEEE Signal Process. Lett. 2019,
26, 1533–1537. [CrossRef]
38. Kok, M.; Schön, T.B. Magnetometer calibration using inertial sensors. IEEE Sens. J. 2016, 16, 5679–5689. [CrossRef]
39. Nazarahari, M.; Rouhani, H. Sensor fusion algorithms for orientation tracking via magnetic and inertial measurement units: An
experimental comparison survey. Inf. Fusion 2021, 76, 8–23. [CrossRef]
40. Deng, Z.-A.; Hu, Y.; Yu, J.; Na, Z. Extended Kalman Filter for Real Time Indoor Localization by Fusing WiFi and Smartphone
Inertial Sensors. Micromachines 2015, 6, 523–543. [CrossRef]
41. Sreelekshmy, I.; Resmi, R. A review on real time MEMS sensor fusion. Int. Res. J. Eng. Technol. (IRJET) 2020, 7, 21–23.
42. Chen, H.; Schall, M.C.; Fethke, N.B. Measuring upper arm elevation using an inertial measurement unit: An exploration of sensor
fusion algorithms and gyroscope models. Appl. Ergon. 2020, 89, 103187. [CrossRef]
43. Azarbeik, M.M.; Razavi, H.; Merat, K.; Salarieh, H. Augmenting inertial motion capture with SLAM using EKF and SRUKF data
fusion algorithms. Measurement 2023, 222, 113690. [CrossRef]
44. Poulose, A.; Kim, J.; Han, D.S. A Sensor Fusion Framework for Indoor Localization Using Smartphone Sensors and Wi-Fi RSSI
Measurements. Appl. Sci. 2019, 9, 4379. [CrossRef]
45. Fang, H.; Haile, M.A.; Wang, Y. Robust extended Kalman filtering for systems with measurement outliers. IEEE Control Syst. Lett.
2021, 30, 795–802. [CrossRef]
46. Nathan, V.; Jafari, R. Particle filtering and sensor fusion for robust heart rate monitoring using wearable sensors. IEEE J. Biomed.
Health Inform. 2018, 22, 1834–1846. [CrossRef]
47. John, A.; Wang, H.; Cardiff, B.; Parhi, K.K.; John, D. Multimodal fusion for robust respiratory rate estimation in wearable sensing.
Inf. Fusion 2025, 123, 103253. [CrossRef]
48. Guan, W.; Wang, J.; Wang, Y. Design of an Embedded System for Wearable Physiological Monitoring. IEEE Access 2016, 4,
3940–3950.
49. Zalizovskyi, M.; Huzynets, N. Comparative analysis between real-time operating systems and supercycles. Electron. Inf. Technol.
2024, 26, 33–45. [CrossRef]
50. Labrosse, J.J. MicroC/OS-II: The Real-Time Kernel, 2nd ed.; CRC Press: Boca Raton, FL, USA, 2002; pp. 35–45.
51. Banbury, C.; Zhou, C.; Fedorov, I.; Matas, R.; Thakker, U.; Gope, D.; Janapa Reddi, V.; Mattina, M.; Whatmough, P. MicroNets:
Neural Network Architectures for Deploying TinyML Applications on Commodity Microcontrollers. In Proceedings of the
Machine Learning and Systems (MLSys), Virtual, 5–9 April 2021; Volume 3, pp. 517–532.
52. Maioli, A.; Quinones, K.A.; Ahmed, S.; Alizai, M.H.; Mottola, L. Dynamic Voltage and Frequency Scaling for Intermittent
Computing. ACM Trans. Sens. Netw. 2025, 21, 16. [CrossRef]
53. Zidar, J.; Mati´c, T.; Aleksi, I.; Hocenski, Ž. Dynamic Voltage and Frequency Scaling as a Method for Reducing Energy Consumption
in Ultra-Low-Power Embedded Systems. Electronics 2024, 13, 826. [CrossRef]
54. Pillai, P.; Shin, K.G. Real-time dynamic voltage scaling for low-power embedded operating systems. In Proceedings of the Eighteenth
ACM Symposium on Operating Systems Principles (SOSP ‘01), Banff, AL, Canada, 21–24 October 2001; Association for Computing
Machinery: New York, NY, USA, 2001; pp. 89–102. [CrossRef]
55. Mittal, S. A survey of techniques for improving energy efficiency in embedded computing systems. Int. J. Comput. Aided Eng.
Technol. 2014, 6, 440–459. [CrossRef]
56. Dias, D.; Cunha, J.P.S. Wearable Health Devices—Vital Signs Monitoring, Systems and Technologies. Sensors 2018, 18, 2414.
[CrossRef]
57. Vafeas, A.; Biswas, M.I.; Fafoutis, X.; Elsts, A.; Craddock, I.; Piechocki, R.; Oikonomou, G. Wearable devices for digital health: The
SPHERE Wearable 3. In Proceedings of the International Conference on Embedded Wireless Systems and Networks (EWSN 2020), Lyon,
France, 17–18 February 2020; Junction Publishing: Junction, TX, USA, 2020; pp. 236–241.
58. Covi, E.; Donati, E.; Liang, X.; Kappel, D.; Heidari, H.; Payvand, M.; Wang, W. Adaptive extreme edge computing for wearable
devices. Front. Neurosci. 2021, 15, 611300. [CrossRef] [PubMed]
59. Pantelopoulos, A.; Bourbakis, N.G. A survey on wearable sensor-based systems for health monitoring and prognosis. IEEE Trans.
Syst. Man Cybern.—Part C Appl. Rev. 2010, 40, 1–12. [CrossRef]
60. Pinheiro, G.P.M.; Miranda, R.K.; Praciano, B.J.G.; Santos, G.A.; Mendonça, F.L.L.; Javidi, E.; da Costa, J.P.J.; de Sousa, R.T., Jr.
Multi-sensor wearable health device framework for real-time monitoring of elderly patients using a mobile application and
high-resolution parameter estimation. Front. Hum. Neurosci. 2022, 15, 750591. [CrossRef]
61. Perez, A.J.; Zeadally, S. Recent Advances in Wearable Sensing Technologies. Sensors 2021, 21, 6828. [CrossRef]
62. Irfan, M.; Dalai, S.; Trslic, P.; Riordan, J.; Dooly, G. LSAF-LSTM-Based Self-Adaptive Multi-Sensor Fusion for Robust UAV State
Estimation in Challenging Environments. Machines 2025, 13, 130. [CrossRef]
https://doi.org/10.3390/electronics15020295
Electronics 2026, 15, 295 29 of 29
63. Erhan, L.; Ndubuaku, M.; Di Mauro, M.; Song, W.; Chen, M.; Fortino, G.; Bagdasar, O.; Liotta, A. Smart anomaly detection in
sensor systems: A multi-perspective review. Inf. Fusion 2021, 67, 64–79. [CrossRef]
64. Valade, A.; Acco, P.; Grabolosa, P.; Fourniols, J.-Y. A Study about Kalman Filters Applied to Embedded Sensors. Sensors 2017,
17, 2810. [CrossRef] [PubMed]
65. Wang, J.; Chen, Y.; Hao, S.; Peng, X.; Hu, L. Deep learning for sensor-based activity recognition: A survey. Pattern Recognit. Lett.
2019, 119, 3–11. [CrossRef]
66. Shaukat, N.; Ali, A.; Javed Iqbal, M.; Moinuddin, M.; Otero, P. Multi-Sensor Fusion for Underwater Vehicle Localization by
Augmentation of RBF Neural Network and Error-State Kalman Filter. Sensors 2021, 21, 1149. [CrossRef]
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
https://doi.org/10.3390/electronics15020295