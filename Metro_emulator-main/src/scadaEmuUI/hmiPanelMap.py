#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        hmiPanelMap.py
#
# Purpose:     This module is used to display the top view of the main railway 
#              system junction sensor-signals controlling and station sensor-signals
#              controlling real-time state.
# 
# Author:      Yuancheng Liu
#
# Version:     v0.1.3
# Created:     2023/06/13
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License 
#-----------------------------------------------------------------------------

import os
import wx
import time

import scadaGobal as gv

DEF_PNL_SIZE = (1750, 480)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelMap(wx.Panel):
    """ RailWay junction and station view map. """
    def __init__(self, parent, panelSize=DEF_PNL_SIZE):
        wx.Panel.__init__(self, parent, size=panelSize)
        self.bgColor = wx.Colour(30, 40, 62)
        self.SetBackgroundColour(self.bgColor)
        self.panelSize = panelSize
        self.toggle = False
        self._loadLabelsImg()
        # Paint the map
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.SetDoubleBuffered(True)  # Set the panel double buffer to void the panel flash during update.

#-----------------------------------------------------------------------------
    def _loadLabelsImg(self):
        """ Load the label image file and create the bitmap dict."""
        self.labelDict = { # (bitmap, location)
            'weline': [None, (70, 25)],
            'ccline': [None, (70, 175)],
            'nsline': [None, (1550, 335)],
        }
        for key in gv.gTrackConfig.keys():
            imgName = gv.gTrackConfig[key]['icon']
            imgPath = os.path.join(gv.IMG_FD, imgName)
            if os.path.exists(imgPath):
                self.labelDict[key][0] = wx.Bitmap(imgPath)
        # Draw the current date and time
        imgPath = os.path.join(gv.IMG_FD, 'time.png')
        self.labelDict['timelb'] = [wx.Bitmap(imgPath), (1450, 15)]
    
#-----------------------------------------------------------------------------
    def _drawRailWay(self, dc):
        """ Draw the background, railway tracks and different labels."""
        w, h = self.panelSize
        trackSeq = ('weline', 'ccline', 'nsline')
        dc.SetBrush(wx.Brush(self.bgColor))
        dc.DrawRectangle(0, 0, w, h)
        # draw the track lines.
        for i, trackName in enumerate(trackSeq):
            color = gv.gTrackConfig[trackName]['color']
            dc.SetPen(wx.Pen(color, width=4, style=wx.PENSTYLE_SOLID))
            dc.DrawLine(50, 100+160*i, 1700, 100+160*i,)
            dc.SetPen(wx.Pen(color, width=2, style=wx.PENSTYLE_SOLID))
            dc.DrawCircle(40, 100+160*i, 8)
            dc.DrawCircle(50, 100+160*i, 8)
            dc.DrawCircle(1700, 100+160*i, 8)
            dc.DrawCircle(1710, 100+160*i, 8)
        # draw three track's label
        for val in self.labelDict.values():
            bitmap, pos = val
            dc.DrawBitmap(bitmap, pos[0], pos[1])
        # draw the date and time label
        dc.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        dc.SetTextForeground(wx.Colour('GREEN'))
        dc.DrawText(time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time())), 1500, 15)

#-----------------------------------------------------------------------------
    def _drawSensors(self, dc):
        """ Draw the sensors with the state on track."""
        dc.SetPen(self.dcDefPen)
        dc.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        dc.SetBrush(wx.Brush('GRAY'))
        for sensorAgent in gv.iMapMgr.getSensors().values():
            sensorId = sensorAgent.getID()
            sensorNum = sensorAgent.getSensorsCount()
            posList = sensorAgent.getSensorPos()
            stateList = sensorAgent.getSensorsState()
            dc.SetTextForeground(wx.Colour('White'))
            for i in range(sensorNum):
                pos = posList[i]
                dc.DrawText(sensorId+"-s"+str(i), pos[0]+3, pos[1]+3)
                state = stateList[i]
                if state:
                    color = 'YELLOW' if self.toggle else 'BLUE'
                    dc.SetBrush(wx.Brush(color))
                    dc.DrawRectangle(pos[0]-6, pos[1]-6, 12, 12)
                else:
                    dc.SetBrush(wx.Brush('GRAY'))
                    dc.DrawRectangle(pos[0]-4, pos[1]-4, 8, 8)

