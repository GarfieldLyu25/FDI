#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcSignalSimulator.py
#
# Purpose:     A simple plc simulation module to connect and control the real-world 
#              emulator via UDP (to simulate the eletrical signals change) and handle
#              SCADA system Modbus TCP request.
#              This module will simulate the sensors-signals-auto-control system. 
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
    take 39 input signal and provide 19 output signal.
"""
from collections import OrderedDict

import plcSimGlobalSignal as gv
import modbusTcpCom
import plcSimulator

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class tFlipFlopLadderLogic(modbusTcpCom.ladderLogic):
    """ A T-flip-flop latching relay ladder logic set with 19 ladders. The ladder logic
        needs to be init and passed in the data handler (with handler auto-update flag 
        set to True).
    """

    def __init__(self, parent, ladderName) -> None:
        super().__init__(parent, ladderName=ladderName)

    def initLadderInfo(self):
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 39
        self.srcCoilsInfo['address'] = 0
        self.srcCoilsInfo['offset'] = 19
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 19
        # Init the flipflop coils and registers config:
        # For total 39 holding registers connected addresses
        # address: 0 - 17: weline sensors
        # address: 18 - 24: nsline sensors
        # address: 25 - 38: ccline sensors.
        weIdxOffSet, nsIdxOffset, ccIdxOffset = 0, 17, 25
        # init all the flip flop maping table.
        self.ffConfig = [
            # Init all the weline signals flipflop:
            {'coilIdx': 0, 'onRegIdx':(ccIdxOffset+12,), 'offRegIdx':(ccIdxOffset+13,)},
            {'coilIdx': 1, 'onRegIdx':(ccIdxOffset+12,), 'offRegIdx':(ccIdxOffset+13,)},
            {'coilIdx': 2, 'onRegIdx':(ccIdxOffset+10,), 'offRegIdx':(ccIdxOffset+11,)},
            {'coilIdx': 3, 'onRegIdx':(ccIdxOffset+10,), 'offRegIdx':(ccIdxOffset+11,)},
            {'coilIdx': 4, 'onRegIdx':(ccIdxOffset+8,), 'offRegIdx':(ccIdxOffset+9,)},
            {'coilIdx': 5, 'onRegIdx':(ccIdxOffset+8,), 'offRegIdx':(ccIdxOffset+9,)},
            {'coilIdx': 6, 'onRegIdx':(ccIdxOffset+6,), 'offRegIdx':(ccIdxOffset+7,)},
            {'coilIdx': 7, 'onRegIdx':(ccIdxOffset+6,), 'offRegIdx':(ccIdxOffset+7,)},
            # Init all the nsline signals flipflop:
            {'coilIdx': 8, 'onRegIdx':(ccIdxOffset+0,), 'offRegIdx':(ccIdxOffset+1,)},
            {'coilIdx': 9, 'onRegIdx':(ccIdxOffset+0,), 'offRegIdx':(ccIdxOffset+1,)},
            {'coilIdx': 10, 'onRegIdx':(ccIdxOffset+2,), 'offRegIdx':(ccIdxOffset+3,)},
            {'coilIdx': 11, 'onRegIdx':(ccIdxOffset+4,), 'offRegIdx':(ccIdxOffset+5,)},
            # Init all the ccline signal flipflop:
            {'coilIdx': 12, 'onRegIdx': (nsIdxOffset+0, nsIdxOffset+6), 'offRegIdx': (nsIdxOffset+1, nsIdxOffset+7)},
            {'coilIdx': 13, 'onRegIdx': (nsIdxOffset+4,), 'offRegIdx': (nsIdxOffset+5,)},
            {'coilIdx': 14, 'onRegIdx': (nsIdxOffset+2,), 'offRegIdx': (nsIdxOffset+3,)},
            {'coilIdx': 15, 'onRegIdx': (weIdxOffSet+7, weIdxOffSet+9), 'offRegIdx': (weIdxOffSet+8, weIdxOffSet+10)},
            {'coilIdx': 16, 'onRegIdx': (weIdxOffSet+5, weIdxOffSet+11), 'offRegIdx': (weIdxOffSet+6, weIdxOffSet+12)},
            {'coilIdx': 17, 'onRegIdx': (weIdxOffSet+3, weIdxOffSet+13), 'offRegIdx': (weIdxOffSet+4, weIdxOffSet+14)},
            {'coilIdx': 18, 'onRegIdx': (weIdxOffSet+1, weIdxOffSet+15), 'offRegIdx': (weIdxOffSet+2, weIdxOffSet+16)}
        ]

#-----------------------------------------------------------------------------
    def _tfligFlogRun(self, coilState, toggleOnList, toggleOffList):
        """ Function to simulate a normal t-flip-flop latching replay to take input
            and calculate the output based on the current state. If there is N register
            state changed, this ladder logic will execute N times.
            Args:
                coilState (int/bool): Current output State. 
                toggleOnList (list(int/bool)): input registers's state list which can toggle
                    the relay on.
                toggleOffList (list(int/bool)): input registers's state list which can toggle
                    the relay off.
            Returns:
                bool: the filp-flop positive output.
        """
        if coilState: 
            if 1 in toggleOffList or True in toggleOffList: return False 
        else:
            if 1 in toggleOnList or True in toggleOnList: return True
        return coilState

#-----------------------------------------------------------------------------
    def runLadderLogic(self, regsList, coilList=None):
        coilsRsl = []
        if len(regsList) != 39 or coilList is None or len(coilList)!=19:
            gv.gDebugPrint('runLadderLogic(): input not valid', logType=gv.LOG_WARN)
            gv.gDebugPrint("Input registers list: %s" %str(regsList), logType=gv.LOG_INFO)
            gv.gDebugPrint("Input coils list: %s" %str(coilList), logType=gv.LOG_INFO)
        else:
            for item in self.ffConfig:
               coilState = coilList[item['coilIdx']]
               onRegListState = [regsList[i] for i in item['onRegIdx']]
               offRegListState = [regsList[i] for i in item['offRegIdx']]
               coilsRsl.append(self._tfligFlogRun(coilState, onRegListState, offRegListState) ) 
        gv.gDebugPrint('Finished calculate all coils: %s' %str(coilsRsl), logType=gv.LOG_INFO)
        return coilsRsl
        
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class signalPlcSet(plcSimulator.plcSimuInterface):

    def __init__(self, parent, plcID, addressInfoDict, ladderObj, updateInt=0.6):
        super().__init__(parent, plcID, addressInfoDict, ladderObj, updateInt=updateInt)

    def _initInputState(self):
        self.regsAddrs = (0, 39)
        self.regSRWfetchKey = 'sensors'
        self.regs2RWmap = OrderedDict()
        self.regs2RWmap['weline'] = (0, 17)
        self.regs2RWmap['nsline'] = (17, 31)
        self.regs2RWmap['ccline'] = (31, 39)
        self.regsStateRW = OrderedDict()
        self.regsStateRW['weline'] = [0]*17
        self.regsStateRW['nsline'] = [0]*14
        self.regsStateRW['ccline'] = [0]*8

    def _initCoilState(self):
        self.coilsAddrs = (0, 19)
        self.coilsRWSetKey = 'signals'
        self.coils2RWMap = OrderedDict()
        self.coils2RWMap['weline'] = (0, 8)
        self.coils2RWMap['nsline'] = (8, 12)
        self.coils2RWMap['ccline'] = (12, 19)
        self.coilStateRW = OrderedDict()
        self.coilStateRW['weline']  = [False]*8
        self.coilStateRW['nsline']  = [False]*4 
        self.coilStateRW['ccline']  = [False]*7 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    #gv.gDebugPrint("Start Init the PLC: %s" %str(gv.PLC_NAME), logType=gv.LOG_INFO)``
    gv.iLadderLogic = tFlipFlopLadderLogic(None, ladderName='T_flipflop_logic_set')
    addressInfoDict = {
        'hostaddress': gv.gModBusIP,
        'realworld':gv.gRealWorldIP, 
        'allowread':gv.ALLOW_R_L,
        'allowwrite': gv.ALLOW_W_L
    }
    plc = signalPlcSet(None, gv.PLC_NAME, addressInfoDict,  
                       gv.iLadderLogic, updateInt=gv.gInterval)
    plc.run()

if __name__ == "__main__":
    main()