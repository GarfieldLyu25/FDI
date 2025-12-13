#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        trainDataMgr.py
#
# Purpose:     Data manager module used to control all the data processing 
#              modules and store the interprocess/result data.
#
# Author:      Yuancheng Liu
#
# Created:     2023/06/13
# Version:     v0.1.2
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License  
#-----------------------------------------------------------------------------

import time
import snap7
from collections import OrderedDict
from random import randint

import trainCtrlGlobal as gv
import modbusTcpCom
import snap7Comm
from snap7Comm import BOOL_TYPE, INT_TYPE, REAL_TYPE


# flag to identify whether the train's data will be added a slight random change 
# before show up on the UI to simulate the real-world scenario.
RANDOM_FLG = True 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class TrainAgent(object):
    """ Agent class to store a trains' information and generate the adjusted 
        random data if needed.
    """
    def __init__(self, trainID, designVoltage, dataRandFlg=True) -> None:
        """ Init example: train = TrainAgent(1, 750)
            Args:
                trainID (str): train ID
                designVoltage (int): trains operating voltage.
        """
        self.id = trainID
        self.throttleOn = 0
        self.speed = 0 
        self.vlotage = 0 
        self.current = 0
        self.designVoltage = designVoltage
        self.powerFlag = False if not gv.TEST_MD else True
        self.dataRanFlg = dataRandFlg
        self.fsensorTriggered = False

#-----------------------------------------------------------------------------
# Define all the get() function here

    def getTrainInfo(self):
        """ Return the adjusted train information dictionary. Example: 
            {
                'id': self.id,
                'speed': 0,
                'current': o,
                'voltage': self.designVoltage + randint(0,50) if self.dataRanFlg else 0,
                'power': self.powerFlag
            }
        """
        result = {
            'id': self.id,
            'speed': self.speed,
            'voltage': self.vlotage,
            'current': self.current,
            'fsensor': self.fsensorTriggered,
            'power': self.powerFlag
        }
        return result

#-----------------------------------------------------------------------------
# Define all the set function() here.
    def setThrottle(self, throttleState):
        self.throttleOn = throttleState

    def setFsensorVal(self, sensorState):
        self.fsensorTriggered = sensorState

    def setSpeed(self, speed):
        self.speed = int(speed)

    def setVoltage(self, voltage):
        self.vlotage = int(voltage)

    def setCurrent(self, current):
        self.current = int(current)
    
    def setPower(self, state):
        self.powerFlag = state

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MapManager(object):
    """ UI manager module to control all the UI components."""
    def __init__(self, parent) -> None:
        self.parent = parent
        self.trainsAgentDict = OrderedDict() # each element is a list of train agents.
        self._initTrains()
        gv.gDebugPrint("Finished init map manager: %s" %str(self.trainsAgentDict), 
                       prt=False, logType=gv.LOG_INFO)

#-----------------------------------------------------------------------------
    def _initTrain(self, trackID, trainNum, designVoltage):
        """ Init one train agent on a tracks and add them in the related trains
            agents list of <self.trainsAgentDict>
        """
        self.trainsAgentDict[trackID] = []
        for i in range(trainNum):
            trainID = '-'.join((trackID, str(i)))
            train = TrainAgent(trainID, designVoltage, dataRandFlg=RANDOM_FLG)
            self.trainsAgentDict[trackID].append(train)

#-----------------------------------------------------------------------------
    def _initTrains(self):
        # init all the weline trains
        trackID, trainNum, designVoltage = 'weline', 4, 750
        self._initTrain(trackID, trainNum, designVoltage)
        # init all the nsline trains
        trackID, trainNum, designVoltage = 'nsline', 3, 750
        self._initTrain(trackID, trainNum, designVoltage)
        # init all the ccline Trains
        trackID, trainNum, designVoltage = 'ccline', 3, 750
        self._initTrain(trackID, trainNum, designVoltage)

#-----------------------------------------------------------------------------
    def updateTrainsThrottle(self, trackID, speedList):
        if trackID in self.trainsAgentDict.keys():
            idxRange = min(len(speedList), len(self.trainsAgentDict[trackID]))
            for idx in range(idxRange):
                train = self.trainsAgentDict[trackID][idx]
                train.setThrottle(speedList[idx])

#-----------------------------------------------------------------------------
    def updateTrainsPwr(self, trackID, speedList):
        if trackID in self.trainsAgentDict.keys():
            idxRange = min(len(speedList), len(self.trainsAgentDict[trackID]))
            for idx in range(idxRange):
                train = self.trainsAgentDict[trackID][idx]
                train.setPower(speedList[idx])

    def updateTrainsSensor(self, trackID, rtuDataList):
        if trackID in self.trainsAgentDict.keys():
            for idx in range(len(rtuDataList)):
                train = self.trainsAgentDict[trackID][idx]
                dataList = rtuDataList[idx]
                # data sequence: [state['fsensor'], state['speed'], state['voltage'], state['current']]
                train.setFsensorVal(dataList[0])
                train.setSpeed(dataList[1])
                train.setVoltage(dataList[2])
                train.setCurrent(dataList[3])

