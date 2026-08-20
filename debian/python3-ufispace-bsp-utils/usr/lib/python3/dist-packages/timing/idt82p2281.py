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
from time import sleep

from common.logger import Logger
from cpld.cpld import CPLD
from timing.cp2130 import CP2130

class IDT82P2281:

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.cp2130 = CP2130()
        self.cpld = CPLD()

    def __del__(self):
        pass

    def init(self):
        # TODO: Some re-org to de-couple this initialization
        self.cp2130.init()

        # Hardware reset, the behavior depends on CPLD implementation
        # RESET down. wait 100ns. RESET up. wait 2ms. More time for safety
        self.cpld.bits_hardware_reset(0)
        sleep(0.001)
        self.cpld.bits_hardware_reset(1)
        sleep(0.005)

        # By default, run T1 mode
        # The registers are accessible after 2ms. Sleep 5ms for safety.
        self.set_t1_enable()

    def deinit(self):
        pass

    def get_los_interrupt_enable(self):
        data = self.cp2130.get_interrupt_enable()
        los_ie = data&0b00000001

        return los_ie

    def set_los_interrupt_enable(self, enable):
        ie = self.cp2130.get_interrupt_enable()
        config = (ie&0b11111110)|enable

        self.cp2130.set_interrupt_enable(config)
        # Clear LOS interrupt status
        self.cp2130.clear_interrupt_status(0b00000001)

    def get_los_status(self):
        status = self.cp2130.get_line_status()
        los = status&0b00000001

        return los

    def set_e1_enable(self):
        # select E1 mode
        self.cp2130.set_operating_mode(OperatingMode.E1)
        sleep(0.005)

        # software reset
        self.cp2130.software_reset()
        sleep(0.005)

        # transmit cfg
        self.cp2130.set_cfg_transmit(0x00)
        sleep(0.005)

        # transmit and receive termination Cfg
        self.cp2130.set_term_cfg_tx_rx(0x00)
        sleep(0.005)

        # interrupt enable control
        self.cp2130.set_interrupt_enable(0x01)
        sleep(0.005)

        # interrupt trigger edges select
        self.cp2130.set_intr_tri_edge_sel(0x01)
        sleep(0.005)

        # interrupt status
        self.cp2130.clear_interrupt_status(0x00)
        sleep(0.005)

        # In case of LOS, this configuration determines the output on the REFA_OUT pins.
        # To prevent internal clock, output high level when LOS.
        self.cp2130.set_output_control_no_mclk()
        sleep(0.005)

    def set_t1_enable(self):
        # select T1 mode
        self.cp2130.set_operating_mode(OperatingMode.T1_SF)
        sleep(0.005)

        # software reset
        self.cp2130.software_reset()
        sleep(0.005)

        # transmit cfg
        self.cp2130.set_cfg_transmit(0x02)
        sleep(0.005)

        # transmit and receive termination Cfg
        self.cp2130.set_term_cfg_tx_rx(0x12)
        sleep(0.005)

        # interrupt enable control
        self.cp2130.set_interrupt_enable(0x01)
        sleep(0.005)

        # interrupt trigger edges select
        self.cp2130.set_intr_tri_edge_sel(0x01)
        sleep(0.005)

        # interrupt status
        self.cp2130.clear_interrupt_status(0x01)
        sleep(0.005)

        # In case of LOS, this configuration determines the output on the REFA_OUT pins.
        # To prevent internal clock, output high level when LOS.
        self.cp2130.set_output_control_no_mclk()
        sleep(0.005)

    def setBitsT1E1Selection(self, mode):
        if mode == 1:
            self.set_t1_enable()
        elif mode == 2:
            self.set_e1_enable()
        else:
            raise ValueError("The select mode index is out of range (1-2)")

class OperatingMode:
    T1_SF = 0x01
    T1_ESF = 0x03
    T1_DM = 0x05
    T1_SLC_96 = 0x07
    J1_SF = 0x09
    J1_ESF = 0x0B
    E1 = 0x00
