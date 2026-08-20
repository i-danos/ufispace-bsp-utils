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
from gpio.ioexp import IOExpander

class ResetUtility:

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.cpld = CPLD()
        self.ioexp = IOExpander()
        
    def set_bmc_reset_mask(self, target = None):
        hw_rev = self.cpld.get_hw_rev()
        build_rev = self.cpld.get_build_rev()
        
        if target == None:
            target = 'all'
            
        if hw_rev == self.cpld.HARDWARE_REV_ALPHA_STR:
            self.cpld.bmc_reset_set(target)
        elif hw_rev == self.cpld.HARDWARE_REV_BETA_STR:
            if build_rev == self.cpld.BUILD_REV_A1_STR:
                self.cpld.bmc_reset_set(target)
            elif build_rev == self.cpld.BUILD_REV_A2_STR:
                self.cpld.bmc_reset_set(target)
            else:
                self.ioexp.bmc_reset_set(target)
        else:
            self.ioexp.bmc_reset_set(target)

    def unset_bmc_reset_mask(self, target = None):
        hw_rev = self.cpld.get_hw_rev()
        build_rev = self.cpld.get_build_rev()
        
        if target == None:
            target = 'all'
        
        if hw_rev == self.cpld.HARDWARE_REV_ALPHA_STR:
            self.cpld.bmc_reset_unset(target)
        elif hw_rev == self.cpld.HARDWARE_REV_BETA_STR:
            if build_rev == self.cpld.BUILD_REV_A1_STR:
                self.cpld.bmc_reset_unset(target)
            elif build_rev == self.cpld.BUILD_REV_A2_STR:
                self.cpld.bmc_reset_unset(target)
            else:
                self.ioexp.bmc_reset_unset(target)
        else:
            self.ioexp.bmc_reset_unset(target)

    def set_mux_reset_mask(self, target):
        self.cpld.mux_reset_set(target)

    def unset_mux_reset_mask(self, target):
        self.cpld.mux_reset_unset(target)

