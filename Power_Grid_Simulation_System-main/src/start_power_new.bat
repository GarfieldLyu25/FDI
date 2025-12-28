@echo off

start C:\Users\Administrator\.conda\envs\powersystem\python.exe PhysicalWorldEmu\PowerGridPWRun.py
timeout /t 2 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe plcCtrl\plcSimulatorPwr.py
timeout /t 2 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe rtuCtrl\rtuSimulatorPower.py
timeout /t 2 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe powerlink\PowerLinkRun.py
timeout /t 2 >nul
start C:\Users\Administrator\.conda\envs\powersystem\python.exe ScadaHMI\ScadaHMIRun.py


echo 所有组件已启动
pause