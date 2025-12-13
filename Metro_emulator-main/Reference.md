# Technique Reference 

The project "Railway IT/OT System Cyber Security Test Platform" aims to simplify and simulate key features of real-world railway control chains. This document provides an overview of the technique references utilized in designing the OT environment for our railway system, encompassing track cross sensor-signal PLC control, station sensor-signal PLC control, railway track PLC and RTU control, as well as train PLC and RTU control.

The design of the railway OT network is inspired by a model railway system emulation project detailed at https://www.nepaview.com/model-train-plc-project.html. For the real world railway system using the similar design logic, our project follows the Mitsubishi electric's railway infrastructure solution for the London underground. 

**Table of Contents**

[TOC]

------



#### Real-World Railway System Reference

The real-world application of PLC and RTU systems for monitoring and controlling railway infrastructure is exemplified by the Mitsubishi's railway infrastructure solution for the London Underground. We refer to the public document "RAIL infrastructure solution for rai industry processes" 's managing rail industry processes section, signaling section and asset monitoring section.

- Doc link: https://eu-assets.contentstack.com/v3/assets/blt5412ff9af9aef77f/blt97226dbd57cabfd7/61723538fc41b20dc51813d2/ad4e90f7-5d02-11e5-a60e-b8ac6f83a177_Mits_Railway_Brochure_UK_Final.pdf
- Doc file: `reference_00_Mits_Railway_Brochure_UK_Final.pdf`



#### Project Main Idea Reference

The foundational concept stems from the railway simulation module of this project: 

- Project link: https://www.nepaview.com/model-train-plc-project.html



#### Railway Track Signal PLC Control Reference

For railway PLC control, insights were gathered from the research paper titled "Automation of Railway Signaling Using PLC and SCADA" by Dr. N.G.P IT ICRADAIS 2K16 (March 24, 2016). 

- Paper link: https://www.researchgate.net/publication/336588607_EC001_Automation_of_Railway_Signaling_Using_Plc_and_Scada?enrichId=rgreq-4e13f6263d5e6231c831baf8126adba8-XXX&enrichSource=Y292ZXJQYWdlOzMzNjU4ODYwNztBUzo4MTQ2NDQ3NTkzNzU4NzNAMTU3MTIzNzg1NDM4MA%3D%3D&el=1_x_2&_esc=publicationCoverPdf
- PFD doc: `reference_01_AUTOMATIONOFRAILWAYSIGNALINGUSINGPLCANDSCADA.pdf`



#### Railway Sensor and Signal Automated Control Reference [PLC]

For the railway tracks cross junction automatic control, we refer to the same design logic of the railway gate crossing area control in this document "Automatic Railway Gate Crossing Control Using PLC"

- Doc link: https://www.irjet.net/archives/V7/i6/IRJET-V7I6593.pdf
- Doc : `reference_02_IRJET-V7I6593.pdf`

For the railway track and station sensor-signal automatic control logic, we use the similar logic introduced in the paper "PLC Based Fully Automated Railway System" ISSN: 2395-1621

- Paper link: https://www.ierjournal.org/pupload/mdinfotech/PLC%20Based%20Automation.pdf
- Doc: `reference_03_PLC Based Automation.pdf`

For the railway tracks cross junction section design in our system, we followed the same design of track-road-cross signal control  in paper "Development of an Automated Railway Level Crossing Gate Control System using PLC"

- Paper link: https://ieomsociety.org/ieom2019/papers/795.pdf
- Doc file: `reference_04_ieom2019_papers_795.pdf`



#### Railway and Trains Automated Monitoring Reference  [RTU] 

The document titled "Remote Terminal Unit (RTU) over Internet Protocol (IP) for Railway" offers insights of the design of railway and train monitoring RTU design.

- Article link: https://www.meidensha.com/rd/rd_02/rd_02_02/rd_02_02_01/rd_02_02_01_01/pdf/article-201203-0009.pdf

- Doc file: `reference_05_article-201203-0009.pdf`

  





