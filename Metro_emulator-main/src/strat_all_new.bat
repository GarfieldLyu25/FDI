@echo off
start C:\Users\Administrator\.conda\envs\powersystem\python.exe metroEmuUI\MetroEmuRun.py
timeout /t 3 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe plcCtrl\signalPlcEmu\plcSimulatorSignal.py
timeout /t 3 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe plcCtrl\stationPlcEmu\plcSimulatorStation.py
timeout /t 3 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe plcCtrl\trainPlcEmu\plcSimulatorTrain.py
timeout /t 3 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe rtuCtrl\trainRtuEmu\rtuSimulatorTrain.py
timeout /t 3 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe trainCtrlUI\trainCtrlRun.py
timeout /t 3 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe scadaEmuUI\hmiEmuRun.py
pause