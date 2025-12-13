#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        MetroEmuRun.py
#
# Purpose:     This module is the main wx-frame for the metro railway and signal
#              sysetm emulator.
#
# Author:      Yuancheng Liu
#
# Version:     v0.1.2
# Created:     2023/05/26
# Copyright:   Copyright (c) 2023 Singapore National Cybersecurity R&D Lab LiuYuancheng
# License:     MIT License 
#-----------------------------------------------------------------------------

import os 
import time
import json

import wx
import metroEmuGobal as gv
import railwayMgr as mapMgr
import railwayPanel as pnlFunction
import railwayPanelMap as pnlMap
import dataMgr as dm

FRAME_SIZE = (1800, 1030)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class UIFrame(wx.Frame):
    """ Main UI frame window."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=FRAME_SIZE)
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        # No boader frame:
        # wx.Frame.__init__(self, parent, id, title, style=wx.MINIMIZE_BOX | wx.STAY_ON_TOP)
        # self.SetBackgroundColour(wx.Colour(30, 40, 62))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        #self.SetTransparent(gv.gTranspPct*255//100)
        # Init the global variables:
        self._initGlobals()
        # Build the top menu bar.
        self._buildMenuBar()
        # Build UI sizer
        self.SetSizer(self._buidUISizer())
        # Add the bottom status bar under single line mode.
        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText('Test mode: %s' %str(gv.gTestMD))
        # Set the periodic call back
        self.updateLock = False
        # Define the data manager parallel thread.
        gv.iDataMgr = dm.DataManager(self)
        gv.iDataMgr.start()

        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(gv.PERIODIC)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        gv.gDebugPrint("Metro-System real world main frame inited.", logType=gv.LOG_INFO)

#--UIFrame---------------------------------------------------------------------
    def _initGlobals(self):
        # Init the global parameters used only by this module
        gv.gTrackConfig['weline'] = {'id':'weline', 'num': 4, 'color': wx.Colour(52, 169, 129), 
                                     'stationCfg': gv.CONFIG_DICT['WE_STATION_CFG'], 'icon': 'welabel.png'}
        gv.gTrackConfig['nsline'] = {'id':'nsline', 'num': 3, 'color': wx.Colour(233, 0, 97), 
                                     'stationCfg': gv.CONFIG_DICT['NC_STATION_CFG'], 'icon': 'nslabel.png'}
        gv.gTrackConfig['ccline'] = {'id':'ccline', 'num': 3, 'color': wx.Colour(255, 136, 0), 
                                     'stationCfg': gv.CONFIG_DICT['CC_STATION_CFG'], 'icon': 'cclabel.png'}
        gv.gTrackConfig['mtline'] = {'id':'mtline', 'num': 0, 'color': wx.Colour(200, 210, 200), 
                                     'stationCfg': gv.CONFIG_DICT['MT_STATION_CFG'], 'icon': None}
        # Init all the global instance
        # if gv.gCollsionTestFlg: gv.gTestMD = False # disable the test mode flag to fetch the signal from PLC
        # Init all the train list
        self.trainCfgFiles = [filename for filename in os.listdir(gv.gTrainCfgDir) if filename.endswith('.json')]
        gv.gDebugPrint("Avalible Scenario file: %s" %str(self.trainCfgFiles), logType=gv.LOG_INFO)
        gv.iMapMgr = mapMgr.MapMgr(self)

#--UIFrame---------------------------------------------------------------------
    def _buildMenuBar(self):
        menubar = wx.MenuBar()  # Creat the function menu bar.
        # Add the config menu
        
        # load scenario
        configMenu = wx.Menu()
        scenarioItem = wx.MenuItem(configMenu, 100, text = "Load Scenario",kind = wx.ITEM_NORMAL)
        configMenu.Append(scenarioItem)
        self.Bind(wx.EVT_MENU, self.onLoadScenario, scenarioItem)
        menubar.Append(configMenu, '&Config')

        # Add the about menu.
        helpMenu = wx.Menu()
        aboutItem = wx.MenuItem(helpMenu, 200,text = "Help",kind = wx.ITEM_NORMAL)
        helpMenu.Append(aboutItem)
        self.Bind(wx.EVT_MENU, self.onHelp, aboutItem)
        menubar.Append(helpMenu, '&About')

        self.SetMenuBar(menubar)

#--UIFrame---------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI Sizer. """
        flagsL = wx.LEFT
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        mSizer.AddSpacer(5)
        # Add the train control panels.
        vbox0 = self._buildTrainCtrlSizer()                
        mSizer.Add(vbox0, flag=flagsL, border=2)
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 980),
                                 style=wx.LI_VERTICAL), flag=flagsL, border=2)
        mSizer.AddSpacer(5)
        # Add the real word display panel.
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.AddSpacer(5)
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        label = wx.StaticText(self, label= "RealWorld Metro System Emulator")
        label.SetFont(font)
        vbox1.Add(label, flag=wx.CENTRE, border=2)
        vbox1.AddSpacer(5)
        gv.iMapPanel = self.mapPanel = pnlMap.PanelMap(self)
        vbox1.Add(gv.iMapPanel, flag=wx.CENTRE, border=2)
        mSizer.Add(vbox1, flag=flagsL, border=2)
        return mSizer