#-----------------------------------------------------------------------------
    def getTrainsInfo(self, trackID):
        """ Collect data from all the train agtens in <self.trainsAgentDict> and 
            build a list of data.
        """
        result = []
        if trackID in self.trainsAgentDict.keys():
            for train in self.trainsAgentDict[trackID]:
                result.append(train.getTrainInfo())
        return result

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(object):
    """ The data manager is a module running parallel with the main thread to 
        connect to PLCs module to do the data communication with modbus TCP.
    """
    def __init__(self, parent, plcInfo) -> None:
        self.parent = parent
        self.plcClients = OrderedDict()
        self.regsDict = {}
        self.coilsDict = {}
        self.plcInfo = plcInfo
        self.plcConnectionState = {}
        for key, val in plcInfo.items():
            plcIpaddr = val['ipaddress']
            plcPort = val['port']
            self.plcClients[key] = modbusTcpCom.modbusTcpClient(plcIpaddr, tgtPort=plcPort)
            if self.plcClients[key].checkConn():
                gv.gDebugPrint('DataManager: Connected to PLC.', logType=gv.LOG_INFO)
                self.plcConnectionState[key] = True
            else:
                gv.gDebugPrint('DataManager: Failed to connect to PLC.', logType=gv.LOG_INFO)
                self.plcConnectionState[key] = False
            self.regsDict[key] = []
            self.coilsDict[key] = []
        
        # Init the RTU client
        self.rtuClient = snap7Comm.s7CommClient(gv.RTU_IP, rtuPort=gv.RTU_PORT, 
                                                snapLibPath=gv.gS7snapDllPath)
        self.rtuConnectionState = self.rtuClient.checkConn()
        self.rtuDataList = {
            'weline': [None, None, None, None],
            'nsline': [None, None, None],
            'ccline': [None, None, None],
        }
        gv.gDebugPrint('TrainsHMI dataMgr inited', logType=gv.LOG_INFO)

    #-----------------------------------------------------------------------------
    def periodic(self, now):
        """ Call back every periodic time."""
        gv.gDebugPrint('DataManager: try to get PLC information', logType=gv.LOG_INFO)
        for key, val in self.plcClients.items():
            hRegsAddr, hRegsNum = self.plcInfo[key]['hRegsInfo']
            self.regsDict[key] = self.plcClients[key].getHoldingRegs(hRegsAddr, hRegsNum)
            coilsAddr, coilsNum = self.plcInfo[key]['coilsInfo']
            self.coilsDict[key] = self.plcClients[key].getCoilsBits(coilsAddr, coilsNum)
            if self.regsDict[key] is None or self.coilsDict[key] is None:
                self.plcConnectionState[key] = False
            else:
                self.plcConnectionState[key] = True
        time.sleep(0.1)
        gv.gDebugPrint('DataManager: try to get RTU information', logType=gv.LOG_INFO)
        self.fetchRTUdata()

    #-----------------------------------------------------------------------------
    def fetchRTUdata(self):
        for key in gv.gTrackConfig.keys():
            memoryIdxList = gv.gTrackConfig[key]['rtuMemIdxList']
            for idx, memIdx in enumerate(memoryIdxList):
                rtuDataList = self.rtuClient.readAddressVal(memIdx, dataIdxList = (0, 2, 4, 6), 
                                                            dataTypeList=[BOOL_TYPE, INT_TYPE, INT_TYPE, INT_TYPE])
                self.rtuDataList[key][idx] = rtuDataList
        #print(self.rtuDataList)

    def getAllRtuDataDict(self):
        return self.rtuDataList

    #-----------------------------------------------------------------------------
    # define all the get() function here.
    def getPlcHRegsData(self, plcid, startIdx, endIdx):
        if plcid in self.regsDict.keys():
            if not self.regsDict[plcid] is None:
                return self.regsDict[plcid][startIdx:endIdx]
        return None

    #-----------------------------------------------------------------------------
    def getPlcCoilsData(self, plcid, startIdx, endIdx):
        if plcid in self.coilsDict.keys():
            if not self.coilsDict[plcid] is None:
                return self.coilsDict[plcid][startIdx:endIdx]
        return None

    #-----------------------------------------------------------------------------
    def getPlcConntionState(self, plcID):
        if plcID in self.plcClients.keys():
            return self.plcClients[plcID].checkConn() and self.plcConnectionState[plcID]
        return False

    def getRtuConnectionState(self):
        return self.rtuConnectionState

    #-----------------------------------------------------------------------------
    def getAllPlcRegsData(self):
        """ Combine all the registers data into one list and return it."""
        result = []
        for val in self.regsDict.values():
            if val is None: continue
            result += val
        return result
    
    #-----------------------------------------------------------------------------
    def getAllPlcCoisData(self):
        """ Combine all the coils data in to one list and return it."""
        result = []
        for val in self.coilsDict.values():
            if val is None: continue
            result += val
        return result
    
    #-----------------------------------------------------------------------------
    def setPlcCoilsData(self, plcid, idx, val):
        """ Set the PLC coils state
            Args:
                plcid (str): PLC ID
                idx (int): coils address index.
                val (bool): coil on/off state.
        """
        if plcid in self.plcClients.keys():
            gv.gDebugPrint('DataManager: set PLC coil:%s' %str((plcid, idx, val)), 
                           logType=gv.LOG_INFO)
            self.plcClients[plcid].setCoilsBit(idx, val)
            time.sleep(0.1)
    
    #-----------------------------------------------------------------------------
    def stop(self):
        for client in self.plcClients.values():
            client.close()
        gv.gDebugPrint('DataManager: Stopped all PLC clients', logType=gv.LOG_INFO)