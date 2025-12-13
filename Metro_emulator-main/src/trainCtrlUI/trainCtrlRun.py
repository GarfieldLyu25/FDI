#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        TrainCtrlRun.py
#
# Purpose:     This module is the main wx-frame for the metro trains controller
#              sysetm HMI to display the trian state information and change the 
#              trains setting. 
#
# Author:      Yuancheng Liu
#
# Version:     v0.1.3
# Created:     2023/07/12
# Copyright:   Copyright (c) 2023 Singapore National Cybersecurity R&D Lab LiuYuancheng
# License:     MIT License 
#-----------------------------------------------------------------------------

import os
import time

import wx

import trainCtrlGlobal as gv
import trainCtrlPanel as pnlFunction
import trainDataMgr as dataMgr

FRAME_SIZE = (1860, 1000)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class UIFrame(wx.Frame):
    """ Main UI frame window."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters, No boader frame."""
        wx.Frame.__init__(self, parent, id, title, size=FRAME_SIZE)
        self.SetBackgroundColour(wx.Colour(39, 40, 62))
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        self._initGlobals()
        # Build UI sizer
        self._buildMenuBar()
        self.SetSizer(self._buidUISizer())
        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText('Test mode: %s' % str(gv.TEST_MD))
        # Init the local parameters:
        self.updateLock = False
        self.plcOnline = True if gv.TEST_MD else False
        self.rtuOnline = True if gv.TEST_MD else False
        # Turn on all the trains power during init.
        self.loadTrainsPwrConfig()
        # Load the auto collision config setting 
        self.loadAutoCAConfig()
        # update the plc connection indicator
        self.updatePlcConIndicator()
        # Set the periodic call back
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(gv.PERIODIC)  # every 500 ms
        self.Bind(wx.EVT_CLOSE, self.onClose)

#-----------------------------------------------------------------------------
    def _initGlobals(self):
        """ Init the global parameters used only by this module."""
        gv.gTrackConfig['weline'] = {'id': 'weline', 'num': 4,
                                     'trainHregIdx': (0, 4),
                                     'trainCoilIdx': (0, 4),
                                     'rtuMemIdxList': [1, 2, 3, 4],
                                     'color': wx.Colour(52, 169, 129),
                                     'icon': 'welabel.png'}

        gv.gTrackConfig['nsline'] = {'id': 'nsline', 'num': 3,
                                     'trainHregIdx': (4, 7),
                                     'trainCoilIdx': (4, 7),
                                     'rtuMemIdxList': [5, 6, 7],
                                     'color': wx.Colour(233, 0, 97),
                                     'icon': 'nslabel.png'}

        gv.gTrackConfig['ccline'] = {'id': 'ccline', 'num': 3,
                                     'trainHregIdx': (7, 10),
                                     'trainCoilIdx': (7, 10),
                                     'rtuMemIdxList': [8, 9, 10],
                                     'color': wx.Colour(255, 136, 0),
                                     'icon': 'cclabel.png'}
        # Init the display manager 
        gv.iMapMgr = dataMgr.MapManager(self)
        # Init the data manager if we are under real mode.(need to connect to PLC module.)
        if not gv.TEST_MD: gv.idataMgr = dataMgr.DataManager(self, gv.gPlcInfo)

