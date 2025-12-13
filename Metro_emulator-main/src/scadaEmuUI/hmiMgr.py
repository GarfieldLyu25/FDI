#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        hmiMgr.py
#
# Purpose:     The management module to control all the components on the map 
#              and update the components state. 
# 
# Author:      Yuancheng Liu
#
# Version:     v0.1.3
# Created:     2023/05/29
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import scadaGobal as gv
from collections import OrderedDict

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class AgentSensors(object):
    """ The sensors set to show the sensors detection state."""
    def __init__(self, parent, id, posList=None):
        self.parent = parent
        self.id = id
        self.sensorsCount = 0 if posList is None else len(posList)
        self.sensorsPosList = [] if posList is None else posList
        self.sensorsStateList = [0]*self.sensorsCount

    def addOneSensor(self, pos):
        self.sensorsPosList.append(pos)
        self.sensorsCount += 1
        self.sensorsStateList.append(0)
    
    def updateSensorState(self, idx, state):
        if idx < self.sensorsCount:
            self.sensorsStateList[idx] = state

    def updateSensorsState(self, statList):
        if statList is None: return
        print("update sensor: %s, in: %s, %s " %(str(self.id), str(self.sensorsCount), str(len(statList))))
        if len(statList) == self.sensorsCount:
            self.sensorsStateList = statList
#-----------------------------------------------------------------------------
# Init all the get() function here:
    def getID(self):
        return self.id

    def getSensorsCount(self):
        return self.sensorsCount

    def getSensorPos(self):
        return self.sensorsPosList

    def getSensorsState(self):
        return self.sensorsStateList

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentSignal(object):
    """ The signal agent."""
    def __init__(self, parent, id, pos) -> None:
        self.parent = parent
        self.id = id
        self.pos = pos
        self.state = False
        self.triggerOnPosList = []
        self.triggerOffPosList = []
    
    def addTGonPos(self, pos):
        self.triggerOnPosList.append(pos)

    def addTFoffPos(self, pos):
        self.triggerOffPosList.append(pos)

#-----------------------------------------------------------------------------
# Init all the get() function here:
    def getID(self):
        return self.id
    
    def getState(self):
        return self.state

    def getPos(self):
        return self.pos
    
    def getTGonPos(self):
        return self.triggerOnPosList
    
    def getTGoffPos(self):
        return self.triggerOffPosList
    
    def setState(self, state):
        self.state = state

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class AgentStation(object):
    """ The station agent."""
    def __init__(self, parent, id, pos, labelLayout=gv.LAY_D) -> None:
        self.parent = parent
        self.id = id 
        self.pos = pos 
        self.sensorState = False    # station sensor state. 
        self.signalState = False    # station singal state.
        self.labelLayout = labelLayout

#-----------------------------------------------------------------------------
# Init all the get() function here:
    def getID(self):
        return self.id
    
    def getPos(self):
        return self.pos

    def getSensorState(self):
        return self.sensorState
    
    def getSignalState(self):
        return self.signalState

    def getlabelLayout(self):
        return self.labelLayout

#-----------------------------------------------------------------------------
# Init all the set() function here:
    def setSensorState(self, state):
        self.sensorState = state

    def setSignalState(self, state):
        self.signalState = state

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MapMgr(object):
    """ Map manager to init/control differet elements state on the map."""
    def __init__(self, parent):
        """ Init all the elements on the map. All the parameters are public to 
            other module.
        """
        self.sensors = OrderedDict()
        self.signals = OrderedDict()
        self.stations = OrderedDict()
        self._initSensors()
        self._initSignals()
        self._initStations()

#-----------------------------------------------------------------------------
    def _initSensors(self):
        """ Init all the sensors location on track."""
        # weline (top)
        y = 100
        sensorPos_we = [(80+100*i, y) for i in range(17)]
        self.sensors['weline'] = AgentSensors(self, 'we')
        for pos in sensorPos_we:
            self.sensors['weline'].addOneSensor(pos)
        # ccline (mid)
        y += 160
        sensorPos_cc = [(80+120*i, y) for i in range(14)] 
        self.sensors['ccline'] = AgentSensors(self, 'cc')
        for pos in sensorPos_cc:
            self.sensors['ccline'].addOneSensor(pos)
        # nsline (btm)
        y+= 160
        sensorPos_ns = [(80+210*i, y) for i in range(8)]
        self.sensors['nsline'] = AgentSensors(self, 'ns')
        for pos in sensorPos_ns:
            self.sensors['nsline'].addOneSensor(pos)

