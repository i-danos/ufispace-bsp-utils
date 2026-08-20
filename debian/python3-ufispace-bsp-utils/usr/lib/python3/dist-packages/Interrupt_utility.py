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
from cpld.cpld import CPLD

class InterruptUtility:

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.cpld = CPLD()

    def get_nmi_interrupt(self):
        try:
            int_list = self.cpld.get_nmi_interrupt()

            return int_list
        except Exception as e:
            raise

    def get_ethernet_MAC_PHY_status_interrupt(self):
        try:
            int_list = self.cpld.get_ethernet_mac_phy_status_interrupt()

            return int_list
        except Exception as e:
            raise

    def get_synce_ptp_status_interrupt(self):
        try:
            int_list = self.cpld.get_synce_ptp_status_interrupt()

            return int_list
        except Exception as e:
            raise

    def get_port_status_interrupt(self):
        try:
            int_list = self.cpld.get_port_status_interrupt()

            return int_list
        except Exception as e:
            raise

    def get_cpld_alarm_interrupt(self):
        try:
            int_list = self.cpld.get_cpld_alarm_interrupt()

            return int_list
        except Exception as e:
            raise

    def clear_host_status_smbus_alert(self):
        self.cpld.host_status_smbus_alert_clear()
    
    def enable_interrupt_mask(self, input):
        self.cpld.interrupt_mask_enable(input)

    def disable_interrupt_mask(self, input):
        self.cpld.interrupt_mask_disable(input)
        
    def get_interrupt_mask(self):        
        return self.cpld.interrupt_mask_get()
        
    def enable_smbus_interrupt(self):
        self.cpld.smbus_intr_enable()

    def disable_smbus_interrupt(self):
        self.cpld.smbus_intr_disable()

