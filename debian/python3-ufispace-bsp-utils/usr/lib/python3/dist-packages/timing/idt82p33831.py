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
from time import sleep

from common.logger import Logger
from timing.idt82p33831_reg import IDT82P33831RegisterConst as DPLLConst
from timing.idt82p33831_reg import IDT82P33831Operation
from cpld.cpld import CPLD

class IDT82P33831:

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.dpll_op = IDT82P33831Operation()
        self.cpld = CPLD()

        self.input_map = {}
        self.input_map[IDT82P33831Const.GPS_1PPS] = \
            ReferenceInput(DPLLConst.DPLL1, DPLLConst.INPUT13, IDT82P33831Const.TYPE_1PPS)
        self.input_map[IDT82P33831Const.PTP_1PPS] = \
            ReferenceInput(DPLLConst.DPLL1, DPLLConst.INPUT10, IDT82P33831Const.TYPE_1PPS)
        self.input_map[IDT82P33831Const.SMA_1PPS] = \
            ReferenceInput(DPLLConst.DPLL1, DPLLConst.INPUT7, IDT82P33831Const.TYPE_1PPS)
        self.input_map[IDT82P33831Const.TOD_1PPS] = \
            ReferenceInput(DPLLConst.DPLL1, DPLLConst.INPUT8, IDT82P33831Const.TYPE_1PPS)
        self.input_map[IDT82P33831Const.GPS_10M] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT14, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_PHY_100G_PIN1] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT4, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_PHY_100G_PIN2] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT5, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_PHY_10G] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT6, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_QAX_10G] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT3, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.PTP_10M] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT12, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SMA_10M] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT9, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.BITS] = \
            ReferenceInput(DPLLConst.DPLL2, DPLLConst.INPUT11, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.GPS_10M_DPLL3] = \
            ReferenceInput(DPLLConst.DPLL3, DPLLConst.INPUT14, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_PHY_100G_PIN1_DPLL3] = \
            ReferenceInput(DPLLConst.DPLL3, DPLLConst.INPUT4, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_PHY_100G_PIN2_DPLL3] = \
            ReferenceInput(DPLLConst.DPLL3, DPLLConst.INPUT5, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_PHY_10G_DPLL3] = \
            ReferenceInput(DPLLConst.DPLL3, DPLLConst.INPUT6, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SYNCE_QAX_10G_DPLL3] = \
            ReferenceInput(DPLLConst.DPLL3, DPLLConst.INPUT3, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.SMA_10M_DPLL3] = \
            ReferenceInput(DPLLConst.DPLL3, DPLLConst.INPUT9, IDT82P33831Const.TYPE_FREQ)
        self.input_map[IDT82P33831Const.BITS_DPLL3] = \
            ReferenceInput(DPLLConst.DPLL3, DPLLConst.INPUT11, IDT82P33831Const.TYPE_FREQ)

    def __del__(self):
        pass

    def init(self):
        
        # Hardware reset, the behavior depends on CPLD implementation
        # RESET down. wait 50us. RESET up. wait 2ms. More time for safety
        self.cpld.smu_hardware_reset(0)
        sleep(0.001)
        self.cpld.smu_hardware_reset(1)
        sleep(0.1)
        
        # Initialize APLL configuration
        self.dpll_op.init_apll()

        # Set DPLL compensation
        self.dpll_op.setDPLLCompensation()
        
        # Enable Hitless switch
        self.dpll_op.setDpllHitlessCfg(DPLLConst.DPLL1, 2)
        self.dpll_op.setDpllHitlessCfg(DPLLConst.DPLL2, 2)

        # Disable GNSS from DPLL3 (G.8275.2/GM use OCXO)
        self.dpll_op.disableDPLLInput(DPLLConst.DPLL3, DPLLConst.INPUT14)

        # Initial DPLL default interrupt configuration mask
        self.dpll_op.initializeInterruptMask()

        # Clear interrupt (Write 1 to clear)
        self.clearInterruptStatus()

    def deinit(self):
        pass

    def getDisqualifiedInputs(self):
        interrupts = self.dpll_op.getInterrupts()
        dis_inputs = []
        dis_inputs_index = []

        # Get which input clock index is disqualified
        for x in interrupts["inputs"]:
            if self.dpll_op.getInputStatusDisqualify(x) == 1:
                dis_inputs_index.append(x)

        # There is no any disqualified input clock
        if len(dis_inputs_index) == 0:
            return dis_inputs

        # Transfer input clock index to input clock name
        for key, input in self.input_map.items():
            if input.getInput() in dis_inputs_index:
                dis_inputs.append(key)

        return dis_inputs

    def getInputInterrupts(self):
        inputs = []
        interrupts = self.dpll_op.getInterrupts()
        for key, input in self.input_map.items():
            if input.getInput() in interrupts["inputs"]:
                inputs.append(key)
        return inputs

    def clearInterruptStatus(self):
        self.dpll_op.clearInterruptStatus()

    def _get_input(self, source, type):
        if source not in self.input_map:
            raise ValueError("Input not existed: " + source)

        input = self.input_map[source]
        if type is not None and input.getType() != type:
            raise ValueError("Input not " + type + ": " + source)

        return input

    def getDPLLPriorityStatus(self, dpll_type):
        if dpll_type == 1:
            dpll = DPLLConst.DPLL1
        elif dpll_type == 2:
            dpll = DPLLConst.DPLL2
        elif dpll_type == 3:
            dpll = DPLLConst.DPLL3
        else:
            raise ValueError("Unknown DPLL:" + dpll_type)

        data = self.dpll_op.getDPLLPriorityTable(dpll)

        info = {}
        current = "None"
        for key, input in self.input_map.items():
            if input.getDPLL() == dpll:
                if data["current"] == input.getInput():
                    current = key
        info["current"] = current

        priority = []
        for i in range(0,3):
            current = "None"
            for key, input in self.input_map.items():
                if input.getDPLL() == dpll:
                    if data["priority"][i] == input.getInput():
                        current = key
            priority.append(current)
        info["priority"] = priority

        return info

    def getDPLLOperatingStatus(self, dpll_type):
        if dpll_type == 1:
            dpll = DPLLConst.DPLL1
        elif dpll_type == 2:
            dpll = DPLLConst.DPLL2
        elif dpll_type == 3:
            dpll = DPLLConst.DPLL3
        else:
            raise ValueError("Unknown DPLL:" + dpll_type)

        data = self.dpll_op.getDPLLOperatingStatus(dpll)

        return data

    def getInputStatus(self, source):
        input = self._get_input(source, None)
        return self.dpll_op.getInputStatus(input.getInput())

    def get1PPSInputPriority(self, source):
        input = self._get_input(source, IDT82P33831Const.TYPE_1PPS)
        return self.dpll_op.getDPLLInputPriority(input.getDPLL(), input.getInput())

    def set1PPSInputPriority(self, source, priority):
        input = self._get_input(source, IDT82P33831Const.TYPE_1PPS)
        self.dpll_op.setDPLLInputPriority(input.getDPLL(), input.getInput(), priority)

    def getFrequencyInputPriority(self, source):
        input = self._get_input(source, IDT82P33831Const.TYPE_FREQ)
        if input.getDPLL() != DPLLConst.DPLL2:
            raise ValueError("The Input not existed in DPLL2: " + source)
        return self.dpll_op.getDPLLInputPriority(input.getDPLL(), input.getInput())

    def getFrequencyInputPriorityDPLL3(self, source):
        input = self._get_input(source, IDT82P33831Const.TYPE_FREQ)
        if input.getDPLL() != DPLLConst.DPLL3:
            raise ValueError("The Input not existed in DPLL3: " + source)
        return self.dpll_op.getDPLLInputPriority(input.getDPLL(), input.getInput())

    def setFrequencyInputPriority(self, source, priority):
        input = self._get_input(source, IDT82P33831Const.TYPE_FREQ)
        if input.getDPLL() != DPLLConst.DPLL2:
            raise ValueError("The Input not existed in DPLL2: " + source)
        self.dpll_op.setDPLLInputPriority(input.getDPLL(), input.getInput(), priority)

    def setFrequencyInputPriorityDPLL3(self, source, priority):
        input = self._get_input(source, IDT82P33831Const.TYPE_FREQ)
        if input.getDPLL() != DPLLConst.DPLL3:
            raise ValueError("The Input not existed in DPLL3: " + source)
        self.dpll_op.setDPLLInputPriority(input.getDPLL(), input.getInput(), priority)

    def getRevertiveMode(self):
        dpll1 = self.dpll_op.getDPLLRevertiveMode(DPLLConst.DPLL1)
        dpll2 = self.dpll_op.getDPLLRevertiveMode(DPLLConst.DPLL2)
        dpll3 = self.dpll_op.getDPLLRevertiveMode(DPLLConst.DPLL3)
        return "{DPLL1 revertive:%d, DPLL2 revertive:%d, DPLL3 revertive:%d" \
                %(dpll1, dpll2, dpll3)

    def setRevertiveMode(self, revertive):
        # Global configuration. Both DPLL should be configured.
        # TODO: Rollback configuration when one of them failed.
        self.dpll_op.setDPLLRevertiveMode(DPLLConst.DPLL1, revertive)
        self.dpll_op.setDPLLRevertiveMode(DPLLConst.DPLL2, revertive)
        self.dpll_op.setDPLLRevertiveMode(DPLLConst.DPLL3, revertive)

    def enableInterruptMask(self, source):
        if source not in self.input_map:
            raise ValueError("Input not existed: " + source)
   
        input = self.input_map[source]
        self.dpll_op.enbleDPLLInterrupt(input.getInput())
        
    def disableInterruptMask(self, source):
        if source not in self.input_map:
            raise ValueError("Input not existed: " + source)
      
        input = self.input_map[source]
        self.dpll_op.disableDPLLInterrupt(input.getInput())   
            
    def getInterruptMask(self):
        info = {}
        for key, value in self.input_map.items():
            info[key] = self.dpll_op.getDPLLInterrupt(value.getInput())
   
        return info

    def setSyncESelectOption(self, mode):
        self.dpll_op.setSyncEOptionMode(mode)

    def setDPLLFastLock(self, dpll):
        self.dpll_op.setDPLLFastLockMode(dpll)

    def getInputClockPhaseOffset(self, source):
        input = self._get_input(source, None)
        ns = self.dpll_op.getInputClockPhaseOffsetCfg(input.getInput())

        rv = []
        rv.append("Input: " + source)
        rv.append("Offset(ns): " +  str(ns))
        return rv

    def setInputClockPhaseOffset(self, source, offset):
        OFFSET_MIN = -128
        OFFSET_MAX = 127

        if offset > OFFSET_MAX or offset < OFFSET_MIN:
            raise ValueError("The offset is out of range (" + \
                              str(OFFSET_MIN) + " to " + str(OFFSET_MAX) +")")

        input = self._get_input(source, None)
        self.dpll_op.setInputClockPhaseOffsetCfg(input.getInput(), offset)

    def calculateDPLLOutputOffset(self, DPLL, offset, base_num, ph1_max, 
                                   ph2_max, ph1_cfg, ph2_cfg, fine_ph_cfg):
        base = base_num
        offset_base = offset * base
        ph1_cfg_base = ph1_cfg * base
        ph2_cfg_base = ph2_cfg * base
        fine_ph_cfg_base = fine_ph_cfg * base
        OFFSET_MIN = 0
        OFFSET_MAX = int(ph2_max * ph2_cfg + ph1_max * ph1_cfg + 1)

        if offset < OFFSET_MIN or offset > OFFSET_MAX:
            raise ValueError("The offset is out of range (" + \
                              str(OFFSET_MIN) + " to " + str(OFFSET_MAX) +")")

        # formular = ph1_cfg * N + ph2_cfg * N - fine_ph_cfg * N
        # need to calculate the N for ph1_cfg, ph2_cfg and fine_ph_cfg
        # N = (ph1_reg, ph2_reg, fine_ph_reg)
        # all of the xxx_base is convenience to do the division

        ph2_reg = offset_base // ph2_cfg_base
        remainder_num = offset_base % ph2_cfg_base

        if remainder_num % ph1_cfg_base == 0:
            ph1_reg = remainder_num // ph1_cfg_base
            fine_ph_reg = 0
        else:
            ph1_reg = remainder_num // ph1_cfg_base + 1
            fine_ph_reg = (ph1_reg * ph1_cfg_base - remainder_num) // fine_ph_cfg_base

            if ph1_reg > ph1_max:
                ph1_reg = ph1_max
                fine_ph_reg = 0

        self.dpll_op.setDPLLOutputOffsetCfg(DPLL, int(ph1_reg), 
                                            int(ph2_reg), int(fine_ph_reg))

    def setDPLLOpMode(self, dpll, mode):
        self.dpll_op.setDPLLOpModeReg(dpll, mode)
        
    def setDPLLHitlessMode(self, dpll, mode):
        self.dpll_op.setDpllHitlessCfg(dpll, mode)

