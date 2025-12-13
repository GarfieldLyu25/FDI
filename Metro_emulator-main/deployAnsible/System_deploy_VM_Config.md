### Railway-system real-world emulator

**VM-Instance-Type**: m7g.2xlarge

**OS :** Microsoft windows 10/11 home

**Display mode**:

- Display output: Yes
- Display resolution: 1920 x 1080
- Display orientation: Landscape

**Software/Lib needed:** 

- python >= 3.7.4
- python-lib: wxpython >= 4.1.0

**VM Deploy Config:** 

- NIC number: 1
- RDP: enable
- NIC 1: IP address: 10.0.10.100, gateway: 10.0.10.1

**Program Deploy Config:** 

(clone lib and program code and double run the executable file)

- Github Library base:  `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/lib`
- Github Code base: `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/metroEmuUI`
- Executable file: `runMetroEmuUI_win.bat`



### Trains-System Control PLCs set

**VM-Instance-Type**: m1.medium

**OS :** ubuntu 20.04 server

**Display mode**:

- Display output: No

**Software/Lib needed:** 

- python >= 3.7.4
- python-lib: pyModbusTCP==0.2.0

**VM Deploy Config:** 

- NIC number: 2
- SSH: enable
- NIC 1: IP address: 10.0.10.13, gateway: 10.0.10.1
- NIC 2: IP address: 192.168.100.13, gateway: 192.168.100.1

**Program Deploy Config:** 

(clone lib and program code and double run the executable file)

- Github Library base:  `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/lib`
- Github Code base: `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/plcCtrl/trainPlcEmu`
- Executable file: `runTrainPlcCtrlEmu.bat`



### Stations-System Control PLCs set

**VM-Instance-Type**: m1.medium

**OS :** ubuntu 20.04 server

**Display mode**:

- Display output: No

**Software/Lib needed:** 

- python >= 3.7.4
- python-lib: pyModbusTCP==0.2.0

**VM Deploy Config:** 

- NIC number: 2
- SSH: enable
- NIC 1: IP address: 10.0.10.12, gateway: 10.0.10.1
- NIC 2: IP address: 192.168.100.12, gateway: 192.168.100.1

**Program Deploy Config:** 

(clone lib and program code and double run the executable file)

- Github Library base:  `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/lib`
- Github Code base: `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/plcCtrl/stationPlcEmu`
- Executable file: `runStationPlcCtrlEmu_win.bat`



### Signals-System Control PLCs set

**VM-Instance-Type**: m1.medium

**OS :** ubuntu 20.04 server

**Display mode**:

- Display output: No

**Software/Lib needed:** 

- python >= 3.7.4
- python-lib: pyModbusTCP==0.2.0

**VM Deploy Config:** 

- NIC number: 2
- SSH: enable
- NIC 1: IP address: 10.0.10.11, gateway: 10.0.10.1
- NIC 2: IP address: 192.168.100.11, gateway: 192.168.100.1

**Program Deploy Config:** 

(clone lib and program code and double run the executable file)

- Github Library base:  `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/lib`
- Github Code base: `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/plcCtrl/signalPlcEmu`
- Executable file: `runSignalPlcCtrlEmu_win.bat`



### Scada-HMI-System[master] emulator

**VM-Instance-Type**: m7g.2xlarge

**OS :** Microsoft windows 10/11 home

**Display mode**:

- Display output: Yes
- Display resolution: 1920 x 1080
- Display orientation: Landscape

**Software/Lib needed:** 

- python >= 3.7.4
- python-lib: wxpython >= 4.1.0

**VM Deploy Config:** 

- NIC number: 2
- RDP: enable
- NIC 1: IP address: 192.168.100.100, gateway: 192.168.100.1
- NIC 2: IP address: 192.168.11.100, gateway: 192.168.11.1

**Program Deploy Config:** 

(clone lib and program code and double run the executable file)

- Github Library base:  `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/lib`
- Github Code base: `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/scadaEmuUI`
- Executable file: `runHmiEmuUI_win.bat`



### Scada-HMI-System[slave] emulator

**VM-Instance-Type**: m7g.2xlarge

**OS :** Microsoft windows 10/11 home

**Display mode**:

- Display output: Yes
- Display resolution: 1920 x 1080
- Display orientation: Landscape

**Software/Lib needed:** 

- python >= 3.7.4
- python-lib: wxpython >= 4.1.0

**VM Deploy Config:** 

- NIC number: 1
- RDP: enable
- NIC 1: IP address: 192.168.11.101, gateway: 192.168.11.1

**Program Deploy Config:** 

(clone lib and program code and double run the executable file)

- Github Library base:  `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/lib`
- Github Code base: `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/scadaEmuUI`
- Executable file: `runHmiEmuUI_win.bat`



### Trains Controller HMI emulator

**VM-Instance-Type**: m7g.2xlarge

**OS :** Microsoft windows 10/11 home

**Display mode**:

- Display output: Yes
- Display resolution: 1920 x 1080
- Display orientation: Landscape

**Software/Lib needed:** 

- python >= 3.7.4
- python-lib: wxpython >= 4.1.0

**VM Deploy Config:** 

- NIC number: 1
- RDP: enable
- NIC 1: IP address: 192.168.100.15, gateway: 192.168.100.1

**Program Deploy Config:** 

(clone lib and program code and double run the executable file)

- Github Library base:  `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/lib`
- Github Code base: `https://github.com/LiuYuancheng/Metro_emulator/tree/main/src/scadaEmuUI`
- Executable file: `runHmiEmuUI_win.bat`