#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###########################################################################
#Copyright 2019 Ufi Space Co.,Ltd.                                        #
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

from common.logger import Logger
from eeprom.eeprom import EEPRom
from const.const import PortStatus
from gpio.ioexp import IOExpander
from cpld.cpld import CPLD
from protocol.i2c import I2C


class EEPRomUtility:

    SFP_VALID_PORTS  = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27)
    QSFP_VALID_PORTS = (0, 1)

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.eeprom = EEPRom()
        self.ioexp = IOExpander()

    def dump_cpu_eeprom(self):
        try:
            content = self.eeprom.dump_cpu_eeprom()

            return {"content":content}
        except Exception as e:
            raise

    def dump_sfp_eeprom(self, port_num, page = None):
        try:
            if port_num not in self.SFP_VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.sfp_get_presence(port_num)
            content = []
            if result == PortStatus.SFP_ABSENCE:
                for i in range(256):
                    content.append(255)
            else:
                content = self.eeprom.dump_sfp_eeprom(port_num, page = page)

            content = bytes(content)
            return {"content":content}
        except Exception as e:
            ### Error handle
            # Check if we also can't access other i2c devices
            i2c = I2C(0)
            if i2c.check_status() == False:
                self.logger.error("SFP Port "+ str(port_num) + " might have transceiver issue, please check it")
                #Try to reset i2c mux
                cpld = CPLD()
                cpld.mux_reset_by_sfp_port(port_num)
            else:
                self.logger.error("Dump SFP port ever failed, but I2C bus is OK")
            raise

    def dump_qsfp_eeprom(self, port_num, page = None):
        try: 
            if port_num not in self.QSFP_VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.qsfp_get_presence(port_num)
            content = []
            if result == PortStatus.QSFP_ABSENCE:
                for i in range(256):
                    content.append(255)
            else:
                content = self.eeprom.dump_qsfp_eeprom(port_num, page = page)
            
            content = bytes(content)
            return {"content":content}
        except Exception as e:
            ### Error handle
            # Check if we also can't access other i2c devices
            i2c = I2C(0)
            if i2c.check_status() == False:
                self.logger.error("QSFP Port "+ str(port_num) + " might have transceiver issue, please check it")
                #Try to reset i2c mux
                cpld = CPLD()
                cpld.mux_reset_by_qsfp_port(port_num)
            else:
                self.logger.error("Dump QSFP port ever failed, but I2C bus is OK")
            raise
