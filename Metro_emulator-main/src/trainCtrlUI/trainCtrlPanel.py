#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        trainCtrl.py
#
# Purpose:     This module is used to create different function panels for the 
#              train control HMI.
#
# Author:      Yuancheng Liu
#
# Created:     2023/07/12
# Version:     v0.1.3
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License  
#-----------------------------------------------------------------------------

import os
from math import pi

import wx
import wx.grid
import wx.lib.agw.speedmeter as SM
import wx.gizmos as gizmos

import trainCtrlGlobal as gv

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class PanelTrainInfo(wx.Panel):
    """ Mutli-information display panel used to show all the trains' name, speed 
        track-id, current, voltage and power state.
    """
    def __init__(self, parent, panelSize=(600, 300)):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=panelSize)
        self.SetBackgroundColour(wx.Colour(39, 40, 62))
        self.SetSizer(self._buidUISizer())

#------------------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the UI sizer with the information grid"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        flagsL = wx.LEFT
        sizer.AddSpacer(5)
        # Row 0: Set the panel label
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        label = wx.StaticText(self, label="Trains Information [RTU]")
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour("WHITE"))
        sizer.Add(label, flag=flagsL, border=2)
        sizer.AddSpacer(10)
        # Row 1: set the information display grid
        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(12, 6)
        self.grid.SetRowLabelSize(40)
        # Set the Grid's column labels.
        self.grid.SetColLabelValue(0, 'Train-ID')
        self.grid.SetColLabelValue(1, 'Railway-ID')
        self.grid.SetColLabelValue(2, 'Speed[km/h]')
        self.grid.SetColSize(2, 80)
        self.grid.SetColLabelValue(3, 'Current[A]')
        self.grid.SetColSize(3, 90)
        self.grid.SetColLabelValue(4, 'DC-Voltage[V]')
        self.grid.SetColSize(4, 100)
        self.grid.SetColLabelValue(5, 'Power-State')
        self.grid.SetColSize(5, 100)
        sizer.Add(self.grid, flag=flagsL, border=2)
        return sizer

#------------------------------------------------------------------------------
    def updateTrainInfoGrid(self):
        """ Update the trains information grid."""
        lineIdx = 0
        for key in gv.gTrackConfig.keys():
            trainsInfo = gv.iMapMgr.getTrainsInfo(key)
            colorVal = gv.gTrackConfig[key]['color']
            for data in trainsInfo:
                self.grid.SetCellValue(lineIdx, 0, ' '+ str(data['id']))
                self.grid.SetCellValue(lineIdx, 1, key)
                self.grid.SetCellBackgroundColour(lineIdx, 1, colorVal)
                self.grid.SetCellValue(lineIdx, 2, ' '+ str(data['speed']) + ' km/h')
                self.grid.SetCellValue(lineIdx, 3, ' '+ str(data['current']) + ' A')
                self.grid.SetCellValue(lineIdx, 4, ' '+ str(data['voltage']) + ' V')
                pwdFlg = 'ON' if data['power'] else 'OFF'
                bgColor = wx.Colour('GREEN') if data['power'] else wx.Colour('RED')
                self.grid.SetCellValue(lineIdx, 5, ' '+ str(pwdFlg))
                self.grid.SetCellBackgroundColour(lineIdx, 5, bgColor)
                lineIdx += 1
        self.grid.ForceRefresh()  # refresh all the grid's cell at one time 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class SpeedGaugePanel(wx.Panel):
    """ Train speed gauge panel."""

    def __init__(self, parent, panelSize=(200, 230), speedRange=(0, 140)):
        wx.Panel.__init__(self, parent, size=panelSize)
        self.pnlSize = panelSize
        self.speedRange = speedRange
        self.speedVal = 0
        self.bgColor = wx.Colour(200, 210, 200)
        self.SetBackgroundColour(self.bgColor)
        self.SetSizer(self._buidUISizer())
    
