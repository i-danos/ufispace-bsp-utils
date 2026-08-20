#!/usr/bin/env python3
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
from const.const import SFP
from const.const import PortRate
from const.const import PortStatus
from gpio.ioexp import IOExpander

class SFPUtility:

    VALID_PORTS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27)

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.ioexp = IOExpander()

    def get_presence(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.sfp_get_presence(port_num)

            if result == PortStatus.SFP_ABSENCE:
                ret_val = {"presence":"absence"}
            else:
                ret_val = {"presence":"presence"}

            return ret_val
        except Exception as e:
            raise

    def get_rx_lost(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.sfp_get_rx_lost(port_num)

            if result == SFP.DETECTED:
                ret_val = {"rx_lost":"detected"}
            else:
                ret_val = {"rx_lost":"undetected"}

            return ret_val
        except Exception as e:
            raise

    def get_tx_fault(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.sfp_get_tx_flt(port_num)

            if result == SFP.DETECTED:
                ret_val = {"tx_flt":"detected"}
            else:
                ret_val = {"tx_flt":"undetected"}

            return ret_val
        except Exception as e:
            raise

    def set_port_rate(self, port_num, rate):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            self.ioexp.sfp_set_port_rate(port_num, rate)
        except Exception as e:
            raise

    def get_port_rate(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.sfp_get_port_rate(port_num)

            if result == PortRate.Rate_1G:
                ret_val = {"rate":"1G"}
            else:
                ret_val = {"rate":"10G"}

            return ret_val
        except Exception as e:
            raise

    def set_port_status(self, port_num, status):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            self.ioexp.sfp_set_port_status(port_num, status)
        except Exception as e:
            raise

    def get_port_status(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.sfp_get_port_status(port_num)

            if result == PortStatus.ENABLED:
                ret_val = {"status":"enabled"}
            else:
                ret_val = {"status":"disabled"}

            return ret_val
        except Exception as e:
            raise
