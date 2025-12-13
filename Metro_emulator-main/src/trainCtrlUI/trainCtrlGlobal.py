#-----------------------------------------------------------------------------
# Name:        trainCtrlGlobal.py
#
# Purpose:     This module is used as a local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2010/08/26
# Version:     v0.1.2
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License  
#-----------------------------------------------------------------------------
"""
For good coding practice, follow the following naming convention:
    1) Global variables should be defined with initial character 'g'
    2) Global instances should be defined with initial character 'i'
    2) Global CONSTANTS should be defined with UPPER_CASE letters
"""

import os, sys
import platform
import json
from collections import OrderedDict

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(__file__)
print("Current source code location : %s" % dirpath)
APP_NAME = ('TrainCtrl', 'HMI')

TOPDIRS = ['src', 'rail']
LIBDIR = 'lib'
CONFIG_FILE_NAME = 'trainHMIConfig.txt'

#-----------------------------------------------------------------------------
# Init the logger:
# find the lib directory
for topdir in TOPDIRS:
    idx = dirpath.find(topdir)
    gTopDir = dirpath[:idx + len(topdir)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
    # Config the lib folder 
    gLibDir = os.path.join(gTopDir, LIBDIR)
    if os.path.exists(gLibDir):
        print("Import all the lib-module from folder : %s" %str(gLibDir))
        sys.path.insert(0, gLibDir)
        break
    
import Log
Log.initLogger(gTopDir, 'Logs', APP_NAME[0], APP_NAME[1], historyCnt=100, fPutLogsUnderDate=True)

# Set the S7comm dll lib
gS7snapDllPath = os.path.join(dirpath, 'snap7.dll') if platform.system() == 'Windows' else None

# Init the log type parameters.
DEBUG_FLG   = False
LOG_INFO    = 0
LOG_WARN    = 1
LOG_ERR     = 2
LOG_EXCEPT  = 3
# init the log print module.
def gDebugPrint(msg, prt=True, logType=None):
    if prt: print(msg)
    if logType == LOG_WARN:
        Log.warning(msg)
    elif logType == LOG_ERR:
        Log.error(msg)
    elif logType == LOG_EXCEPT:
        Log.exception(msg)
    elif logType == LOG_INFO or DEBUG_FLG:
        Log.info(msg)

#-----------------------------------------------------------------------------
# Init the configure file loader.
import ConfigLoader
gGonfigPath = os.path.join(dirpath, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gGonfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gGonfigPath))
    exit()
CONFIG_DICT = iConfigLoader.getJson()

#------<IMAGES PATH>-------------------------------------------------------------
IMG_FD = os.path.join(dirpath, 'img')
ICO_PATH = os.path.join(IMG_FD, "metro.ico")
TEST_MD = CONFIG_DICT['TEST_MD']    # test mode flag, True: the simulator will operate with control logic itself. 
PERIODIC = 500      # update the main in every 500ms

PLC_ID = CONFIG_DICT['PLC_ID']
PLC_IP = CONFIG_DICT['PLC_IP']
PLC_PORT = int(CONFIG_DICT['PLC_PORT'])

RTU_ID = CONFIG_DICT['RTU_ID']
RTU_IP = CONFIG_DICT['RTU_IP']
RTU_PORT = int(CONFIG_DICT['RTU_PORT'])

UI_TITLE = CONFIG_DICT['UI_TITLE']

#-------<GLOBAL VARIABLES (start with "g")>------------------------------------
# VARIABLES are the built in data type.
gTrackConfig = OrderedDict()

# The PLC module's information
gPlcInfo = OrderedDict()
gPlcInfo['PLC-06'] = {'id': PLC_ID, 'ipaddress': PLC_IP, 'port': PLC_PORT, 
                      'hRegsInfo': (0, 10), 'coilsInfo': (0, 10)}

# Init the plc display panel data fetching mapping information.
gPlcPnlInfo = OrderedDict()
gPlcPnlInfo['PLC-06'] = {'id': 'PLC-06', 'label': 'PLC-06[Master:slot-0]', 
                         'ipaddress': PLC_IP, 'port': PLC_PORT, 'tgt': PLC_ID, 
                         'hRegsInfo': (0, 8), 'coilsInfo': (0, 8)}

gPlcPnlInfo['PLC-07'] = {'id': 'PLC-07', 'label': 'PLC-07[Slave:slot-1]', 
                         'ipaddress': PLC_IP, 'port': PLC_PORT, 'tgt': PLC_ID, 
                         'hRegsInfo': (8, 10), 'coilsInfo': (8, 11)}
# main frame update rate every 2 sec.
gUpdateRate = float(CONFIG_DICT['CLK_INT'])
gTrainsPwrList = json.loads(CONFIG_DICT['TRAINS_PWR'])
gAutoCA = CONFIG_DICT['AUTO_CA']

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
iMainFrame = None   # UI MainFrame.
iInfoPanel = None   # UI map display panel
iRtuPanel = None    
iMapMgr = None      # manager module to control all the compontents displayed on UI
idataMgr = None     # manager module to process all the data.