#-----------------------------------------------------------------------------
    def _buidUISizer(self):
        # init the local function local constants
        flagsL = wx.LEFT
        lightGreen = wx.Colour(183, 253, 172)
        lightYellow = wx.Colour(253, 253, 172)
        lightBlue = wx.Colour(140, 170, 220)
        lightRed = wx.Colour(255, 130, 130)
        font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # Init the sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.speedGauge = SM.SpeedMeter(self, size=(self.pnlSize[0], self.pnlSize[1]-30) ,
                                        agwStyle=SM.SM_DRAW_HAND|SM.SM_DRAW_SECTORS|SM.SM_DRAW_MIDDLE_TEXT|SM.SM_DRAW_SECONDARY_TICKS)
        self.speedGauge.SetBackgroundColour(self.bgColor)
        self.speedGauge.SetAngleRange(-pi/6, 7*pi/6)
        intervals = range(int(self.speedRange[0]), int(self.speedRange[1])+1, 20)
        self.speedGauge.SetIntervals(intervals)
        colours = [lightBlue, lightGreen, lightGreen,
                   lightYellow, lightYellow, lightRed, lightRed]
        self.speedGauge.SetIntervalColours(colours)
        # Set the ticks.
        ticks = [str(interval) for interval in intervals]
        self.speedGauge.SetTicks(ticks)
        self.speedGauge.SetTicksColour(wx.BLACK)
        self.speedGauge.SetNumberOfSecondaryTicks(5)
        self.speedGauge.SetTicksFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        # Set The Text In The Center Of SpeedMeter
        self.speedGauge.SetMiddleText("Km / h")
        self.speedGauge.SetMiddleTextColour(wx.BLACK)
        self.speedGauge.SetMiddleTextFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        # Set The Colour For The Hand Indicator
        self.speedGauge.SetHandColour(wx.Colour(255, 50, 0))
        self.speedGauge.DrawExternalArc(False)
        self.speedGauge.SetSpeedValue(self.speedVal)
        sizer.Add(self.speedGauge, flag=flagsL, border=2)
        sizer.AddSpacer(10)
        # Add the speed display label.
        self.speedLabel = wx.StaticText(self, label=" Speed : %s Km/h" %str(self.speedVal))
        self.speedLabel.SetFont(font)
        sizer.Add(self.speedLabel, flag=wx.CENTER, border=2)
        return sizer

#-----------------------------------------------------------------------------
    def setSpeedValue(self, speedVal):
        self.speedVal = speedVal
        gaugeVal = min(speedVal, self.speedRange[1])
        self.speedGauge.SetSpeedValue(gaugeVal)
        self.speedLabel.SetLabel(" Speed : %s Km/h" %str(self.speedVal))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelTrain(wx.Panel):
    """ Trains information display and control panel. """
    def __init__(self, parent, trackId, trainId, panelSize=(300, 280), bgColour=None, fontColour=None):
        """ init example panel = PanelTrain(None, 'weline', 1, panelSize=(300, 280), 
                                            bgColor = wx.Colour('WHITE'),
                                            fontColor = wx.Colour('BLACK'))
        Args:
            parent (_type_): _description_
            trackId (str): _description_
            trainId (str/int): _description_
            panelSize (tuple, optional): Panel size. Defaults to (300, 280).
            bgColor (wx.Colour, optional): Panel background color. Defaults to wx.Colour(200, 210, 200).
            fontColor (_type_, optional): Panel font color. Defaults to wx.Colour('BLACK').
        """
        wx.Panel.__init__(self, parent, size=panelSize)
        self.trainId = trainId
        self.trackId = trackId
        self.bgColor = wx.Colour(200, 210, 200) if bgColour is None else bgColour
        self.fontColur = wx.Colour('BLACK') if fontColour is None else fontColour
        self.powerState = False
        self.currentVal = 0
        self.voltageVal = 750
        self.speedVal = 0 
        self.SetBackgroundColour(self.bgColor)
        self.SetSizer(self._buidUISizer())

