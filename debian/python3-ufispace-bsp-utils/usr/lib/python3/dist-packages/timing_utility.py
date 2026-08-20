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
from timing.idt82p2281 import IDT82P2281
from timing.idt82p33831 import IDT82P33831
from timing.idt82p33831 import IDT82P33831Const as DPLLConst
from timing.neom8t import NEOM8T

class TimingUtility:

    def __init__(self):
        pass

    def set_1pps_priority(self, input, priority):
        idt = IDT82P33831()
        idt.set1PPSInputPriority(input, priority)

    def set_frequency_priority(self, input, priority):
        idt = IDT82P33831()
        idt.setFrequencyInputPriority(input, priority)

    def set_frequency_priority_dpll3(self, input, priority):
        idt = IDT82P33831()
        idt.setFrequencyInputPriorityDPLL3(input, priority)

    def get_1pps_priority(self, input):
        idt = IDT82P33831()
        priority = idt.get1PPSInputPriority(input)
        return {"priority": priority}

    def get_1pps_priorities(self):
        idt = IDT82P33831()

        inputs = [DPLLConst.GPS_1PPS, DPLLConst.PTP_1PPS,
                  DPLLConst.SMA_1PPS, DPLLConst.TOD_1PPS]
        response = []

        for input in inputs:
            priority = idt.get1PPSInputPriority(input)
            response.append({"input": input, "priority": priority})

        return response

    def get_frequency_priority(self, input):
        idt = IDT82P33831()
        priority = idt.getFrequencyInputPriority(input)
        return {"priority": priority}

    def get_frequency_priority_dpll3(self, input):
        idt = IDT82P33831()
        priority = idt.getFrequencyInputPriorityDPLL3(input)
        return {"priority": priority}

    def get_frequency_priorities(self):
        idt = IDT82P33831()
        inputs = [DPLLConst.GPS_10M, DPLLConst.SYNCE_PHY_100G_PIN1,
                  DPLLConst.SYNCE_PHY_100G_PIN2, DPLLConst.SYNCE_PHY_10G,
                  DPLLConst.SYNCE_QAX_10G, DPLLConst.PTP_10M,
                  DPLLConst.SMA_10M, DPLLConst.BITS]
        response = []

        for input in inputs:
            priority = idt.getFrequencyInputPriority(input)
            response.append({"input": input, "priority": priority})

        return response

    def get_frequency_priorities_dpll3(self):
        idt = IDT82P33831()
        inputs = [DPLLConst.GPS_10M_DPLL3, DPLLConst.SYNCE_PHY_100G_PIN1_DPLL3,
                  DPLLConst.SYNCE_PHY_100G_PIN2_DPLL3,
                  DPLLConst.SYNCE_PHY_10G_DPLL3, DPLLConst.SYNCE_QAX_10G_DPLL3,
                  DPLLConst.SMA_10M_DPLL3, DPLLConst.BITS_DPLL3]
        response = []

        for input in inputs:
            priority = idt.getFrequencyInputPriorityDPLL3(input)
            response.append({"input": input, "priority": priority})

        return response

    def set_revertive(self, revertive):
        idt = IDT82P33831()
        idt.setRevertiveMode(revertive)

    def get_revertive(self):
        idt = IDT82P33831()
        return idt.getRevertiveMode()

    def get_dpll_disqualified_inputs(self):
        idt = IDT82P33831()
        inputs = idt.getDisqualifiedInputs()

        # Clear the interrupt status
        idt.clearInterruptStatus()
        return inputs

    def clear_dpll_interrupts(self):
        idt = IDT82P33831()
        idt.clearInterruptStatus()

    def get_dpll_input_status(self, input):
        idt = IDT82P33831()
        status = idt.getInputStatus(input)
        return status

    def get_dpll_status(self, dpll):
        idt = IDT82P33831()
        pri_status = idt.getDPLLPriorityStatus(dpll)
        op_status = idt.getDPLLOperatingStatus(dpll)

        status = {}
        status["current"] = pri_status["current"]
        status["priority"] = pri_status["priority"]
        status["status"] = op_status

        return status

    def enable_dpll_interrupt_mask(self, input):
        idt = IDT82P33831()
        inputs = idt.enableInterruptMask(input)
        
    def disable_dpll_interrupt_mask(self, input):
        idt = IDT82P33831()
        inputs = idt.disableInterruptMask(input)
        
    def get_dpll_interrupt_mask(self):
        idt = IDT82P33831()
        return idt.getInterruptMask()
        
    # Under developing...
    def get_gps_cable_delay(self):
        neo = NEOM8T()
        delay = neo.getAntennaCableDelay()
        return {"cable_delay": delay}

    def set_gps_cable_delay(self, delay):
        neo = NEOM8T()
        neo.setAntennaCableDelay(delay)

    def get_bits_status(self):
        idt = IDT82P2281()
        status = {}

        los = idt.get_los_status()
        status["LOS"] = los

        return status

    def set_gps_tod_timing_format(self):
        neo = NEOM8T()
        neo.setGPSToDTimingFormat()

    def set_synce_select_option(self, mode):
        idt = IDT82P33831()
        idt.setSyncESelectOption(mode)

    def set_bits_t1e1_selection(self, mode):
        idt = IDT82P2281()
        idt.setBitsT1E1Selection(mode)

    def set_dpll_fast_lock(self, dpll):
        idt = IDT82P33831()
        idt.setDPLLFastLock(dpll)

    def get_input_clock_phase_offset(self, source):
        idt = IDT82P33831()
        rv = idt.getInputClockPhaseOffset(source)
        return rv

    def set_input_clock_phase_offset(self, source, offset):
        idt = IDT82P33831()
        idt.setInputClockPhaseOffset(source, offset)

    def set_dpll1_output_offset(self, offset):
        base = 10               # convenience to do the division
        ph1_max = 24            # define in div1_cfg
        ph2_max = 24999999      # define in div2_cfg
        ph1_cfg = 1.6
        ph2_cfg = 40
        fine_ph_cfg = 0.2
        DPLL = 1

        idt = IDT82P33831()
        idt.calculateDPLLOutputOffset(DPLL, offset, base, ph1_max, ph2_max,
                                       ph1_cfg, ph2_cfg, fine_ph_cfg)

    def set_dpll2_output_offset(self, offset):
        base = 10000            # convenience to do the division 
        ph1_max = 19            # define in div1_cfg
        ph2_max = 2             # define in div2_cfg
        ph1_cfg = 1.6667
        ph2_cfg = 33.3333
        fine_ph_cfg = 0.2083
        DPLL = 2

        idt = IDT82P33831()
        idt.calculateDPLLOutputOffset(DPLL, offset, base, ph1_max, ph2_max,
                                       ph1_cfg, ph2_cfg, fine_ph_cfg)

    def set_dpll_op_mode(self, dpll, mode):
        idt = IDT82P33831()
        idt.setDPLLOpMode(dpll, mode)

    def set_dpll_hitless_mode(self, dpll, mode):
        idt = IDT82P33831()
        idt.setDPLLHitlessMode(dpll, mode)