#-----------------------------------------------------------------------------
    def _builSignalList(self, configDict):
        signals = []
        for signalInfo in configDict:
            signal = AgentSignal(self, signalInfo['id'], signalInfo['pos'])
            sPosList = self.getSensors(trackID=signalInfo['tiggerS']).getSensorPos()
            for idx in signalInfo['onIdx']:
                signal.addTGonPos(sPosList[idx])
            for idx in signalInfo['offIdx']:
                signal.addTFoffPos(sPosList[idx])
            signals.append(signal)
        return signals

#-----------------------------------------------------------------------------
    def _initSignals(self):
        """ Init all the signals location on track."""
        # weline (top)
        y = 100
        key = 'weline'
        trackSignalConfig_we = [
            {'id': 'we-0', 'pos':(80+100*1+30, y), 'tiggerS': 'ccline', 'onIdx':(12,), 'offIdx':(13,) },
            {'id': 'we-2', 'pos':(80+100*3+30, y), 'tiggerS': 'ccline', 'onIdx':(10,), 'offIdx':(11,) },
            {'id': 'we-4', 'pos':(80+100*5+30, y), 'tiggerS': 'ccline', 'onIdx':(8,), 'offIdx':(9,) },
            {'id': 'we-6', 'pos':(80+100*7+30, y), 'tiggerS': 'ccline', 'onIdx':(6,), 'offIdx':(7,) },
            {'id': 'we-7', 'pos':(80+100*9+30, y), 'tiggerS': 'ccline', 'onIdx':(6,), 'offIdx':(7,) },
            {'id': 'we-5', 'pos':(80+100*11+30, y), 'tiggerS': 'ccline', 'onIdx':(8,), 'offIdx':(9,) },
            {'id': 'we-3', 'pos':(80+100*13+30, y), 'tiggerS': 'ccline', 'onIdx':(10,), 'offIdx':(11,) },
            {'id': 'we-1', 'pos':(80+100*15+30, y), 'tiggerS': 'ccline', 'onIdx':(12,), 'offIdx':(13,) },            
        ]
        self.signals[key] = self._builSignalList(trackSignalConfig_we)
        # ccline (mid)
        y += 160
        trackSignalConfig_cc = [
            {'id': 'cc-0', 'pos':(80+120*0+40, y), 'tiggerS': 'nsline', 'onIdx':(0, 6), 'offIdx':(1, 7) },
            {'id': 'cc-1', 'pos':(80+120*2+40, y), 'tiggerS': 'nsline', 'onIdx':(4,), 'offIdx':(5,) },
            {'id': 'cc-2', 'pos':(80+120*4+40, y, y), 'tiggerS': 'nsline', 'onIdx':(2,), 'offIdx':(3,) },
            {'id': 'cc-3', 'pos':(80+120*6+40, y),  'tiggerS': 'weline', 'onIdx':(7,9), 'offIdx':(8,10) },
            {'id': 'cc-4', 'pos':(80+120*8+40, y),  'tiggerS': 'weline', 'onIdx':(5,11), 'offIdx':(6,12) },
            {'id': 'cc-5', 'pos':(80+120*10+40, y),  'tiggerS': 'weline', 'onIdx':(3,13), 'offIdx':(4,14) },
            {'id': 'cc-6', 'pos':(80+120*12+40, y),  'tiggerS': 'weline', 'onIdx':(1, 15), 'offIdx':(2,16) },
        ]
        key = 'ccline'
        self.signals[key] = self._builSignalList(trackSignalConfig_cc)
        # nsline (btm)
        y += 160
        trackSignalConfig_ns = [
            {'id': 'ns-0', 'pos':(80+210*0+70, y), 'tiggerS': 'ccline', 'onIdx':(0,), 'offIdx':(1,) },
            {'id': 'ns-1', 'pos':(80+210*2+70, y), 'tiggerS': 'ccline', 'onIdx':(0,), 'offIdx':(1,) },
            {'id': 'ns-2', 'pos':(80+210*4+70, y), 'tiggerS': 'ccline', 'onIdx':(2,), 'offIdx':(3,) },
            {'id': 'ns-3', 'pos':(80+210*6+70, y), 'tiggerS': 'ccline', 'onIdx':(4,), 'offIdx':(5,) },
        ]
        key = 'nsline'
        self.signals[key] = self._builSignalList(trackSignalConfig_ns)