#-----------------------------------------------------------------------------
    def _buidUISizer(self):
        flagsL = wx.LEFT
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        # Init the sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(5)
        # r0: add title
        titleLabel = wx.StaticText(
            self, label=" Train: %s - %s" % (self.trackId, str(self.trainId)))
        titleLabel.SetFont(font)
        titleLabel.SetForegroundColour(self.fontColur)
        sizer.Add(titleLabel, flag=flagsL, border=2)
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(295, -1),
                            style=wx.LI_HORIZONTAL), flag=flagsL, border=2)
        sizer.AddSpacer(5)
        # r1: Add the gaugae
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.speedGauge = SpeedGaugePanel(self)
        hbox.Add(self.speedGauge, flag=flagsL, border=2)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddSpacer(10)
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        # Add the power display
        color = wx.Colour('GREEN') if self.powerState else wx.Colour('RED')
        labelStr = ' Power:ON' if self.powerState else ' Power:OFF'
        self.powerLabel = wx.StaticText(self, label=labelStr)
        self.powerLabel.SetFont(font)
        self.powerLabel.SetBackgroundColour(color)
        vbox.Add(self.powerLabel, flag=flagsL, border=2)
        # Added the current display
        vbox.AddSpacer(10)
        crtlabel = wx.StaticText(self, label=' Current [A] :')
        crtlabel.SetFont(font)
        crtlabel.SetForegroundColour(self.fontColur)
        vbox.Add(crtlabel, flag=flagsL, border=2)
        vbox.AddSpacer(5)
        self.currentLed = gizmos.LEDNumberCtrl(self, -1, size=(80, 35), style=gizmos.LED_ALIGN_CENTER)
        self.currentLed.SetValue(str(self.currentVal))
        vbox.Add(self.currentLed, flag=flagsL, border=2)
        # Add the voltage display
        vbox.AddSpacer(10)
        voltagelabel = wx.StaticText(self, label=' Voltage [V]:')
        voltagelabel.SetFont(font)
        voltagelabel.SetForegroundColour(self.fontColur)
        vbox.Add(voltagelabel, flag=flagsL, border=2)
        vbox.AddSpacer(5)
        self.voltageLed = gizmos.LEDNumberCtrl(self, -1, size=(80, 35), style=gizmos.LED_ALIGN_CENTER)
        self.voltageLed.SetValue(str(750))
        vbox.Add(self.voltageLed, flag=flagsL, border=2)
        # Add the power control
        vbox.AddSpacer(10)
        pwrCtrllabel = wx.StaticText(self, label=' Pwr Control')
        pwrCtrllabel.SetFont(font)
        pwrCtrllabel.SetForegroundColour(self.fontColur)
        vbox.Add(pwrCtrllabel, flag=flagsL, border=2)
        startBmp = wx.Bitmap(os.path.join(gv.IMG_FD, 'reset32.png'), wx.BITMAP_TYPE_ANY)
        stoptBmp = wx.Bitmap(os.path.join(gv.IMG_FD, 'emgStop32.png'), wx.BITMAP_TYPE_ANY)
        hbox0 =  wx.BoxSizer(wx.HORIZONTAL)
        # Add the start button.
        self.recbtn1 = wx.BitmapButton(self, bitmap=startBmp,
                                       size=(startBmp.GetWidth()+10, startBmp.GetHeight()+10))
        self.recbtn1.Bind(wx.EVT_BUTTON, self.turnOnTrainPwr)
        hbox0.Add(self.recbtn1, flag=flagsL, border=1)
        # Add the emergency stop button.
        self.recbtn2 = wx.BitmapButton(self, bitmap=stoptBmp,
                                       size=(stoptBmp.GetWidth()+10, stoptBmp.GetHeight()+10))
        self.recbtn2.Bind(wx.EVT_BUTTON, self.turnOffTrain)
        hbox0.Add(self.recbtn2, flag=flagsL, border=1)
        vbox.Add(hbox0, flag=flagsL, border=0)
        hbox.Add(vbox, flag=flagsL, border=2)
        sizer.Add(hbox, flag=flagsL, border=2)
        return sizer 

   #-----------------------------------------------------------------------------
    def updateState(self, stateDict):
        """ update all the state. 
            stateDict example:{
                'id': self.id,
                'speed': 0,
                'current': o,
                'voltage': self.designVoltage + randint(0,50) if self.dataRanFlg else 0,
                'power': self.powerFlag
            }
        """
        if self.speedVal != stateDict['speed']:
            self.speedVal = stateDict['speed']
            self.speedGauge.setSpeedValue(self.speedVal)
        if self.powerState != stateDict['power']:
            self.powerState = stateDict['power']
            color = wx.Colour('GREEN') if self.powerState else wx.Colour('RED')
            labelStr = ' Power:ON' if self.powerState else ' Power:OFF'
            self.powerLabel.SetLabel(labelStr)
            self.powerLabel.SetBackgroundColour(color)
        if self.currentVal != stateDict['current']:
            self.currentVal = stateDict['current']
            self.currentLed.SetValue(str(self.currentVal))
        if self.voltageVal != stateDict['voltage']:
            self.voltageVal = stateDict['voltage']
            self.voltageLed.SetValue(str(self.voltageVal))

    #-----------------------------------------------------------------------------
    def turnOnTrainPwr(self, event):
        gv.gDebugPrint(' Turn on train power: %s on track: %s' %(str(self.trainId), self.trackId))
        if gv.idataMgr:
            TrainTgtPlcID = 'PLC-06'
            startIdx = gv.gTrackConfig[self.trackId]['trainCoilIdx'][0]
            idx = startIdx + int(self.trainId)
            # pop up a power change confirm message box
            dlg = wx.MessageDialog(None, "Confirm Power Turn ON: %s" %'-'.join((self.trackId, str(self.trainId))),
                                   'Train Pwr Change',wx.YES_NO | wx.ICON_WARNING)
            result = dlg.ShowModal()
            if result == wx.ID_YES: gv.idataMgr.setPlcCoilsData(TrainTgtPlcID, idx, True)

    #-----------------------------------------------------------------------------
    def turnOffTrain(self, event):
        gv.gDebugPrint(' Turn off train power: %s on track: %s' %(str(self.trainId), self.trackId))
        if gv.idataMgr:
            TrainTgtPlcID = 'PLC-06'
            startIdx = gv.gTrackConfig[self.trackId]['trainCoilIdx'][0]
            idx = startIdx + int(self.trainId)
            # pop up a power change confirm message box
            dlg = wx.MessageDialog(None, "Confirm Power Turon OFF: %s" %'-'.join((self.trackId, str(self.trainId))),
                                   'Train Pwr Change',wx.YES_NO | wx.ICON_WARNING)
            result = dlg.ShowModal()
            if result == wx.ID_YES: gv.idataMgr.setPlcCoilsData(TrainTgtPlcID, idx, False)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelRTU(wx.Panel):
    """_summary_

    Args:
        wx (_type_): _description_

    Returns:
        _type_: _description_
    """
    def __init__(self, parent, name, ipAddr, icon=None):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.rtuName = name
        self.ipAddr = ipAddr
        self.connectedFlg = False
        self.rtuSensorIndicators = []
        # Init the UI.
        img = os.path.join(gv.IMG_FD, 'rtuIcon.png')
        self.lbBmap = wx.Image(img, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.SetSizer(self.buidUISizer())

    def buidUISizer(self):
        """ Build the UI sizer."""
        mSizer = wx.BoxSizer(wx.HORIZONTAL) # main sizer
        flagsR = wx.LEFT
        # Row idx = 0 : set the basic PLC informaiton.
        titleSZ = self._buildTitleSizer()
        mSizer.Add(titleSZ, flag=flagsR, border=5)
        mSizer.AddSpacer(5)

        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 60),
                                 style=wx.LI_VERTICAL), flag=flagsR, border=5)
        mSizer.AddSpacer(6)
        indicatorsSZ = self._buildFsenserSizer()
        mSizer.Add(indicatorsSZ, flag=flagsR, border=5)
        mSizer.AddSpacer(10)
        return mSizer

    def _buildTitleSizer(self):
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        flagsR = wx.LEFT
        btnSample = wx.StaticBitmap(self, -1, self.lbBmap, (0, 0), (self.lbBmap.GetWidth(), self.lbBmap.GetHeight()))
        hsizer.Add(btnSample, flag=flagsR, border=5)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.nameLb = wx.StaticText(self, label=" RTU Name: ".ljust(15)+self.rtuName)
        vsizer.Add(self.nameLb, flag=flagsR, border=5)
        self.ipaddrLb = wx.StaticText( self, label=" RTU IPaddr: ".ljust(15)+self.ipAddr)
        vsizer.Add(self.ipaddrLb, flag=flagsR, border=5)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.StaticText(self, label=" Connection:".ljust(15)), flag=flagsR)
        self.connLb = wx.StaticText(self, label=' Connected ' if self.connectedFlg else ' Unconnected ')
        self.connLb.SetBackgroundColour( wx.Colour('GREEN') if self.connectedFlg else wx.Colour(120, 120, 120))
        hbox0.Add(self.connLb, flag=flagsR, border=5)
        vsizer.Add(hbox0, flag=flagsR, border=5)
        hsizer.Add(vsizer, flag=flagsR, border=5)
        return hsizer

    def _buildFsenserSizer(self):
        szier = wx.GridSizer(3, 4, 2, 2)
        for idx in range(1, 13):
            sensBt = wx.Button(self, label="TF-Sen-%02d" %(idx,), size=(70, 20))
            #sensBt.SetBackgroundColour(wx.Colour("GOLD")) 
            self.rtuSensorIndicators.append(sensBt)
            szier.Add(sensBt)
        return szier

    def setConnection(self, state):
        """ Update the connection state on the UI."""
        self.connectedFlg = state
        self.connLb.SetLabel(' Connected ' if self.connectedFlg else ' Unconnected ')
        self.connLb.SetBackgroundColour(
            wx.Colour('GREEN') if self.connectedFlg else wx.Colour(120, 120, 120))
        self.Refresh(False)

    def updateSenIndicator(self):
        resultList = []
        for key in gv.gTrackConfig.keys():
            trainsInfo = gv.iMapMgr.getTrainsInfo(key)
            for data in trainsInfo:
                resultList.append(data['fsensor'])
        for idx, val in enumerate(resultList):
            color = wx.Colour('GOLD') if val else wx.Colour('FOREST GREEN')
            self.rtuSensorIndicators[idx].SetBackgroundColour(color)
        self.Refresh(False)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelPLC(wx.Panel):
    """ PLC panel UI to show PLC input feedback state and the relay connected 
        to the related output pin.
    """
    def __init__(self, parent, name, ipAddr, icon=None, dInInfoList=None, dOutInfoList=None):
        """ Init the panel."""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        # Init self paremeters
        self.plcName = name
        self.ipAddr = ipAddr
        self.regsNum = 16
        self.coilsNum = 8
        self.connectedFlg = False
        self.gpioInList = [0]*self.regsNum  # PLC GPIO input stuation list.
        self.gpioInLbList = []  # GPIO input device <id> label list.
        self.gpioOuList = [0]*self.coilsNum # PLC GPIO output situation list.
        self.gpioOuLbList = []  # GPIO output device <id> label list.
        self.dInInfoList = dInInfoList
        self.dOutInfoList = dOutInfoList

        # Init the UI.
        img = os.path.join(gv.IMG_FD, 'plcIcon.png')
        self.lbBmap = wx.Image(img, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.SetSizer(self.buidUISizer())
        #self.Layout() # must call the layout if the panel size is set to fix.

#--PanelPLC--------------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI and the return the wx.sizer. """
        mSizer = wx.BoxSizer(wx.VERTICAL) # main sizer
        flagsR = wx.LEFT
        mSizer.AddSpacer(5)
        # Row idx = 0 : set the basic PLC informaiton.
        titleSZ = self._buildTitleSizer()
        mSizer.Add(titleSZ, flag=flagsR, border=5)
        mSizer.AddSpacer(10)
        # Row idx = 1: set the GPIO and feed back of the PLC. 
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(270, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=5)
        mSizer.AddSpacer(10)
        # - row line structure: Input indicator | output label | output button with current status.
        for i in range(self.regsNum):
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            # Col idx = 0: PLC digital in 
            if self.dInInfoList and i < len(self.dInInfoList):
                cfg = self.dInInfoList[i]
                lbtext = cfg['item']
                inputLb = wx.StaticText(self, label=lbtext.ljust(6))
                inputLb.SetBackgroundColour(cfg['color'])
                hsizer.Add(inputLb, flag=flagsR, border=5)
            else:
                inputLb = wx.StaticText(self, label='NoIO'.ljust(6))
                inputLb.SetBackgroundColour(wx.Colour('BLACK'))
                hsizer.Add(inputLb, flag=flagsR, border=5)
            # Col idx = 0: PLC input indicators.
            lbtext = " R_%H 0."+str(i)
            inputLb = wx.StaticText(self, label=lbtext.ljust(12))
            inputLb.SetBackgroundColour(wx.Colour(120, 120, 120))
            hsizer.Add(inputLb, flag=flagsR, border=5)
            self.gpioInLbList.append(inputLb)
            # Col idx =1: PLC output labels.
            hsizer.AddSpacer(5)
            if i < self.coilsNum:
                # Added the coils output info.
                hsizer.Add(wx.StaticText(self, label=str(
                    " %Q 0."+str(i)+':').ljust(12)), flag=flagsR, border=5)
                # Col idx =2: PLC output ON/OFF contorl buttons.
                #hsizer.AddSpacer(5)
                outputBt = wx.Button(self, label='OFF', size=(50, 17), name=self.plcName+':'+str(i))
                self.gpioOuLbList.append(outputBt)
                hsizer.Add(outputBt, flag=flagsR, border=5)
                # Add the digital output 
                if self.dOutInfoList and i < len(self.dOutInfoList):
                    cfg = self.dOutInfoList[i]
                    lbtext = cfg['item']
                    outputLb = wx.StaticText(self, label=lbtext.ljust(6))
                    outputLb.SetBackgroundColour(cfg['color'])
                    hsizer.Add(outputLb, flag=flagsR, border=5)
                else:
                    outputLb = wx.StaticText(self, label='NoIO'.ljust(6))
                    outputLb.SetBackgroundColour(wx.Colour('BLACK'))
                    hsizer.Add(outputLb, flag=flagsR, border=5)
            mSizer.Add(hsizer, flag=flagsR, border=5)
            mSizer.AddSpacer(3)
        return mSizer

#--PanelPLC--------------------------------------------------------------------
    def _buildTitleSizer(self):
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        flagsR = wx.LEFT
        btnSample = wx.StaticBitmap(self, -1, self.lbBmap, (0, 0), (self.lbBmap.GetWidth(), self.lbBmap.GetHeight()))
        hsizer.Add(btnSample, flag=flagsR, border=5)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.nameLb = wx.StaticText(self, label=" PLC Name: ".ljust(15)+self.plcName)
        vsizer.Add(self.nameLb, flag=flagsR, border=5)
        self.ipaddrLb = wx.StaticText( self, label=" PLC IPaddr: ".ljust(15)+self.ipAddr)
        vsizer.Add(self.ipaddrLb, flag=flagsR, border=5)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.StaticText(self, label=" Connection:".ljust(15)), flag=flagsR)
        self.connLb = wx.StaticText(self, label=' Connected ' if self.connectedFlg else ' Unconnected ')
        self.connLb.SetBackgroundColour( wx.Colour('GREEN') if self.connectedFlg else wx.Colour(120, 120, 120))
        hbox0.Add(self.connLb, flag=flagsR, border=5)
        vsizer.Add(hbox0, flag=flagsR, border=5)
        hsizer.Add(vsizer, flag=flagsR, border=5)
        return hsizer