#-----------------------------------------------------------------------------
    def _drawSignals(self, dc):
        """ Draw the signals with the State on track."""
        dc.SetPen(self.dcDefPen)
        dc.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        dc.SetTextForeground(wx.Colour('White'))
        dc.SetBrush(wx.Brush('Green'))
        for signals in gv.iMapMgr.getSignals().values():
            for signalAgent in signals:
                id = signalAgent.getID()
                pos = signalAgent.getPos()
                state = signalAgent.getState()
                # draw the trigger relation line to link the sensors
                tgOnlineStype = wx.PENSTYLE_SOLID if state else wx.PENSTYLE_LONG_DASH
                dc.SetPen(wx.Pen('RED', width=1, style=tgOnlineStype))
                for sensorPos in signalAgent.getTGonPos():
                    dc.DrawLine(pos[0]-10, pos[1], sensorPos[0], sensorPos[1])

                tgOfflineStype = wx.PENSTYLE_SOLID if not state else wx.PENSTYLE_LONG_DASH
                dc.SetPen(wx.Pen('GREEN', width=1, style=tgOfflineStype))
                for sensorPos in signalAgent.getTGoffPos():
                    dc.DrawLine(pos[0]+10, pos[1], sensorPos[0], sensorPos[1])
                # draw the signal sample.
                dc.SetPen(self.dcDefPen)
                x, y = pos[0], pos[1]
                dc.DrawText("S-"+str(id), x, y-25)
                color = 'RED' if state else 'GREEN'
                dc.SetBrush(wx.Brush(color))
                dc.DrawRectangle(x-10, y-4, 20, 8)

#-----------------------------------------------------------------------------
    def _drawStations(self, dc):
        """ Draw the station sensor and signal state."""
        dc.SetPen(self.dcDefPen)
        dc.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        for key, stations in gv.iMapMgr.getStations().items():
            dc.SetTextForeground(gv.gTrackConfig[key]['color'])
            for i, station in enumerate(stations):
                id = station.getID()
                pos = station.getPos()
                sensorState = station.getSensorState()
                signalState = station.getSignalState()
                dc.SetPen(wx.Pen(gv.gTrackConfig[key]['color']))
                lboffset = 30 if station.getlabelLayout() == gv.LAY_D else -45
                lioffest = 25 if station.getlabelLayout() == gv.LAY_D else -25
                dc.DrawLine(pos[0], pos[1], pos[0], pos[1]+lioffest)
                dc.DrawText("ST[%s]:%s" % (str(i), str(id)), pos[0]-30, pos[1]+lboffset)
                dc.SetPen(self.dcDefPen)
                dc.SetBrush(wx.Brush('GRAY'))
                # Draw the station sensor state
                if sensorState:
                    color = 'YELLOW' if self.toggle else 'BLUE'
                    dc.SetBrush(wx.Brush(color))
                    dc.DrawRectangle(pos[0]-5, pos[1]-5, 10, 10)
                else:
                    dc.DrawRectangle(pos[0]-5, pos[1]-5, 10, 10)
                # Draw the station signal state
                color = 'RED' if signalState else 'GREEN'
                dc.SetPen(wx.Pen(color, width=2, style=wx.PENSTYLE_SOLID))
                dc.SetBrush(wx.Brush(color, wx.TRANSPARENT))
                dc.DrawRectangle(pos[0]-10, pos[1]-10, 20, 20)

#-----------------------------------------------------------------------------
    def onPaint(self, event):
        """ Draw the whole panel by using the wx device context."""
        dc = wx.PaintDC(self)
        self.dcDefPen = dc.GetPen()
        # Draw all the components
        self._drawRailWay(dc)
        self._drawSignals(dc)
        self._drawSensors(dc)
        self._drawStations(dc)

#-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function
            will set the self update flag.
        """
        self.Refresh(False)
        self.Update()
        self.toggle = not self.toggle

#-----------------------------------------------------------------------------
    def periodic(self , now):
        """ periodicly call back to do needed calcualtion/panel update"""
        # Call the onPaint to update the map display.
        self.updateDisplay()
