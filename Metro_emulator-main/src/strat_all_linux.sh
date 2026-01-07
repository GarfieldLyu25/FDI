#!/bin/bash

PYTHON="/home/xf/miniconda3/envs/powersystem/bin/python"

wait_udp_listen() {
	local port="$1"
	local retries="${2:-100}"
	local i=0
	while (( i < retries )); do
		if ss -lunp 2>/dev/null | grep -q ":${port}\\b"; then
			return 0
		fi
		sleep 0.1
		((i++))
	done
	return 1
}

wait_tcp_listen() {
	local port="$1"
	local retries="${2:-200}"
	local i=0
	while (( i < retries )); do
		if ss -lntp 2>/dev/null | grep -q ":${port}\\b"; then
			return 0
		fi
		sleep 0.1
		((i++))
	done
	return 1
}

set -m

echo "[1/4] Starting MetroEmu (real-world emulator UI)..."
$PYTHON metroEmuUI/MetroEmuRun.py &

echo "[2/4] Waiting for MetroEmu UDP/3002..."
wait_udp_listen 3002 150 || echo "Warning: MetroEmu UDP/3002 not detected yet; continuing."

echo "[3/4] Starting PLCs + RTU..."
$PYTHON plcCtrl/signalPlcEmu/plcSimulatorSignal.py &
$PYTHON plcCtrl/stationPlcEmu/plcSimulatorStation.py &
$PYTHON plcCtrl/trainPlcEmu/plcSimulatorTrain.py &
$PYTHON rtuCtrl/trainRtuEmu/rtuSimulatorTrain.py &

echo "Waiting for PLC Modbus ports (2502/2503/2504) and RTU S7 (2102)..."
wait_tcp_listen 2502 200 || echo "Warning: PLC 2502 not detected yet."
wait_tcp_listen 2503 200 || echo "Warning: PLC 2503 not detected yet."
wait_tcp_listen 2504 200 || echo "Warning: PLC 2504 not detected yet."
wait_tcp_listen 2102 200 || echo "Warning: RTU 2102 not detected yet."

echo "[4/4] Starting TrainCtrl + SCADA HMI..."
$PYTHON trainCtrlUI/trainCtrlRun.py &
$PYTHON scadaEmuUI/hmiEmuRun.py &

echo "地铁模拟系统所有组件已启动"
echo "按回车键退出..."
read
