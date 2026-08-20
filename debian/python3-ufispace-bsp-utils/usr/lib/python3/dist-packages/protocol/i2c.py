#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###########################################################################
#Copyright 2020 Ufi Space Co.,Ltd.                                        #
#                                                                         #
#Licensed under the Apache License, Version 2.0 (the "License");          #
#you may not use this file except in compliance with the License.         #
#You may obtain a copy of the License at                                  #
#                                                                         #
#    http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                         #
#Unless required by applicable law or agreed to in writing, software      #
#distributed under the License is distributed on an "AS IS" BASIS,        #
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#See the License for the specific language governing permissions and      #
#limitations under the License.                                           #
###########################################################################
import os
import sys
from smbus import SMBus
from protocol.lpc import LPC
from protocol.lpc import LPCDevType

from common.logger import Logger

class I2C:
    def __init__(self, busnum=0):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.busnum = busnum
        self.lpc = LPC()

    def check_status(self):
        try:
            hst_sts = self.lpc.regGet(LPCDevType.SMBUS_MEM,0x0)

            #bit 5 is in use, and bit 0 is host busy
            if (hst_sts & 0x01) != 0:
                self.logger.error("i2c bus is busy")
                return False
            else:
                return True
        except Exception as e:
            self.logger.error("Error to check I2C bus status, err:" + repr(e))
            return False
