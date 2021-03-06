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
@change: 10/16/2013 Original Implementation
@change: 02/12/2014 ekkehard Implemented self.detailedresults flow
@change: 02/12/2014 ekkehard Implemented isapplicable
@change: 04/09/2014 ekkehard Decription Update
@change: 07/21/2014 ekkehard added AllowPreReleaseInstallation
@change: 09/15/2014 ekkehard fixed CatalogURL string
@change: 2015/04/14 dkennel updated for new style isApplicable
'''
from __future__ import absolute_import
import re
import types
from ..ruleKVEditor import RuleKVEditor
from ..CommandHelper import CommandHelper
from ..localize import APPLESOFTUPDATESERVER


class ConfigureAppleSoftwareUpdate(RuleKVEditor):
    '''
    This Mac Only rule does three thing:
    To fix issue the following commands:

    1. Set the default Apple Software Update Server for the organization server
    defaults -currentHost write /Library/Preferences/com.apple.SoftwareUpdate CatalogURL http://apple.foo.com:8088/
    2. Disables AutomaticDownload:
    defaults -currentHost write /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload -bool no
    3. Disables AutomaticCheckEnabled:
    defaults -currentHost write /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled -bool no
    4. Disables AutomaticCheckEnabled:
    defaults -currentHost write /Library/Preferences/com.apple.SoftwareUpdate ConfigDataInstall -bool no
    5. Disables DisableCriticalUpdateInstall:
    defaults -currentHost write /Library/Preferences/com.apple.SoftwareUpdate DisableCriticalUpdateInstall -bool no
    6. Disables ability to install PreReleases:
    defaults -currentHost write /Library/Preferences/com.apple.SoftwareUpdate AllowPreReleaseInstallation -bool no

    1. defaults -currentHost read /Library/Preferences/com.apple.SoftwareUpdate CatalogURL
    2. defaults -currentHost read /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload
    3. defaults -currentHost read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled
    4. defaults -currentHost read /Library/Preferences/com.apple.SoftwareUpdate ConfigDataInstall
    5. defaults -currentHost read /Library/Preferences/com.apple.SoftwareUpdate DisableCriticalUpdateInstall
    6. defaults -currentHost read /Library/Preferences/com.apple.SoftwareUpdate AllowPreReleaseInstallation
    7. defaults -currentHost read /Library/Preferences/com.apple.SoftwareUpdate RecommendedUpdates
    
    OS X Yosemite considerations:
    defaults write /Library/Preferences/com.apple.commerce AutoUpdate -bool [TRUE|FALSE]
    defaults write /Library/Preferences/com.apple.commerce AutoUpdateRestartRequired -bool [TRUE|FALSE]

    @author: ekkehard j. koch
    '''

###############################################################################

    def __init__(self, config, environ, logdispatcher, statechglogger):
        RuleKVEditor.__init__(self, config, environ, logdispatcher,
                              statechglogger)
        self.rulenumber = 262
        self.rulename = 'ConfigureAppleSoftwareUpdate'
        self.formatDetailedResults("initialize")
        self.mandatory = True
        self.helptext = "This rules set the default to get software " + \
        "updates from " + str(APPLESOFTUPDATESERVER) + " disables the " + \
        "Check for Updates in the Software Update System Preference Panel " + \
        "for most users. Does not disable this option when the account is " + \
        "an admin account and the update server is set to the our ASUS " + \
        "server and disable the Download Updates in Background option of " + \
        "the Software Update System Preference Panel for most users. Does " + \
        "not disable this option when the account is an admin account and " + \
        "the update server is set to the our ASUS server."
        self.rootrequired = True
        self.guidance = ['CCE 14813-0', 'CCE 14914-6', 'CCE 4218-4',
                         'CCE 14440-2']
        self.isApplicableWhiteList = [{"0": "darwin",
                                       "1": "Mac OS X",
                                       "2": ["10.9", "10.10"]}]
        self.isApplicableBlackList = [{"0": "darwin",
                                       "1": "Mac OS X",
                                       "2": ["10.0", "10.1", "10.2", "10.3",
                                             "10.4", "10.5", "10.6", "10.7",
                                             "10.8"]}]
        self.applicable = {'type': 'white',
                           'os': {'Mac OS X': ['10.9', 'r', '10.10.10']}}
        self.addKVEditor("ConfigureCatalogURL",
                         "defaults",
                         "/Library/Preferences/com.apple.SoftwareUpdate",
                         "",
                         {"CatalogURL": [str(APPLESOFTUPDATESERVER),
                                         str(APPLESOFTUPDATESERVER)]},
                         "present",
                         "",
                         "Set software update server (CatalogURL) to '" +
                         str(APPLESOFTUPDATESERVER) +
                         "'. This should always be enabled. If disabled " + \
                         " it will point to the Apple Software Update " + \
                         "Server. NOTE: your system will report as not " + \
                         "compliant if you disable this option.",
                         None,
                         False,
                         {"CatalogURL":
                          [re.escape("The domain/default pair of (/Library" + \
                                     "/Preferences/com.apple.Software" + \
                                     "Update, CatalogURL) does not exist"),
                           None]})
        self.addKVEditor("DisableAutomaticDownload",
                         "defaults",
                         "/Library/Preferences/com.apple.SoftwareUpdate",
                         "",
                         {"AutomaticDownload": ["0", "-bool no"]},
                         "present",
                         "",
                         "Disable Automatic Software Update Downloads. " +
                         "This should be enabled.",
                         None,
                         False,
                         {"AutomaticDownload": ["1", "-bool yes"]})
        self.addKVEditor("DisableAutomaticCheckEnabled",
                         "defaults",
                         "/Library/Preferences/com.apple.SoftwareUpdate",
                         "",
                         {"AutomaticCheckEnabled": ["0", "-bool no"]},
                         "present",
                         "",
                         "Disable Automatic Checking For Downloads. " +
                         "This should be enabled.",
                         None,
                         False,
                         {"AutomaticCheckEnabled": ["1", "-bool yes"]})
        self.addKVEditor("DisableConfigDataInstall",
                         "defaults",
                         "/Library/Preferences/com.apple.SoftwareUpdate",
                         "",
                         {"ConfigDataInstall": ["0", "-bool no"]},
                         "present",
                         "",
                         "Disable Installing of system data files.",
                         None,
                         False,
                         {"ConfigDataInstall": ["1", "-bool yes"]})
        self.addKVEditor("DisableCriticalUpdateInstall",
                         "defaults",
                         "/Library/Preferences/com.apple.SoftwareUpdate",
                         "",
                         {"CriticalUpdateInstall": ["0", "-bool no"]},
                         "present",
                         "",
                         "Disable Installing of security updates.",
                         None,
                         False,
                         {"CriticalUpdateInstall": ["1", "-bool yes"]})
        self.addKVEditor("DisableAllowPreReleaseInstallation",
                         "defaults",
                         "/Library/Preferences/com.apple.SoftwareUpdate",
                         "",
                         {"AllowPreReleaseInstallation": ["0", "-bool no"]},
                         "present",
                         "",
                         "Disable Installation of Pre Release Software.",
                         None,
                         False,
                         {"AllowPreReleaseInstallation": ["1", "-bool yes"]})
        self.addKVEditor("RecommendedUpdates",
                         "defaults",
                         "/Library/Preferences/com.apple.SoftwareUpdate",
                         "",
                         {"RecommendedUpdates": [re.escape("(\n)\n"), None]},
                         "present",
                         "",
                         "List of recommended updates.",
                         None,
                         True,
                         {})
        self.ch = CommandHelper(self.logdispatch)
        self.softwareupdatehasnotrun = True

    def beforereport(self):
        success = True
        if self.softwareupdatehasnotrun:
# FIXME this is way to slow
            #success = self.ch.executeCommand("softwareupdate --list")
            self.softwareupdatehasnotrun = False
        else:
            success = True
        return success

###############################################################################

    def formatValue(self, pValue):
        outputvalue = pValue
        datatype = type(outputvalue)
        if datatype == types.StringType:
            if not (outputvalue == ""):
                outputvalue = re.sub("\\\\n|\(|\)|\,|\'", "", outputvalue)
                outputvalue = re.sub("\s+", " ", outputvalue)
        elif datatype == types.ListType:
            for i, item in enumerate(outputvalue):
                item = re.sub("\\\\n|\(|\)|\,|\'", "", item)
                item = re.sub("\s+", " ", item)
                outputvalue[i] = item
        else:
            outputvalue = outputvalue
        return outputvalue