#-----------------------------------------------------------------------------
    def _initStations(self):
        """ Init all the station location on track."""
        # weline (top)
        y = 100
        key = 'weline'
        trackStation_we = [{'id': 'Tuas_Link', 'pos': (80+100*0+60, y), 'layout': gv.LAY_D},
                    {'id': 'Jurong_East', 'pos': (80+100*2+60, y), 'layout': gv.LAY_U},
                    {'id': 'Outram_Park', 'pos': (80+100*4+60, y), 'layout': gv.LAY_U},
                    {'id': 'City_Hall', 'pos': (80+100*6+30, y), 'layout': gv.LAY_U, },
                    {'id': 'Paya_Lebar', 'pos': (80+100*6+60, y), 'layout': gv.LAY_D },
                    {'id': 'Changi_Airport', 'pos': (80+100*8+60, y), 'layout': gv.LAY_U, },
                    {'id': 'Lavender', 'pos': (80+100*10+60, y), 'layout': gv.LAY_U},
                    {'id': 'Raffles_Place', 'pos': (80+100*12+60, y), 'layout': gv.LAY_U},
                    {'id': 'Clementi', 'pos': (80+100*14+60, y), 'layout': gv.LAY_U},
                    {'id': 'Boon_Lay', 'pos': (80+100*15+60, y), 'layout': gv.LAY_D}]
        self.stations[key] = []
        for stationInfo in trackStation_we:
            station = AgentStation(self, stationInfo['id'], stationInfo['pos'], labelLayout=stationInfo['layout'])
            self.stations[key].append(station)
        # ccline (mid)
        y += 160
        key = 'ccline'
        trackStation_cc = [
                    {'id': 'Buona_Vista', 'pos': (80+120*11+40, y), 'layout': gv.LAY_D},
                    {'id': 'Farrer_Road', 'pos': (80+120*12+80, y), 'layout': gv.LAY_D},
                    {'id': 'Serangoon', 'pos': (80+120*3+80, y), 'layout': gv.LAY_U},
                    {'id': 'Nicoll_Highway', 'pos': (80+120*7+40, y), 'layout': gv.LAY_U},
                    {'id': 'Bayfront', 'pos': (80+120*7+80, y),'layout': gv.LAY_D},
                    {'id': 'Harbourfront', 'pos': (80+120*9+80, y),'layout': gv.LAY_D}]
        self.stations[key] = []
        for stationInfo in trackStation_cc:
            station = AgentStation(self, stationInfo['id'], stationInfo['pos'], labelLayout=stationInfo['layout'])
            self.stations[key].append(station)
        # nsline (btm)
        y += 160
        key = 'nsline'
        trackStation_ns = [{'id': 'Jurong_East', 'pos': (80+210*6+140, y), 'layout': gv.LAY_D},
                           {'id': 'Woodlands', 'pos': (80+210*1+70, y), 'layout': gv.LAY_U},
                           {'id': 'Yishun', 'pos': (80+210*1+140, y), 'layout': gv.LAY_D},
                           {'id': 'Orchard', 'pos': (80+210*3+70, y), 'layout': gv.LAY_U},
                           {'id': 'City_Hall', 'pos': (80+210*3+140, y), 'layout': gv.LAY_D},
                           {'id': 'Bishan', 'pos': (80+210*5+140, y), 'layout': gv.LAY_D}]
        self.stations[key] = []
        for stationInfo in trackStation_ns:
            station = AgentStation(self, stationInfo['id'], stationInfo['pos'], labelLayout=stationInfo['layout'])
            self.stations[key].append(station)

#-----------------------------------------------------------------------------
# Init all the get() function here:
    def getSensors(self, trackID=None):
        if trackID and trackID in self.sensors.keys(): return self.sensors[trackID]
        return self.sensors

    def getSignals(self, trackID=None):
        if trackID and trackID in self.signals.keys(): return self.signals[trackID]
        return self.signals
    
    def getStations(self, trackID=None):
        if trackID and trackID in self.stations.keys(): return self.stations[trackID]
        return self.stations

#-----------------------------------------------------------------------------
# Init all the set() function here:
    def setSensors(self, trackID, stateList):
        self.sensors[trackID].updateSensorsState(stateList)

    def setSingals(self, trackID, stateList):
        if trackID is None or stateList is None: return
        if len(stateList) <= len(self.signals[trackID]):
            for i, state in enumerate(stateList):
                self.signals[trackID][i].setState(state)

    def setStationsSensors(self, trackID, stateList):
        if trackID is None or stateList is None: return
        if trackID in self.stations.keys() and len(stateList) <= len(self.stations[trackID]):
            for i, state in enumerate(stateList):
                self.stations[trackID][i].setSensorState(state)

    def setStationsSignals(self, trackID, stateList):
        if trackID is None or stateList is None: return
        if trackID in self.stations.keys() and len(stateList) <= len(self.stations[trackID]):
            for i, state in enumerate(stateList):
                self.stations[trackID][i].setSignalState(state)