#-----------------------------------------------------------------------------
    def _initElectricalLbs(self):
        """ Init the plc digital in and digital out labels."""
        self.digitalInLBList = {}
        self.digitalOutLBList = {}
        welineColor = gv.gTrackConfig['weline']['color']
        nslineColor = gv.gTrackConfig['nsline']['color']
        cclineColor = gv.gTrackConfig['ccline']['color']

        self.digitalInLBList['PLC-06'] = []
        for i in range(0, 4):
            data = {'item': 'weS'+str(i).zfill(2), 'color': welineColor}
            self.digitalInLBList['PLC-06'].append(data)

        for i in range(0, 3):
            data = {'item': 'nsS'+str(i).zfill(2), 'color': nslineColor}
            self.digitalInLBList['PLC-06'].append(data)

        for i in range(0, 1):
            data = {'item': 'ccS'+str(i).zfill(2), 'color': cclineColor}
            self.digitalInLBList['PLC-06'].append(data)

        self.digitalOutLBList['PLC-06'] = []
        for i in range(0, 4):
            data = {'item': 'weP'+str(i).zfill(2), 'color': welineColor}
            self.digitalOutLBList['PLC-06'].append(data)

        for i in range(0, 3):
            data = {'item': 'nsP'+str(i).zfill(2), 'color': nslineColor}
            self.digitalOutLBList['PLC-06'].append(data)

        for i in range(0, 1):
            data = {'item': 'ccP'+str(i).zfill(2), 'color': cclineColor}
            self.digitalOutLBList['PLC-06'].append(data)

        self.digitalInLBList['PLC-07'] = []
        for i in range(2, 4):
            data = {'item': 'ccS'+str(i).zfill(2), 'color': cclineColor}
            self.digitalInLBList['PLC-07'].append(data)

        self.digitalOutLBList['PLC-07'] = []
        for i in range(2, 4):
            data = {'item': 'ccP'+str(i).zfill(2), 'color': cclineColor}
            self.digitalOutLBList['PLC-07'].append(data)

        # Append the collision avidance control
        data = {'item': 'ca_on', 'color': wx.Colour(140, 170, 220)}
        self.digitalOutLBList['PLC-07'].append(data)


#-----------------------------------------------------------------------------
    def _buildMenuBar(self):
        menubar = wx.MenuBar()  # Creat the function menu bar.
        # Add the config menu
        pass
        # Add the about menu.
        helpMenu = wx.Menu()
        aboutItem = wx.MenuItem(helpMenu, 120, text='Help', kind=wx.ITEM_NORMAL)
        helpMenu.Append(aboutItem)
        self.Bind(wx.EVT_MENU, self.onHelp, aboutItem)
        menubar.Append(helpMenu, '&About')
        self.SetMenuBar(menubar)

#-----------------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI Sizer. """
        flagsL = wx.LEFT
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        mSizer.AddSpacer(10)
        # column 0: panel to display all the trains information gauage 
        mSizer.Add(self._buildTrainGaugeSizer(), flag=flagsL, border=2)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 900),
                    style=wx.LI_VERTICAL), flag=flagsL, border=2)
        # column 1: information panel, plc panel and config change panel.
        vbox0 = wx.BoxSizer(wx.VERTICAL)
        vbox0.AddSpacer(5)
        # c1,r0 : time display
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        timeStr = 'Date and Time : ' + time.strftime(' %Y - %m - %d %H : %M : %S ',time.localtime(time.time()))
        self.timeInfo = wx.StaticText(self, label=timeStr)
        self.timeInfo.SetFont(font)
        self.timeInfo.SetForegroundColour(wx.Colour("WHITE"))
        vbox0.Add(self.timeInfo, flag=flagsL, border=2)
        vbox0.AddSpacer(5)

        #
        label2 = wx.StaticText(self, label="RTU [S7Comm] Monitor Panel")
        label2.SetFont(font)
        label2.SetForegroundColour(wx.Colour("WHITE"))
        vbox0.Add(label2, flag=flagsL, border=2)
        vbox0.AddSpacer(5)
        gv.iRtuPanel = pnlFunction.PanelRTU(self, gv.RTU_ID, gv.RTU_IP+ ' : ' + str(gv.RTU_PORT))
        vbox0.Add(gv.iRtuPanel, flag=flagsL, border=2)
        
        # c1, r1: information panel.
        gv.iInfoPanel = pnlFunction.PanelTrainInfo(self)
        vbox0.Add(gv.iInfoPanel, flag=flagsL, border=2)
        vbox0.AddSpacer(5)
        # c1, r2: Plca dispaly sizer
        self.plcPnls = {}
        self._initElectricalLbs()
        plcSZ = self._buildPlcPnlsSizer("PLC [Modbus] Monitor Panels", 
                                    ('PLC-06', 'PLC-07'))
        vbox0.Add(plcSZ, flag=flagsL, border=2)
        vbox0.AddSpacer(5)
        # # c1, r3: config change control sizer.
        ctrlSZ = self._buildControlSizer()
        vbox0.Add(ctrlSZ, flag=flagsL, border=2)
        mSizer.Add(vbox0, flag=flagsL, border=2)
        return mSizer

