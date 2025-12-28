#!/bin/bash

PYTHON="/home/xf/miniconda3/envs/powersystem/bin/python"

$PYTHON PhysicalWorldEmu/PowerGridPWRun.py &
$PYTHON plcCtrl/plcSimulatorPwr.py &
$PYTHON rtuCtrl/rtuSimulatorPower.py &
$PYTHON powerlink/PowerLinkRun.py &
$PYTHON ScadaHMI/ScadaHMIRun.py &

echo "所有组件已启动"
echo "按回车键退出..."
read
