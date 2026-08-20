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
from const.const import Led
from const.const import CPLDConst
from cpld.cpld import CPLD

class CPLDUtility:

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.cpld = CPLD()

    def get_board_id(self):
        try:
            result = self.cpld.get_board_id()

            return {"id":result}
        except Exception as e:
            raise

    def get_board_info(self):
        try:
            board_id = self.cpld.get_board_id()
            hw_rev = self.cpld.get_hw_rev()
            build_rev = self.cpld.get_build_rev()

            return {"id":board_id, "hw_rev":hw_rev, "build_rev":build_rev}
        except Exception as e:
            raise

    def get_cpld_version(self, target):
        try:
            if target == CPLDConst.LOC_CPU:
                result = self.cpld.get_cpu_board_cpld_revision()
            else:
                result = self.cpld.get_main_board_code_version()

            return {"version":"X.%02x" % result}
        except Exception as e:
            raise

    def set_uart_source(self, source):
        try:
            self.cpld.set_uart_source(source)
        except Exception as e:
            raise

    def get_uart_source(self):
        try:
            result = self.cpld.get_uart_source()
            if result == CPLDConst.UART_SOURCE_CPU:
                ret_val = {"source":"CPU"}
            else:
                ret_val = {"source":"BMC"}

            return ret_val
        except Exception as e:
            raise

    def set_led_control(self, target, status, color, blinking):
        try:
            self.cpld.set_led(target, status, color, blinking)
        except Exception as e:
            raise

    def get_led_status(self, target):
        try:
            result = self.cpld.get_led_status(target)

            ret_val = {}
            if result["status"] == Led.STATUS_OFF:
                ret_val.update({"status":"off"})
            else:
                ret_val.update({"status":"on"})

            if result["color"] == Led.COLOR_YELLOW:
                ret_val.update({"color":"yellow"})
            else:
                ret_val.update({"color":"green"})

            if result["blink_status"] == Led.BLINK_STATUS_SOLID:
                ret_val.update({"blink_status":"solid"})
            else:
                ret_val.update({"blink_status":"blinking"})

            return ret_val
        except Exception as e:
            raise

    def get_bmc_power_status(self):
        try:
            result = self.cpld.bmc_power_get()
            if result == 1:
                ret_val = {"status":"ok"}
            else:
                ret_val = {"status":"abnormal"}

            return ret_val
        except Exception as e:
            raise
            
    def enable_power_ctrl_mask(self, target):
        self.cpld.power_ctrl_set(target)
        
    def disable_power_ctrl_mask(self, target):
        self.cpld.power_ctrl_unset(target)

    def set_tod_output(self, status):
        self.cpld.tod_output_set(status)
