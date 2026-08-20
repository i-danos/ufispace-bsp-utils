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
import subprocess

from common.logger import Logger
from protocol.lpc import LPC
from protocol.lpc import LPCDevType
from i2c_mux.i2c_mux import I2CMux
from gpio.ioexp import IOExpander
from cpld.cpld import CPLD
from eeprom.eeprom import EEPRom
from timing.idt82p2281 import IDT82P2281
from timing.idt82p33831 import IDT82P33831
from timing.neom8t import NEOM8T

class PlatformUtility:

    def __init__(self):
        try:
            log = Logger(__name__)
            self.logger = log.getLogger()
            self.lpc = LPC()
            self.i2c_mux = I2CMux()
            self.ioexp = IOExpander()
            self.cpld = CPLD()
            self.eeprom = EEPRom()
            self.idt82p2281 = IDT82P2281()
            self.idt82p33831 = IDT82P33831()
            self.neom8t = NEOM8T()
        except Exception as e:
            raise

    def rov_init(self):
        try:
            rov = self.ioexp.rov_get_voltage()
            if rov == "N/A":
                self.logger.error("ROV value is not valid")
                raise ValueError("ROV value is not valid")
            else:
                self.ioexp.rov_set_voltage(rov)
        except Exception as e:
            raise

    def device_init(self):
        try:
            # Unmount kernel modules
            mod = subprocess.getoutput("lsmod | grep gpio_ich")
            if mod != "":
                subprocess.run(['rmmod', 'gpio_ich'])

            # CPLD
            self.cpld.init()

            # Mount kernel modules
            # I2C I801
            subprocess.run(['modprobe', 'i2c_i801'])

            # I2C Dev
            subprocess.run(['modprobe', 'i2c_dev'])

            # I2C Mux
            subprocess.run(['modprobe', 'i2c_mux_pca954x'])
            self.i2c_mux.init()

            # EEPROM
            self.eeprom.init()

            # GPIO
            self.ioexp.init()

            # Timing Modules

            # Workaround for RS422 Transceiver
            # Currently, default configuration is 0x05. (TX high. RX low. Formed loopback.)
            # TODO: If CPLD default configuration has been changed to receiver, remove it.
            self.cpld.ptp_control_configure_receive()

            self.idt82p2281.init()
            self.idt82p33831.init()
            self.neom8t.init()

            # Disable interrupt of "SyncE_PTP_Mask" and "Fan_Mask"
            self.cpld.interrupt_mask_enable("SyncE_PTP_Mask")
        
            # Disable 0xF011 bit 2 for disabling smbus intr
            self.cpld.smbus_intr_disable()
            
            # Disable 0xF000 bit 5 for clearing smbus alert
            self.cpld.host_status_smbus_alert_clear()            
                        
        except Exception as e:
            raise

    def device_deinit(self):
        try:
            # Remove kernel modules
            # Timing Modules
            self.neom8t.deinit()
            self.idt82p33831.deinit()
            self.idt82p2281.deinit()

            # CPLD
            self.cpld.deinit()

            # GPIO
            self.ioexp.deinit()
                
            # Enable interrupt of "Global_Mask"
            self.cpld.interrupt_mask_enable("Global_Mask")
        except Exception as e:
            raise

def main():
    util = PlatformUtility()

    if len(sys.argv) != 2:
        print("\nUsage: sudo " + sys.argv[0] + " init|deinit")
        return

    if sys.argv[1] == 'init':
        util.device_init()
        util.rov_init()
    elif sys.argv[1] == 'deinit':
        util.device_deinit()
    else:
        print("Invalid arguments:")

        # print command line arguments
        for arg in sys.argv[1:]:
            print(arg)
        print("\nUsage: sudo " + sys.argv[0] + " init|deinit")

if __name__ == "__main__":
    main()
