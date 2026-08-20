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
from const.const import PortStatus
from const.const import LPMode
from gpio.ioexp import IOExpander

class QSFPUtility:

    VALID_PORTS = (0, 1)

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.ioexp = IOExpander()

    def get_presence(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.qsfp_get_presence(port_num)

            if result == PortStatus.QSFP_ABSENCE:
                ret_val = {"presence":"absence"}
            else:
                ret_val = {"presence":"presence"}

            return ret_val
        except Exception as e:
            raise

    def set_lp_mode(self, port_num, enable):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            self.ioexp.qsfp_set_lp_mode(port_num, enable)
        except Exception as e:
            raise

    def get_lp_mode(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            result = self.ioexp.qsfp_get_lp_mode(port_num)

            if result == LPMode.DISABLE:
                ret_val = {"lp_mode":"disabled"}
            else:
                ret_val = {"lp_mode":"enabled"}

            return ret_val
        except Exception as e:
            raise

    def reset_port(self, port_num):
        try:
            if port_num not in self.VALID_PORTS:
                raise ValueError("Port number(" + str(port_num) + ") is out of range")

            self.ioexp.qsfp_reset_port(port_num)
        except Exception as e:
            raise