#-----------------------------------------------------------------------------
    def _buildTrainGaugeSizer(self):
        """ Sizer contents 10 train gauges and 2 place holders to show the trains
            information.
        """
        flagsL = wx.LEFT
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        rowMax = 4 # max number of train panels can be shown in one row.
        # Init the sizers.
        vbox0 = wx.BoxSizer(wx.VERTICAL)
        vbox0.AddSpacer(5)
        # Add the label
        label = wx.StaticText(self, label="Trains Operational State")
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour("WHITE"))
        vbox0.Add(label, flag=flagsL, border=2)
        vbox0.AddSpacer(5)
        # Init and add the train gauge panels.
        self.trainPnlDict = {}
        for key, panelCfg in gv.gTrackConfig.items():
            self.trainPnlDict[key] = []
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            for i in range(rowMax):
                if i < panelCfg['num']:
                    bgcolor, ftcolor = panelCfg['color'], wx.Colour('WHITE')
                    trainPanel = pnlFunction.PanelTrain(self, panelCfg['id'], i, 
                                                        bgColour=bgcolor,
                                                        fontColour=ftcolor)
                    self.trainPnlDict[key].append(trainPanel)
                    hbox.Add(trainPanel, flag=flagsL, border=2)
                else:
                    placeholder = self._getBitMap('placeHolder.png')
                    if placeholder: hbox.Add(placeholder, flag=flagsL, border=2)
                hbox.AddSpacer(5)
            vbox0.Add(hbox, flag=flagsL, border=2)
            vbox0.AddSpacer(10)
        return vbox0

#-----------------------------------------------------------------------------
    def _buildPlcPnlsSizer(self, PanelTitle, panelKeySeq):
        """ Create the sizer contents 2 PLC panel.
            Args:
                PanelTitle (str): Panel title
                panelKeySeq (list(str)): plc sequence. example: ('PLC-00', 'PLC-01', 'PLC-02')
        """
        flagsL = wx.LEFT
        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.AddSpacer(5)
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        label = wx.StaticText(self, label=PanelTitle)
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour("WHITE"))
        vSizer.Add(label, flag=flagsL, border=2)
        vSizer.AddSpacer(5)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        for key in panelKeySeq:
            hbox1.AddSpacer(10)
            panelInfo = gv.gPlcPnlInfo[key]
            ipaddr = panelInfo['ipaddress'] + ' : ' + str(panelInfo['port'])
            dInInfoList =  self.digitalInLBList[key] if key in self.digitalInLBList.keys() else None
            dOutInfoList = self.digitalOutLBList[key] if key in self.digitalOutLBList.keys() else None
            self.plcPnls[key] = pnlFunction.PanelPLC(self, panelInfo['label'], ipaddr, 
                                                     dInInfoList=dInInfoList,
                                                     dOutInfoList=dOutInfoList)
            hbox1.Add(self.plcPnls[key], flag=flagsL, border=2)
        vSizer.Add(hbox1, flag=flagsL, border=2)
        return vSizer
    
#-----------------------------------------------------------------------------
    def _buildControlSizer(self):
        """ Build the train config control sizer."""
        flagsL = wx.LEFT
        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.AddSpacer(5)
        # Add the title
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        label = wx.StaticText(self, label= "Control Panel")
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour("WHITE"))
        vSizer.Add(label, flag=flagsL, border=2)
        vSizer.AddSpacer(5)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        caLabel = wx.StaticText(self, label= "> Trains Collision Auto-Avoidance:")
        caLabel.SetFont(font)
        caLabel.SetForegroundColour(wx.Colour("WHITE"))
        hbox1.Add(caLabel, flag=flagsL, border=2)
        hbox1.AddSpacer(10)
        self.caCombo = wx.ComboBox(self,choices = ('Enable', 'Disable')) 
        self.caCombo.SetSelection(0)
        hbox1.Add(self.caCombo, flag=flagsL, border=2)
        self.caCombo.Bind(wx.EVT_COMBOBOX, self.onChangeCA) 
        vSizer.Add(hbox1, flag=flagsL, border=2)
        return vSizer
    