#--UIFrame---------------------------------------------------------------------
    def _buildTrainCtrlSizer(self):
        flagsL = wx.LEFT
        vbox0 = wx.BoxSizer(wx.VERTICAL)
        vbox0.AddSpacer(5)
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        label = wx.StaticText(self, label="Trains Control")
        label.SetFont(font)
        vbox0.Add(label, flag=flagsL, border=2)
        vbox0.AddSpacer(5)
        for key, panelCfg in gv.gTrackConfig.items():
            img, color = panelCfg['icon'], panelCfg['color']
            if img is None: continue
            img = os.path.join(gv.IMG_FD, img)
            png = wx.Image(img, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            sublabel = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
            vbox0.Add(sublabel, flag=flagsL, border=2)
            for i in range(panelCfg['num']):
                trainPanel = pnlFunction.PanelTainCtrl(self, panelCfg['id'], i, bgColor=color)
                vbox0.Add(trainPanel, flag=flagsL, border=2)
                vbox0.AddSpacer(5)
        img = os.path.join(gv.IMG_FD, 'buttonSample.png')
        png = wx.Image(img, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        btnSample = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
        vbox0.Add(btnSample, flag=flagsL, border=2)
        self.collisionCB = wx.CheckBox(self, label = 'Auto collision avoidance')
        self.collisionCB.SetValue(gv.gCollAvoid)
        self.collisionCB.Bind(wx.EVT_CHECKBOX, self.onCollisionSet)
        vbox0.Add(self.collisionCB, flag=flagsL, border=2)
        
        self.showTRWInfoCB = wx.CheckBox(self, label = 'Show trains information')
        self.showTRWInfoCB.SetValue(gv.gShowTrainRWInfo)
        self.showTRWInfoCB.Bind(wx.EVT_CHECKBOX, self.onShowTRWInfoSet)
        vbox0.Add(self.showTRWInfoCB, flag=flagsL, border=2)

        return vbox0

#--UIFrame---------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        now = time.time()
        if (not self.updateLock) and now - self.lastPeriodicTime >= gv.gUpdateRate:
            print("main frame update at %s" % str(now))
            self.lastPeriodicTime = now
            # update the manager.
            gv.iMapMgr.periodic(now)
            # apply the state on the map panel.
            self.mapPanel.periodic(now)

#-----------------------------------------------------------------------------
    def onCollisionSet(self, event):
        gv.gCollAvoid = self.collisionCB.IsChecked()
        gv.gDebugPrint("Trains automated collision avoidance enable: %s" %str(gv.gCollAvoid), logType=gv.LOG_INFO)

    def onShowTRWInfoSet(self, event):
        gv.gShowTrainRWInfo = self.showTRWInfoCB.IsChecked()
        gv.gDebugPrint("Show Train realworld information enable: %s" %str(gv.gShowTrainRWInfo), logType=gv.LOG_INFO)
    
    def changeCAcheckboxState(self, state):
        self.collisionCB.SetValue(state)

#-----------------------------------------------------------------------------
    def onLoadScenario(self, event):
        self.scenarioDialog = wx.SingleChoiceDialog(self,
                                                    'Select Scenario', 
                                                    'Scenario selection', 
                                                    self.trainCfgFiles)
        resp = self.scenarioDialog.ShowModal()
        if resp == wx.ID_OK:
            trainConfigName = self.scenarioDialog.GetStringSelection()
            trainConfigPath = os.path.join(gv.gTrainCfgDir, trainConfigName)
            if os.path.exists(trainConfigPath):
                with open(trainConfigPath) as json_file:
                    trainConfigDict = json.load(json_file)
                    if gv.iMapMgr:
                        self.updateLock = True
                        gv.iMapMgr.resetTrainsPos(trainConfigDict)
                        self.updateLock = False
        self.scenarioDialog.Destroy()
        self.scenarioDialog = None

#-----------------------------------------------------------------------------
    def onHelp(self, event):
        """ Pop-up the Help information window. """
        wx.MessageBox(' If there is any bug, please contact: \n\n \
                        Author:      Yuancheng Liu \n \
                        Email:       liu_yuan_cheng@hotmail.com \n \
                        Created:     2023/05/02 \n \
                        GitHub Link: https://github.com/LiuYuancheng/Metro_emulator \n', 
                    'Help', wx.OK)

#-----------------------------------------------------------------------------
    def onClose(self, evt):
        """ Pop up the confirm close dialog when the user close the UI from 'x'."""
        try:
            fCanVeto = evt.CanVeto()
            if fCanVeto:
                confirm = wx.MessageDialog(self, 'Click OK to close this program, or click Cancel to ignore close request',
                                            'Quit request', wx.OK | wx.CANCEL| wx.ICON_WARNING).ShowModal()
                if confirm == wx.ID_CANCEL:
                    evt.Veto(True)
                    return
                if gv.iDataMgr: gv.iDataMgr.stop()
                self.timer.Stop()
                self.Destroy()
        except Exception as err:
            gv.gDebugPrint("Error to close the UI: %s" %str(err), logType=gv.LOG_ERR)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        gv.iMainFrame = UIFrame(None, -1, gv.UI_TITLE)
        gv.iMainFrame.Show(True)
        return True

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
