###############################################################################
#                                                                             #
# Copyright 2015.  Los Alamos National Security, LLC. This material was       #
# produced under U.S. Government contract DE-AC52-06NA25396 for Los Alamos    #
# National Laboratory (LANL), which is operated by Los Alamos National        #
# Security, LLC for the U.S. Department of Energy. The U.S. Government has    #
# rights to use, reproduce, and distribute this software.  NEITHER THE        #
# GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY,        #
# EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  #
# If software is modified to produce derivative works, such modified software #
# should be clearly marked, so as not to confuse it with the version          #
# available from LANL.                                                        #
#                                                                             #
# Additionally, this program is free software; you can redistribute it and/or #
# modify it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; either version 2 of the License, or (at your  #
# option) any later version. Accordingly, this program is distributed in the  #
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the     #
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    #
# See the GNU General Public License for more details.                        #
#                                                                             #
###############################################################################
'''
This method runs all the report methods for RuleKVEditors in defined in the
dictionary

@author: ekkehard j. koch
@change: 2014-08-27 - ekkehard - Original Implementation
@change: 2014-10-17 ekkehard OS X Yosemite 10.10 Update
@change: 2015-02-15 ekkehard - Artifact artf35701 : COSMETIC - ConfigurePowerManagement - Poor help text 
@change: 2015/04/14 dkennel updated to use new isApplicable
'''
from __future__ import absolute_import
import traceback
import types
from ..rule import Rule
from ..CommandHelper import CommandHelper
from ..logdispatcher import LogPriority


class ConfigurePowerManagement(Rule):
    '''
    This Mac Only rule does the following:
    - Sets the Mac to stay awake if power is plugged-in.
    - Set the display to sleep after 30 minutes if inactivity (if plugged-in) or after 15 minutes of inactivity (if on laptop battery power)
    - Sets the hard drives to sleep after ten minutes of inactivity.
    - Sets the computer not to wake up if the computer is connected to a phone modem and the phone rings.
    - Sets the hard drives to sleep after ten minutes of inactivity.
    - Sets the computer not to wake up if the computer is connected to a phone modem and the phone rings.
    - Sets the Mac's wake-on-magic-ping option (Wake for Network Access or WakeOnLAN) off.
    - Disables the Start up automatically after a power failure feature in the Energy Saver System Pref. This feature is not available on all computers. This rule should be called disableAutoRestart, but it's not. Sorry.

    @author: ekkehard j. koch
    '''