#-----------------------------------------------------------------------------
    def _getBitMap(self, fileName, scale=None):
        """ get the <wx.StaticBitmap> from the img, if img not exist return None."""
        img = os.path.join(gv.IMG_FD, fileName)
        if os.path.exists(img):
            png = wx.Image(img, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            imgSize =  (png.GetWidth(), png.GetHeight()) if scale is None else scale
            bitmap = wx.StaticBitmap(self, -1, png, (0, 0), imgSize)
            return bitmap
        else:
            gv.gDebugPrint("The image file %s is not in exist" %fileName, logType=gv.LOG_WARN)
            return None

#-----------------------------------------------------------------------------
    def loadTrainsPwrConfig(self):
        """ Load the pre-configured trains' power state to the PLC."""   
        if gv.idataMgr is None: return False
        gv.gDebugPrint('Power all the trains power state to PLC', logType=gv.LOG_INFO)
        csIdx, ceIdx = (0, 10)
        for idx in range(csIdx, ceIdx):
            state = gv.gTrainsPwrList[idx] if idx < len(gv.gTrainsPwrList) else False
            gv.idataMgr.setPlcCoilsData(gv.PLC_ID, idx, state)
        return True

#-----------------------------------------------------------------------------
    def loadAutoCAConfig(self):
        """ Load the pre-configured collision avoidance control state to the PLC."""   
        self.caCombo.SetSelection(0 if gv.gAutoCA else 1)
        if gv.idataMgr is None: return False
        gv.gDebugPrint('Chage the collision avoidance config', logType=gv.LOG_INFO)
        idx = 10
        gv.idataMgr.setPlcCoilsData(gv.PLC_ID, idx, gv.gAutoCA)
        return True

#-----------------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        now = time.time()
        if (not self.updateLock) and now - self.lastPeriodicTime >= gv.gUpdateRate:
            print("main frame update at %s" % str(now))
            self.lastPeriodicTime = now
            if (not gv.TEST_MD) and gv.idataMgr:
                # real module step 1: get data frome PLCs module.
                gv.idataMgr.periodic(now)
                # real module step 2: Update the Plc display
                self.updatePlcConIndicator()
                if self.plcOnline: self.updatePlcPanels()
                # real module step 3: mapping the plc info to trains info.
                self.updateRtuConIndicator()
                if self.rtuOnline: self.updateTrainsInfo()

            # Update the train inforation grid.
            if gv.iMapMgr and self.rtuOnline: 
                gv.iInfoPanel.updateTrainInfoGrid()
                self.updateTrainsPanels()
            if (not gv.TEST_MD) and self.rtuOnline:
                gv.iRtuPanel.updateSenIndicator()
            
            # update time display
            timeStr = 'Date and time : ' + time.strftime(' %Y - %m - %d %H : %M : %S ',time.localtime(time.time()))
            self.timeInfo.SetLabel(timeStr)

#-----------------------------------------------------------------------------
    def updatePlcConIndicator(self):
        """ Update the PLC's state panel connection state."""
        if gv.idataMgr is None: return False
        self.plcOnline = gv.idataMgr.getPlcConntionState(gv.PLC_ID)
        for plcPanel in self.plcPnls.values():
            plcPanel.setConnection(self.plcOnline)
        return True
    
    def updateRtuConIndicator(self):
        if gv.idataMgr is None: return False 
        self.rtuOnline = gv.idataMgr.getRtuConnectionState()
        gv.iRtuPanel.setConnection(self.rtuOnline)

#-----------------------------------------------------------------------------
    def updatePlcPanels(self):
        if gv.idataMgr is None: return False
        for key in self.plcPnls.keys():
            tgtPlcID = gv.gPlcPnlInfo[key]['tgt']
            # update the holding registers
            rsIdx, reIdx = gv.gPlcPnlInfo[key]['hRegsInfo']
            registList = gv.idataMgr.getPlcHRegsData(tgtPlcID, rsIdx, reIdx)
            self.plcPnls[key].updateHoldingRegs(registList)
            # update the coils
            csIdx, ceIdx = gv.gPlcPnlInfo[key]['coilsInfo']
            coilsList = gv.idataMgr.getPlcCoilsData(tgtPlcID, csIdx, ceIdx)
            self.plcPnls[key].updateCoils(coilsList)
            # update the UI display
            self.plcPnls[key].updateDisplay()

#-----------------------------------------------------------------------------
    def updateTrainsInfo(self):
        """ Convert the PLC information to trains information and update the 
            map manager.
        """
        regdataList = gv.idataMgr.getAllPlcRegsData()
        coildataList = gv.idataMgr.getAllPlcCoisData()
        rtuDataDict = gv.idataMgr.getAllRtuDataDict()
        for key in gv.gTrackConfig.keys():
            rsIdx, reIdx = gv.gTrackConfig[key]['trainHregIdx']
            gv.iMapMgr.updateTrainsThrottle(key, regdataList[rsIdx:reIdx])
            csIdx, ceIdx = gv.gTrackConfig[key]['trainCoilIdx']
            gv.iMapMgr.updateTrainsPwr(key, coildataList[csIdx:ceIdx])
            gv.iMapMgr.updateTrainsSensor(key, rtuDataDict[key])

#-----------------------------------------------------------------------------
    def updateTrainsPanels(self):
        """ Update all the trains gauage display."""
        for key in gv.gTrackConfig.keys():
            trainsInfo = gv.iMapMgr.getTrainsInfo(key)
            for i, data in enumerate(trainsInfo):
                self.trainPnlDict[key][i].updateState(data)

#-----------------------------------------------------------------------------
    def onHelp(self, event):
        """ Pop-up the Help information window. """
        wx.MessageBox(' If there is any bug, please contact: \n\n \
                        Author:      Yuancheng Liu \n \
                        Email:       liu_yuan_cheng@hotmail.com \n \
                        Created:     2023/07/20 \n \
                        GitHub Link: https://github.com/LiuYuancheng/Metro_emulator \n', 
                    'Help', wx.OK)

#-----------------------------------------------------------------------------
    def onChangeCA(self, event):
        """ Change the collision avoidance setting.
        """
        if gv.idataMgr:
            state = 'Enable' if self.caCombo.GetSelection() == 0 else 'Disable'
            dlg = wx.MessageDialog(None, "Confirm Change Trains Collision Auto-Avoidance",
                                            ' %s Trains Collision Auto-Avoidance' %str(state),wx.YES_NO | wx.ICON_WARNING)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                val = self.caCombo.GetSelection() == 0
                TrainTgtPlcID = 'PLC-06'
                gv.idataMgr.setPlcCoilsData(TrainTgtPlcID, 10, val)

#-----------------------------------------------------------------------------
    def onClose(self, evt):
        """ Pop up the confirm close dialog when the user close the UI from 'x'."""
        try:
            fCanVeto = evt.CanVeto()
            if fCanVeto:
                confirm = wx.MessageDialog(self, 'Click [ OK ] to close this program, or click [ Cancel ] to ignore close request',
                                            'Quit request', wx.OK | wx.CANCEL| wx.ICON_WARNING).ShowModal()
                if confirm == wx.ID_CANCEL:
                    evt.Veto(True)
                    return
                if gv.idataMgr: gv.idataMgr.stop()
                self.timer.Stop()
                self.Destroy()
        except Exception as err:
            gv.gDebugPrint("Error to close the UI: %s" %str(err), logType=gv.LOG_ERR)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class TrainCtrlHMIApp(wx.App):
    def OnInit(self):
        gv.iMainFrame = UIFrame(None, -1, gv.UI_TITLE)
        gv.iMainFrame.Show(True)
        return True

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app = TrainCtrlHMIApp(0)
    app.MainLoop()