#--PanelPLC--------------------------------------------------------------------
    def setConnection(self, state):
        """ Update the connection state on the UI."""
        self.connectedFlg = state
        self.connLb.SetLabel(' Connected ' if self.connectedFlg else ' Unconnected ')
        self.connLb.SetBackgroundColour(
            wx.Colour('GREEN') if self.connectedFlg else wx.Colour(120, 120, 120))
        self.Refresh(False)

#--PanelPLC--------------------------------------------------------------------
    def updateHoldingRegs(self, regList):
        """ Update the holding register's data and UI indicator's state if there 
            is new register chagne.
        """
        if regList is None or self.gpioInList == regList: return # no new update
        for idx in range(min(self.regsNum, len(regList))):
            status = regList[idx]
            if self.gpioInList[idx] != status:
                self.gpioInList[idx] = status
                self.gpioInLbList[idx].SetBackgroundColour(
                    wx.Colour('GREEN') if status else wx.Colour(120, 120, 120))

#--PanelPLC--------------------------------------------------------------------
    def updateCoils(self, coilsList):
        """ Update the coils data and UI indicator's state if there is new coils
            state chagne.
        """
        if coilsList is None or self.gpioOuList == coilsList: return  
        for idx in range(min(self.coilsNum, len(coilsList))):
            status = coilsList[idx]
            if self.gpioOuList[idx] != status:
                self.gpioOuList[idx] = status
                self.gpioOuLbList[idx].SetLabel('ON' if status else 'OFF')
                self.gpioOuLbList[idx].SetBackgroundColour(
                    wx.Colour('GREEN') if status else wx.Colour(253, 253, 253))

#--PanelPLC--------------------------------------------------------------------
    def updataPLCdata(self):
        if gv.idataMgr:
            plcdata =  gv.idataMgr.getPLCInfo(self.plcName)
            if plcdata:
                self.updateHoldingRegs(plcdata[0])
                self.updateCoils(plcdata[1])

#--PanelPLC--------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function
            will set the self update flag.
        """
        self.Refresh(False)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    """ Main function used for local test debug panel. """

    print('Test Case start: type in the panel you want to check:')
    print('0 - PanelImge')
    print('1 - PanelCtrl')
    #pyin = str(input()).rstrip('\n')
    #testPanelIdx = int(pyin)
    testPanelIdx = 1    # change this parameter for you to test.
    print("[%s]" %str(testPanelIdx))
    app = wx.App()
    mainFrame = wx.Frame(gv.iMainFrame, -1, 'Debug Panel',
                         pos=(300, 300), size=(640, 480), style=wx.DEFAULT_FRAME_STYLE)
    if testPanelIdx == 0:
        testPanel = PanelTrain(mainFrame)
    elif testPanelIdx == 1:
        testPanel = PanelTrain(mainFrame, 'weline', '01')
    mainFrame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()