###############################################################################

    def __init__(self, config, environ, logdispatcher, statechglogger):
        Rule.__init__(self, config, environ, logdispatcher,
                              statechglogger)
        self.rulenumber = 258
        self.rulename = 'ConfigurePowerManagement'
        self.formatDetailedResults("initialize")
        self.mandatory = True
        self.helptext = "Set the power setting to optimize battery usage " +\
        "or computer performance depending on user's current setup."
        self.rootrequired = True
        self.guidance = []
        self.applicable = {'type': 'white',
                           'os': {'Mac OS X': ['10.9', 'r', '10.10.10']}}
        self.psconfiguration = \
        {"ACDisableSystemSleep":
         {"HelpText": "Sets the Mac to stay awake if power is plugged-in. Default(AC Power, sleep, 0).",
          "PowerType": "AC Power",
          "PowerSetting": "sleep",
          "PowerSettingValue": 0,
          "PowerSettingMinimum": 0,
          "PowerSettingMaximum": 60},
         "ACDisplaySleep":
         {"HelpText": "Set Display Sleep  minutes on AC Power. Default(AC Power, displaysleep, 30).",
          "PowerType": "AC Power",
          "PowerSetting": "displaysleep",
          "PowerSettingValue": 30,
          "PowerSettingMinimum": 0,
          "PowerSettingMaximum": 60},
         "BatteryDisplaySleep":
         {"HelpText": "Set Display Sleep minutes on Battery Power. Default(Battery Power, displaysleep, 15).",
          "PowerType": "Battery Power",
          "PowerSetting": "displaysleep",
          "PowerSettingValue": 15,
          "PowerSettingMinimum": 0,
          "PowerSettingMaximum": 60},
         "ACDiskSleep":
         {"HelpText": "Set Disk Sleep minutes on AC Power. Default(AC Power, disksleep, 10).",
          "PowerType": "AC Power",
          "PowerSetting": "displaysleep",
          "PowerSettingValue": 10,
          "PowerSettingMinimum": 0,
          "PowerSettingMaximum": 60},
         "BatteryDiskSleep":
         {"HelpText": "Set Disk Sleep minutes on Battery Power. Default(Battery Power, disksleep, 10).",
          "PowerType": "Battery Power",
          "PowerSetting": "displaysleep",
          "PowerSettingValue": 10,
          "PowerSettingMinimum": 0,
          "PowerSettingMaximum": 60}
         }
        self.ci = {}
        index = -1
        for pslabel, psinfo in sorted(self.psconfiguration.items()):
            datatype = 'int'
            key = pslabel
            instructions = psinfo["HelpText"]
            defaultInteger = psinfo["PowerSettingValue"]
            index = index + 1
            self.ci[pslabel] = self.initCi(datatype, key, instructions, defaultInteger)
        self.pmset = "/usr/bin/pmset"
        self.psd = {}
        self.ch = CommandHelper(self.logdispatch)

    def report(self):
        '''
        Go through power settings dictionary and see if they match
        @param self:essential if you override this definition
        @return: boolean - true if applicable false if not
        '''
        try:
            self.detailedresults = ""
            self.compliant = True
            for pslabel, psinfo in sorted(self.psconfiguration.items()):
                powerType = psinfo["PowerType"]
                powerSetting = psinfo["PowerSetting"]
                powerSettingValue = psinfo["PowerSettingValue"]
                if powerSettingValue == self.getPowerSetting(powerType, powerSetting):
                    self.resultAppend(pslabel + " is compliant.")
                else:
                    self.resultAppend(pslabel + " is not compliant!")
                    self.compliant = False
        except (KeyboardInterrupt, SystemExit):
            # User initiated exit
            raise
        except Exception, err:
            self.rulesuccess = False
            self.detailedresults = self.detailedresults + "\n" + str(err) + \
            " - " + str(traceback.format_exc())
            self.logdispatch.log(LogPriority.ERROR, self.detailedresults)
        self.formatDetailedResults("report", self.compliant,
                                   self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return self.compliant

###############################################################################

    def fix(self):
        '''
        Go through power settings and fix the one we are supposed to
        @param self:essential if you override this definition
        @return: boolean - true if applicable false if not
        '''
        try:
            self.detailedresults = ""
            success = True
            for pslabel, psinfo in sorted(self.psconfiguration.items()):
                powerType = psinfo["PowerType"]
                powerSetting = psinfo["PowerSetting"]
                powerSettingValue = psinfo["PowerSettingValue"]
                if powerSettingValue == self.getPowerSetting(powerType, powerSetting):
                    self.resultAppend(pslabel + " was correctly set.")
                else:
                    if self.ci[pslabel].getcurrvalue() == True:
                        newPowerSettingValue = self.setPowerSetting(powerType, powerSetting)
                        if newPowerSettingValue == self.getPowerSetting(powerType, powerSetting):
                            self.resultAppend(pslabel + " is now compliant!")
                        else:
                            self.resultAppend(pslabel + " setting still not compliant!")
                            success = False
                    else:
                        self.resultAppend(pslabel + " configuration item set to False!")
            self.rulesuccess = success
        except (KeyboardInterrupt, SystemExit):
            # User initiated exit
            raise
        except Exception, err:
            self.rulesuccess = False
            self.detailedresults = self.detailedresults + "\n" + str(err) + \
            " - " + str(traceback.format_exc())
            self.logdispatch.log(LogPriority.ERROR, self.detailedresults)
        self.formatDetailedResults("report", self.compliant,
                                   self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return self.compliant

###############################################################################

    def initializePowerSetting(self, forceUpdate=False):
        if forceUpdate:
            self.psd = {}
        if self.psd == {}:
            itemType = ""
            item = {}
            command = [self.pmset, "-g", "disk"]
            self.ch.executeCommand(command)
            for line in self.ch.getOutput():
                linestripped = line.strip()
                values = linestripped.split()
                if linestripped == "Battery Power:":
                    if not itemType == "":
                        self.psd[itemType] = item
                        item = {}
                    itemType = "Battery Power"
                elif linestripped == "AC Power:":
                    if not itemType == "":
                        self.psd[itemType] = item
                        item = {}
                    itemType = "AC Power"
                elif not itemType == "":
                    name = ""
                    for namepart in values[:-1]:
                        name = name + " " + str(namepart)
                    name = name.strip()
                    value = str(values[-1])
                    item[name] = str(value)
            if not itemType == "":
                self.psd[itemType] = item

    def getPowerSetting(self, powerType, powerSetting, forceUpdate=False):
        self.initializePowerSetting(forceUpdate)
        powerSettingValue = self.psd[powerType][powerSetting]
        return powerSettingValue

    def setPowerSetting(self, powerType, powerSetting, powerSettingValue):
        success = False
        if not powerSettingValue == self.getPowerSetting(powerType, powerSetting):
            if powerType == "Battery Power":
                command = [self.pmset, "-b", powerSetting, powerSettingValue]
                self.ch.executeCommand(command)
            elif powerType == "AC Power":
                command = [self.pmset, "-c", powerSetting, powerSettingValue]
                self.ch.executeCommand(command)
            if powerSettingValue == self.getPowerSetting(powerType, powerSetting):
                success = True
        else:
            success = True
        return success

    def resultAppend(self, pMessage=""):
        '''
        reset the current kveditor values to their defaults.
        @author: ekkehard j. koch
        @param self:essential if you override this definition
        @return: boolean - true
        @note: kveditorName is essential
        '''
        datatype = type(pMessage)
        if datatype == types.StringType:
            if not (pMessage == ""):
                messagestring = pMessage
                if (self.detailedresults == ""):
                    self.detailedresults = messagestring
                else:
                    self.detailedresults = self.detailedresults + "\n" + \
                    messagestring
        elif datatype == types.ListType:
            if not (pMessage == []):
                for item in pMessage:
                    messagestring = item
                    if (self.detailedresults == ""):
                        self.detailedresults = messagestring
                    else:
                        self.detailedresults = self.detailedresults + "\n" + \
                        messagestring
        else:
            raise TypeError("pMessage with value" + str(pMessage) + \
                            "is of type " + str(datatype) + " not of " + \
                            "type " + str(types.StringType) + \
                            " or type " + str(types.ListType) + \
                            " as expected!")
