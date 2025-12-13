#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcSimulatorStation.py
#
# Purpose:     A simple plc simulation module to connect and control the real-world 
#              emulator via UDP (to simulate the eletrical signals change) and handle
#              SCADA system Modbus TCP request.
#              - This module will simulate 3 PLCs connected under master-slave mode
#               
# Author:      Yuancheng Liu
#
# Created:     2023/05/29
# Version:     v0.1.2
# Copyright:   Copyright (c) 2023 Singapore National Cybersecurity R&D Lab LiuYuancheng
# License:     MIT License   
#-----------------------------------------------------------------------------
""" 
    Program design:
        We want to create a PLC simulator which can simulate a PLC set (Master[slot-0], 
        Slave[slot-1], Slave[slot-2]) with thress 16-in 8-out PLCs. The PLC sets will
        take 22 input signal and provide 22 output signal to implement the railway station
        control system.
"""

from collections import OrderedDict

import plcSimGlobalStation as gv
import modbusTcpCom
import plcSimulator

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class directConnLadderLogic(modbusTcpCom.ladderLogic):
    """ A direct connection ladder logic diagram set, holding registers will 
        trigger the connected coils.
    """
    def __init__(self, parent, ladderName) -> None:
        super().__init__(parent, ladderName=ladderName)

    def initLadderInfo(self):
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 22
        self.srcCoilsInfo['address'] = None
        self.srcCoilsInfo['offset'] = None
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 22
        # For total 22 holding registers connected addresses
        # address: 0 - 9: weline stations
        # address: 10 - 15: nsline stations
        # address: 16 - 21: ccline sensors.

#-----------------------------------------------------------------------------
    def runLadderLogic(self, regsList, coilList=None):
        coilsRsl = []
        if len(regsList) != 22:
            gv.gDebugPrint('runLadderLogic(): input not valid', logType=gv.LOG_WARN)
            gv.gDebugPrint("Input registers list: %s" %str(regsList))
        else:
            # direct connection copy the register state to coil directly:
            coilsRsl = list(regsList).copy()
        gv.gDebugPrint('Finished calculate all coils: %s' %str(coilsRsl), logType=gv.LOG_INFO)
        return coilsRsl
        
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class stationPlcSet(plcSimulator.plcSimuInterface):
    """ A PlC simulator to provide below functions: 
        - Create a modbus service running in subthread to handle the SCADA system's 
            modbus requirment.
        - Connect to the real world emulator to fetch the sensor state and calculate 
            the output coils state based on the ladder logic. 
        - Send the signal setup request to the real world emulator to change the signal.
    """
    def __init__(self, parent, plcID, addressInfoDict, ladderObj, updateInt=0.6):
        super().__init__(parent, plcID, addressInfoDict, ladderObj, 
                         updateInt=updateInt)

    def _initInputState(self):
        self.regsAddrs = (0, 22)
        self.regSRWfetchKey = 'stations'
        self.regs2RWmap = OrderedDict()
        self.regs2RWmap['weline'] = (0, 10)
        self.regs2RWmap['nsline'] = (10, 16)
        self.regs2RWmap['ccline'] = (16, 22)
        self.regsStateRW = OrderedDict()
        self.regsStateRW['weline'] = [0]*10
        self.regsStateRW['nsline'] = [0]*6
        self.regsStateRW['ccline'] = [0]*6

    def _initCoilState(self):
        self.coilsAddrs = (0, 22)
        self.coilsRWSetKey = 'stations'
        self.coils2RWMap = OrderedDict()
        self.coils2RWMap['weline'] = (0, 10)
        self.coils2RWMap['nsline'] = (10, 16)
        self.coils2RWMap['ccline'] = (16, 22)
        self.coilStateRW = OrderedDict()
        self.coilStateRW['weline']  = [False]*10
        self.coilStateRW['nsline']  = [False]*6 
        self.coilStateRW['ccline']  = [False]*6 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    gv.gDebugPrint("Start Init the PLC: %s" %str(gv.PLC_NAME), logType=gv.LOG_INFO)
    gv.iLadderLogic = directConnLadderLogic(None, ladderName='Direct_connection')
    addressInfoDict = {
        'hostaddress': gv.gModBusIP,
        'realworld':gv.gRealWorldIP, 
        'allowread':gv.ALLOW_R_L,
        'allowwrite': gv.ALLOW_W_L
    }
    plc = stationPlcSet(None, gv.PLC_NAME, addressInfoDict,
                        gv.iLadderLogic, updateInt=gv.gInterval)
    plc.run()

if __name__ == "__main__":
    main()
