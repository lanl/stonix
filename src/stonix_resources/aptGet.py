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

from subprocess import Popen,PIPE,call
from re import search
import traceback
from logdispatcher import LogPriority
from CommandHelper import CommandHelper
class AptGet(object):

    '''Linux specific package manager for distributions that use the apt-get
    command to install packages.

    :version:
    :author:Derek T Walker 08-06-2012'''

    def __init__(self, logger):
        self.logger = logger
        self.detailedresults = ""
        self.ch = CommandHelper(self.logger)
        self.install = "sudo DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get \
-y install "
        self.remove = "/usr/bin/apt-get -y remove "
###############################################################################
    def installpackage(self, package):
        '''Install a package. Return a bool indicating success or failure.

        @param string package : Name of the package to be installed, must be 
            recognizable to the underlying package manager.
        @return bool :
        @author dwalker'''
        try:
            self.ch.executeCommand(self.install + package)
            if self.ch.getReturnCode() == 0:
                self.detailedresults = package + " pkg installed successfully"
                self.logger.log(LogPriority.INFO,
                                ["AptGet.install",self.detailedresults])
                return True
            else:
                #try to install for a second time
                self.ch.executeCommand(self.install + package)
                if self.ch.getReturnCode() == 0:
                    self.detailedresults = package + " pkg installed successfully"
                    self.logger.log(LogPriority.INFO,
                                ["AptGet.install",self.detailedresults])
                    return True
                else:
                    self.detailedresults = package + " pkg not able to install"
                    self.logger.log(LogPriority.INFO,
                                    ["AptGet.install",self.detailedresults])
                    return False
        except(KeyboardInterrupt,SystemExit):
            raise
        except Exception, err:
            print err
            self.detailedresults = traceback.format_exc()
            self.logger.log(LogPriority.INFO,
                                       ["AptGet.install",self.detailedresults])
            raise(self.detailedresults)
###############################################################################
    def removepackage(self, package):
        '''Remove a package. Return a bool indicating success or failure.

        @param string package : Name of the package to be removed, must be 
            recognizable to the underlying package manager.
        @return bool :
        @author'''
        
        try:
            self.ch.executeCommand(self.remove + package)
            if self.ch.getReturnCode() == 0:
                self.detailedresults = package + " pkg removed successfully"
                self.logger.log(LogPriority.INFO, self.detailedresults)
                return True
            else:
                self.detailedresults = package + " pkg not able to be removed"
                self.logger.log(LogPriority.INFO, self.detailedresults)
                return False
        except(KeyboardInterrupt,SystemExit):
            raise
        except Exception, err:
            print err
            self.detailedresults = traceback.format_exc()
            self.logger.log(LogPriority.INFO, self.detailedresults)
            raise(self.detailedresults)
###############################################################################
    def checkInstall(self, package):
        '''Check the installation status of a package. Return a bool; True if 
        the package is installed.

        @param string package : Name of the package whose installation status 
            is to be checked, must be recognizable to the underlying package 
            manager.
        @return bool :
        @author'''
        
        try:
            stringToMatch = "(.*)" + package + "(.*)"
            self.ch.executeCommand(["/usr/bin/dpkg","-l",package])
            info = self.ch.getOutput()
            match = False
            for line in info:
                if search(stringToMatch,line):
                    parts = line.split()
                    if parts[0] == "ii":
                        match = True
                        break
                else:
                    continue
            if match:
                self.detailedresults = package + " pkg found and installed\n"
                self.logger.log(LogPriority.INFO, self.detailedresults)
                return True
            else:
                self.detailedresults = package + " pkg not installed\n"
                self.logger.log(LogPriority.INFO, self.detailedresults)
                return False
        except(KeyboardInterrupt,SystemExit):
            raise
        except Exception:
            self.detailedresults = traceback.format_exc()
            self.logger.log(LogPriority.INFO, self.detailedresults)
            raise(self.detailedresults)
###############################################################################
    def checkAvailable(self,package):
        try:
            found = False
            retval = call(["/usr/bin/apt-cache","search", package],stdout=PIPE,
                                                       stderr=PIPE,shell=False)
            if retval == 0:
                message = Popen(["/usr/bin/apt-cache","search",package],
                                        stdout=PIPE, stderr=PIPE,shell=False)
                info = message.stdout.readlines()
                while message.poll() is None:
                    continue
                message.stdout.close()
                for line in info:
                    if search(package,line):
                        found = True
                if found:
                    self.detailedresults = package + " pkg is available"
                else:
                    self.detailedresults = package + " pkg is not available"
            else:
                self.detailedresults = package + " pkg not found or may be \
misspelled"
            self.logger.log(LogPriority.INFO, self.detailedresults)
            return found
        except(KeyboardInterrupt,SystemExit):
            raise
        except Exception:
            self.detailedresults = traceback.format_exc()
            self.logger.log(LogPriority.INFO, self.detailedresults)
            raise
###############################################################################
    def getInstall(self):
        return self.install
###############################################################################
    def getRemove(self):
        return self.remove 