class IDT82P33831Const:

    # Reference source for 1 PPS
    GPS_1PPS = "GPS-1PPS"
    PTP_1PPS = "PTP-1PPS"
    SMA_1PPS = "SMA-1PPS"
    TOD_1PPS = "ToD-1PPS"

    # Reference source for frequency
    GPS_10M = "GPS-10MHz"
    SYNCE_PHY_100G_PIN1 = "SyncE-BCM82398-100G-PIN1"
    SYNCE_PHY_100G_PIN2 = "SyncE-BCM82398-100G-PIN2"
    SYNCE_PHY_10G = "SyncE-BCM82780-10G"
    SYNCE_QAX_10G = "SyncE-BCM88470-10G"
    PTP_10M = "PTP-10MHz"
    SMA_10M = "SMA-10MHz"
    BITS = "BITS"

    # Reference source for frequency (DPLL3)
    GPS_10M_DPLL3 = "GPS-10MHz-DPLL3"
    SYNCE_PHY_100G_PIN1_DPLL3 = "SyncE-BCM82398-100G-PIN1-DPLL3"
    SYNCE_PHY_100G_PIN2_DPLL3 = "SyncE-BCM82398-100G-PIN2-DPLL3"
    SYNCE_PHY_10G_DPLL3 = "SyncE-BCM82780-10G-DPLL3"
    SYNCE_QAX_10G_DPLL3 = "SyncE-BCM88470-10G-DPLL3"
    SMA_10M_DPLL3 = "SMA-10MHz-DPLL3"
    BITS_DPLL3 = "BITS-DPLL3"

    TYPE_1PPS = "1PPS"
    TYPE_FREQ = "Frequency"

class ReferenceInput:

    def __init__(self, dpll, input, type):
        self.dpll = dpll
        self.input = input
        self.type = type

    def getDPLL(self):
        return self.dpll

    def getInput(self):
        return self.input

    def getType(self):
        return self.type
