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
import abc
import time

from smbus import SMBus
from common.logger import Logger
from cpld.cpld import CPLD
from i2c_mux.i2c_mux import I2CMux

'''
This class should be re-factor when it's too complicated to maintain.
'''

OperatingStatus = ["Not used", "Free Run", "Holdover", "Not used",
                   "Locked", "Pre-locked2", "Pre-locked", "Phase lost"]

class IDT82P33831Operation:

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.bus = 0
        self.reg_map = self._create_reg_map()

    def _create_reg_map(self):

        reg_map = {}
        # Interrupt status (0x07, 0x08, 0x09, 0x0A)
        reg_map[0x07] = DPLLMultiRegister(self.bus, 0, 0x07, 4)
        # Interrupt mask configuration (0x0B, 0x0C, 0x0D, 0x0E)
        reg_map[0x0b] = DPLLMultiRegister(self.bus, 0, 0x0b, 4)
        # Input status
        reg_map[0xa5] = DPLLSingleRegister(self.bus, 1, 0x25)
        reg_map[0xa6] = DPLLSingleRegister(self.bus, 1, 0x26)
        reg_map[0xa7] = DPLLSingleRegister(self.bus, 1, 0x27)
        reg_map[0xa8] = DPLLSingleRegister(self.bus, 1, 0x28)
        reg_map[0xa9] = DPLLSingleRegister(self.bus, 1, 0x29)
        reg_map[0xaa] = DPLLSingleRegister(self.bus, 1, 0x2a)
        reg_map[0xab] = DPLLSingleRegister(self.bus, 1, 0x2b)
        reg_map[0xac] = DPLLSingleRegister(self.bus, 1, 0x2c)
        reg_map[0xad] = DPLLSingleRegister(self.bus, 1, 0x2d)
        reg_map[0xae] = DPLLSingleRegister(self.bus, 1, 0x2e)
        reg_map[0xaf] = DPLLSingleRegister(self.bus, 1, 0x2f)
        reg_map[0xb0] = DPLLSingleRegister(self.bus, 1, 0x30)
        reg_map[0xb1] = DPLLSingleRegister(self.bus, 1, 0x31)
        reg_map[0xb2] = DPLLSingleRegister(self.bus, 1, 0x32)
        # Input LOS sync configuration
        reg_map[0xb5] = DPLLSingleRegister(self.bus, 1, 0x35)
        reg_map[0xb6] = DPLLSingleRegister(self.bus, 1, 0x36)
        reg_map[0xb7] = DPLLSingleRegister(self.bus, 1, 0x37)
        reg_map[0xb8] = DPLLSingleRegister(self.bus, 1, 0x38)
        reg_map[0xb9] = DPLLSingleRegister(self.bus, 1, 0x39)
        reg_map[0xba] = DPLLSingleRegister(self.bus, 1, 0x3a)
        reg_map[0xbb] = DPLLSingleRegister(self.bus, 1, 0x3b)
        reg_map[0xbc] = DPLLSingleRegister(self.bus, 1, 0x3c)
        reg_map[0xbd] = DPLLSingleRegister(self.bus, 1, 0x3d)
        reg_map[0xbe] = DPLLSingleRegister(self.bus, 1, 0x3e)
        reg_map[0xbf] = DPLLSingleRegister(self.bus, 1, 0x3f)
        reg_map[0xc0] = DPLLSingleRegister(self.bus, 1, 0x40)
        reg_map[0xc1] = DPLLSingleRegister(self.bus, 1, 0x41)
        reg_map[0xc2] = DPLLSingleRegister(self.bus, 1, 0x42)
        # Phase offset configuration
        reg_map[0xc5] = DPLLSingleRegister(self.bus, 1, 0x45)
        reg_map[0xc6] = DPLLSingleRegister(self.bus, 1, 0x46)
        reg_map[0xc7] = DPLLSingleRegister(self.bus, 1, 0x47)
        reg_map[0xc8] = DPLLSingleRegister(self.bus, 1, 0x48)
        reg_map[0xc9] = DPLLSingleRegister(self.bus, 1, 0x49)
        reg_map[0xca] = DPLLSingleRegister(self.bus, 1, 0x4a)
        reg_map[0xcb] = DPLLSingleRegister(self.bus, 1, 0x4b)
        reg_map[0xcc] = DPLLSingleRegister(self.bus, 1, 0x4c)
        reg_map[0xcd] = DPLLSingleRegister(self.bus, 1, 0x4d)
        reg_map[0xce] = DPLLSingleRegister(self.bus, 1, 0x4e)
        reg_map[0xcf] = DPLLSingleRegister(self.bus, 1, 0x4f)
        reg_map[0xd0] = DPLLSingleRegister(self.bus, 1, 0x50)
        # Priority table status for DPLL1
        reg_map[0x100] = DPLLMultiRegister(self.bus, 2, 0x00, 2)
        # Operating status for DPLL1
        reg_map[0x102] = DPLLSingleRegister(self.bus, 2, 0x02)
        # Input mode configuration for DPLL1
        reg_map[0x116] = DPLLSingleRegister(self.bus, 2, 0x16)
        # Input select priority for DPLL1
        reg_map[0x118] = DPLLSingleRegister(self.bus, 2, 0x18)
        reg_map[0x119] = DPLLSingleRegister(self.bus, 2, 0x19)
        reg_map[0x11a] = DPLLSingleRegister(self.bus, 2, 0x1a)
        reg_map[0x11b] = DPLLSingleRegister(self.bus, 2, 0x1b)
        reg_map[0x11c] = DPLLSingleRegister(self.bus, 2, 0x1c)
        reg_map[0x11d] = DPLLSingleRegister(self.bus, 2, 0x1d)
        reg_map[0x11e] = DPLLSingleRegister(self.bus, 2, 0x1e)
        # Operating mode cfg for DPLL1
        reg_map[0x120] = DPLLSingleRegister(self.bus, 2, 0x20)
        # Priority table status for DPLL2
        reg_map[0x180] = DPLLMultiRegister(self.bus, 3, 0x00, 2)
        # Operating status for DPLL2
        reg_map[0x182] = DPLLSingleRegister(self.bus, 3, 0x02)
        # Input mode configuration for DPLL2
        reg_map[0x196] = DPLLSingleRegister(self.bus, 3, 0x16)
        # Input select priority for DPLL2
        reg_map[0x198] = DPLLSingleRegister(self.bus, 3, 0x18)
        reg_map[0x199] = DPLLSingleRegister(self.bus, 3, 0x19)
        reg_map[0x19a] = DPLLSingleRegister(self.bus, 3, 0x1a)
        reg_map[0x19b] = DPLLSingleRegister(self.bus, 3, 0x1b)
        reg_map[0x19c] = DPLLSingleRegister(self.bus, 3, 0x1c)
        reg_map[0x19d] = DPLLSingleRegister(self.bus, 3, 0x1d)
        reg_map[0x19e] = DPLLSingleRegister(self.bus, 3, 0x1e)
        # Operating mode cfg for DPLL2
        reg_map[0x1a0] = DPLLSingleRegister(self.bus, 3, 0x20)
        # Bandwidth related configuration registers for DPLL2
        reg_map[0x1a5] = DPLLMultiRegister(self.bus, 3, 0x25, 3)
        # Priority table status for DPLL3
        reg_map[0x200] = DPLLMultiRegister(self.bus, 4, 0x00, 2)
        # Operating status for DPLL3
        reg_map[0x202] = DPLLSingleRegister(self.bus, 4, 0x02)
        # Input mode configuration for DPLL3
        reg_map[0x216] = DPLLSingleRegister(self.bus, 4, 0x16)
        # Input select priority for DPLL2
        reg_map[0x218] = DPLLSingleRegister(self.bus, 4, 0x18)
        reg_map[0x219] = DPLLSingleRegister(self.bus, 4, 0x19)
        reg_map[0x21a] = DPLLSingleRegister(self.bus, 4, 0x1a)
        reg_map[0x21b] = DPLLSingleRegister(self.bus, 4, 0x1b)
        reg_map[0x21c] = DPLLSingleRegister(self.bus, 4, 0x1c)
        reg_map[0x21d] = DPLLSingleRegister(self.bus, 4, 0x1d)
        reg_map[0x21e] = DPLLSingleRegister(self.bus, 4, 0x1e)
        # Operating mode cfg for DPLL3
        reg_map[0x220] = DPLLSingleRegister(self.bus, 4, 0x20)
        # Dpll Compensation
        reg_map[0xc9] = DPLLSingleRegister(self.bus, 1, 0x49)
        reg_map[0xca] = DPLLSingleRegister(self.bus, 1, 0x4a)
        reg_map[0xcc] = DPLLSingleRegister(self.bus, 1, 0x4c)
        # Dpll 1 Output 2 Compensation
        reg_map[0x312] = DPLLSingleRegister(self.bus, 6, 0x12)
        reg_map[0x313] = DPLLSingleRegister(self.bus, 6, 0x13)
        reg_map[0x314] = DPLLSingleRegister(self.bus, 6, 0x14)
        reg_map[0x315] = DPLLSingleRegister(self.bus, 6, 0x15)
        reg_map[0x316] = DPLLSingleRegister(self.bus, 6, 0x16)
        reg_map[0x317] = DPLLSingleRegister(self.bus, 6, 0x17)
        # Dpll 2 Output 7 Compensation
        reg_map[0x34e] = DPLLSingleRegister(self.bus, 6, 0x4e)
        reg_map[0x34f] = DPLLSingleRegister(self.bus, 6, 0x4f)
        reg_map[0x350] = DPLLSingleRegister(self.bus, 6, 0x50)
        reg_map[0x351] = DPLLSingleRegister(self.bus, 6, 0x51)
        reg_map[0x352] = DPLLSingleRegister(self.bus, 6, 0x52)
        reg_map[0x353] = DPLLSingleRegister(self.bus, 6, 0x53)
        # Dpll 2 Temp holdover
        reg_map[0x38e] = DPLLSingleRegister(self.bus, 3, 0x2b)
        # Dpll 2 Temp holdover
        reg_map[0x480] = DPLLSingleRegister(self.bus, 2, 0x17)
        reg_map[0x490] = DPLLSingleRegister(self.bus, 3, 0x17)
        
        return reg_map

    def init_apll(self):
        apll_reg_map = {
                0x00: 0x00,
                0x01: 0x01,
                0x02: 0x01,
                0x03: 0x00,
                0x04: 0x35,
                0x05: 0x0c,
                0x06: 0x35,
                0x07: 0x0c,
                0x08: 0x35,
                0x09: 0x0c,
                0x0a: 0x02,
                0x0b: 0x00,
                0x0c: 0x02,
                0x0d: 0x00,
                0x0e: 0x00,
                0x0f: 0x01,
                0x10: 0x01
            }
        for key, value in apll_reg_map.items():
            reg = APLLRegister(self.bus, key)
            reg.setConfiguration(value)

    def setDPLLCompensation(self):
        self.reg_map[0xc9].setConfiguration(0xfa)
        self.reg_map[0xca].setConfiguration(0xfa)
        self.reg_map[0xcc].setConfiguration(0xfe)
        self.reg_map[0x312].setConfiguration(0x0)
        self.reg_map[0x313].setConfiguration(0x0)
        self.reg_map[0x314].setConfiguration(0x0)
        self.reg_map[0x315].setConfiguration(0x0)
        self.reg_map[0x316].setConfiguration(0x0)
        self.reg_map[0x317].setConfiguration(0xc0)

    def setDPLLTempHoldover(self):
        self.reg_map[0x38e].setConfiguration(0x40)
        
    def disableDpll3Gnss(self):
        self.reg_map[0x401].setConfiguration(0x0)    

    def disableInputLOSSync(self, input):
        base = 0xb5
        reg = 0xb5+input-1

        config = self.reg_map[reg].getConfiguration()

        config &= 0b00001111

        self.reg_map[reg].setConfiguration(config)

        self.logger.info("Successfully disable LOS sync for input %d %s %d", input, "by", config)

    def disableDPLLInput(self, dpll, input):
        # priority 0 means disable
        self.setDPLLInputPriority(dpll, input, 0)

    def initializeInterruptMask(self):
        # Configure default interrupt mask (hardcode)
        # Use default for 0x0D, 0x0E
        self.reg_map[0x0b].setConfiguration([0x00, 0x00, 0x00, 0x00])
        
    def enbleDPLLInterrupt(self, input):
        # Get mask 
        masks = self.reg_map[0x0b].getConfiguration()
        
        # 1-base to 0-base
        input = input - 1

        masks_new = []
        if input >= 0 and input <=7:
            masks[0] = masks[0] | 1<<input            
        elif input >= 8 and input <=15:
            masks[1] = masks[1] | 1<<(input-8)
            
        self.reg_map[0x0b].setConfiguration([masks[0], masks[1], masks[2], masks[3]])
        
    def disableDPLLInterrupt(self, input):
        # Get mask 
        masks = self.reg_map[0x0b].getConfiguration()
        
        # 1-base to 0-base
        input = input - 1        

        masks_new = []
        if input >= 0 and input <=7:
            masks[0] = masks[0] & ~(1<<input)          
        elif input >= 8 and input <=15:
            masks[1] = masks[1] & ~(1<<(input-8)) 
            
        self.reg_map[0x0b].setConfiguration([masks[0], masks[1], masks[2], masks[3]])
        
    def getDPLLInterrupt(self, input):
        # Get mask 
        masks = self.reg_map[0x0b].getConfiguration()
        
        # 1-base to 0-base
        input = input - 1

        masks_new = []
        if input >= 0 and input <=7:
            ret = masks[0]>>input & 1         
        elif input >= 8 and input <=15:
            ret = masks[1]>>(input-8) & 1
        
        return ret        

    def getInterrupts(self):
        interrupts = self.reg_map[0x07].getConfiguration()

        intr = {}
        # 0x07 0x08: Input interrupt
        inputs = []
        for i in range(1,9):
            data = interrupts[0]
            data >>= (i-1)
            data &= 0b1
            if data == 1:
                inputs.append(i)

        for i in range(9,15):
            data = interrupts[1]
            data >>= (i-9)
            data &= 0b1
            if data == 1:
                inputs.append(i)

        intr["inputs"] = inputs

        # 0x09: Only EEPROM interrupt enabled
        # TODO: TBD, check if needed
        # 0x0A: Disabled by default
        # TODO: To know DPLL status, it should be enabled

        return intr

    def clearInterruptStatus(self):
        self.reg_map[0x07].setConfiguration([0xff, 0xff, 0xff, 0xff])

    def getInputStatus(self, input):
        base = 0xa5
        reg = base+(input-1)

        value = self.reg_map[reg].getConfiguration()

        status = {}
        status["valid_dpll1"] = (value&0b01000000)>>6
        status["valid_dpll2"] = (value&0b10000000)>>7
        status["valid_dpll3"] = (value&0b00100000)>>5
        status["freq_hard_alarm"] = (value&0b00010000)>>4
        status["activity_alarm"] = (value&0b00000100)>>2
        status["phase_lock_alarm_dpll1"] = (value&0b00000001)
        status["phase_lock_alarm_dpll2"] = (value&0b00000010)>>1

        return status

    def getInputStatusDisqualify(self, input):
        base = 0xa5
        reg = base + (input-1)
        alarm_criteria = [0x01,  # PHASE_LOCK_ALARM_DPLL1
                          0x02,  # PHASE_LOCK_ALARM_DPLL2
                          0x04,  # ACTIVITY_ALARM
                          0x08,  # FREQ_SOFT_ALARM
                          0x10]  # FREQ_HARD_ALARM

        value = self.reg_map[reg].getConfiguration()
        i = 0
        for x in alarm_criteria:
            # Do not need to check FREQ_SOFT_ALARM
            if x == 0x08:
                i += 1
                continue

            rv = (value & x) >> i
            i += 1

            # The input clock will be disqualified if any alarm is raised
            if rv == 1:
                return 1

    def getDPLLPriorityTable(self, dpll):
        if dpll == IDT82P33831RegisterConst.DPLL1:
            reg = 0x100
        elif dpll == IDT82P33831RegisterConst.DPLL2:
            reg = 0x180
        elif dpll == IDT82P33831RegisterConst.DPLL3:
            reg = 0x200
        else:
            raise ValueError("DPLL index out of range: %d", dpll)

        data = self.reg_map[reg].getConfiguration()

        info = {}
        info["current"] = (data[0]&0b00001111)
        priority = []
        priority.append((data[0]&0b11110000)>>4)
        priority.append((data[1]&0b00001111))
        priority.append((data[1]&0b11110000)>>4)
        info["priority"] = priority

        return info

    def getDPLLOperatingStatus(self, dpll):
        if dpll == IDT82P33831RegisterConst.DPLL1:
            reg = 0x102
        elif dpll == IDT82P33831RegisterConst.DPLL2:
            reg = 0x182
        elif dpll == IDT82P33831RegisterConst.DPLL3:
            reg = 0x202
        else:
            raise ValueError("DPLL index out of range: %d", dpll)

        data = self.reg_map[reg].getConfiguration()

        status = {}
        lock = (data&0b00001000)>>3
        if lock == 1:
            status["dpll_lock"] = "Phase locked"
        else:
            status["dpll_lock"] = "Out of phase locked"
        op_status = (data&0b00000111)
        status["operating_status"] = OperatingStatus[op_status]

        return status

    def getDPLLInputPriority(self, dpll, input):
        if dpll == IDT82P33831RegisterConst.DPLL1:
            base = 0x118
        elif dpll == IDT82P33831RegisterConst.DPLL2:
            base = 0x198
        elif dpll == IDT82P33831RegisterConst.DPLL3:
            base = 0x218
        else:
            raise ValueError("DPLL index out of range: %d", dpll)

        reg = base+(input-1)//2

        config = self.reg_map[reg].getConfiguration()

        if input%2 == 1:
            config &= 0b00001111
        else:
            config >>=4

        return config

    def setDPLLInputPriority(self, dpll, input, priority):
        if dpll == IDT82P33831RegisterConst.DPLL1:
            base = 0x118
        elif dpll == IDT82P33831RegisterConst.DPLL2:
            base = 0x198
        elif dpll == IDT82P33831RegisterConst.DPLL3:
            base = 0x218
        else:
            raise ValueError("DPLL index out of range: %d", dpll)

        reg = base+(input-1)//2

        config = self.reg_map[reg].getConfiguration()

        if input%2 == 1:
            config &= 0b11110000
            config |= priority
        else:
            priority <<=4
            config &= 0b00001111
            config |= priority

        self.reg_map[reg].setConfiguration(config)

        self.logger.info("Successfully configure priority for dpll %d %s %d %s %d", dpll, "input", input, ":", priority)

    def getDPLLRevertiveMode(self, dpll):
        if dpll == IDT82P33831RegisterConst.DPLL1:
            reg = 0x116
        elif dpll == IDT82P33831RegisterConst.DPLL2:
            reg = 0x196
        elif dpll == IDT82P33831RegisterConst.DPLL3:
            reg = 0x216
        else:
            raise ValueError("DPLL index out of range: %d", dpll)

        config = self.reg_map[reg].getConfiguration()
        revertive = config & 0b00000001

        return revertive

    def setDPLLRevertiveMode(self, dpll, revertive):
        if dpll == IDT82P33831RegisterConst.DPLL1:
            reg = 0x116
        elif dpll == IDT82P33831RegisterConst.DPLL2:
            reg = 0x196
        elif dpll == IDT82P33831RegisterConst.DPLL3:
            reg = 0x216
        else:
            raise ValueError("DPLL index out of range: %d", dpll)

        config = self.reg_map[reg].getConfiguration()
        if revertive == 1:
            config |= 0b00000001
        else:
            config &= 0b11111110

        self.reg_map[reg].setConfiguration(config)

        self.logger.info("Successfully configure revertive mode for dpll%d %s %d", dpll, ":", revertive)

    def setSyncEOptionMode(self, mode):
        if mode == 1:
            # Option 1
            config = [0x4f, 0x6c, 0xca]
        elif mode == 2:
            # Option 2
            config = [0x4c, 0x69, 0xc9]
        else:
            raise ValueError("The select mode index is out of range (1-2)")

        self.reg_map[0x1a5].setConfiguration(config)

        self.logger.info("Successfully configured G.8262 to Option " + str(mode))

    def setDpllHitlessCfg(self, dpll, mode):
        if dpll == 1:
            reg = 0x480
        elif dpll == 2:
            reg = 0x490
        else:
            raise ValueError("The select dpll index is out of range (1-2)")
            
        config = self.reg_map[reg].getConfiguration()
        if mode == 1:
            # Disable hitless switching
            config &= 0b11111011
        elif mode == 2:
            # Enable histless switching
            config |= 0b00000100
        else:
            raise ValueError("The select mode index is out of range (1-2)")

        self.reg_map[reg].setConfiguration(config)

        self.logger.info("Successfully configure hitless to Option " + str(mode))
        
    def setDPLLFastLockMode(self, dpll):
        if dpll == 1:
            reg = 0x120
        elif dpll == 2:
            reg = 0x1A0
        elif dpll == 3:
            reg = 0x220
        else:
            raise ValueError("The dpll index is out of range (1-3)")

        # do free-run disable and enbable several times between msec
        for i in range(0, 3):
            self.reg_map[reg].setConfiguration(0b00000000)
            time.sleep(1)
            self.reg_map[reg].setConfiguration(0b00000001)

        self.logger.info("Successfully configured DPLL " + str(dpll) + " fast lock")

    def getInputClockPhaseOffsetCfg(self, input):
        base = 0xc5

        # address start from IN3 (0xc5)
        reg = base + (input - 3)
        offset = self.reg_map[reg].getConfiguration()

        # Do the calibrate if value is minus number
        if offset > 127:
            offset -= 256

        return offset * 0.61

    def setInputClockPhaseOffsetCfg(self, input, offset):
        base = 0xc5

        # address start from IN3 (0xc5)
        reg = base + (input - 3)
        self.reg_map[reg].setConfiguration(offset)

    def setDPLLOutputOffsetCfg(self, DPLL, ph1_reg, ph2_reg, fine_ph_reg):
        if DPLL == 1:
            # DPLL 1
            base = 0x312
        else:
            # DPLL 2
            base = 0x34e

        mask1 = 0b0000000000000000000011111111
        mask2 = 0b0000000000001111111100000000
        mask3 = 0b0000111111110000000000000000
        mask4 = 0b1111000000000000000000000000

        reg1 = ph2_reg & mask1
        reg2 = (ph2_reg & mask2) >> 8
        reg3 = (ph2_reg & mask3) >> 16
        reg4 = (ph2_reg & mask4) >> 24

        print("ph1_reg : " + str(hex(ph1_reg)))
        print("ph2_reg1: " + str(hex(reg1)))
        print("ph2_reg2: " + str(hex(reg2)))
        print("ph2_reg3: " + str(hex(reg3)))
        print("ph2_reg4: " + str(hex(reg4)))
        print("fine_ph_reg: " + str(hex(fine_ph_reg)))

        self.reg_map[base].setConfiguration(ph1_reg)
        self.reg_map[base+1].setConfiguration(reg1)
        self.reg_map[base+2].setConfiguration(reg2)
        self.reg_map[base+3].setConfiguration(reg3)
        self.reg_map[base+4].setConfiguration(reg4)
        self.reg_map[base+5].setConfiguration(fine_ph_reg)

    def setDPLLOpModeReg(self, dpll, mode):
        AUTO = 0
        FREERUN = 1
        HOLDOVER = 2

        if dpll == IDT82P33831RegisterConst.DPLL1:
            reg = 0x120
        elif dpll == IDT82P33831RegisterConst.DPLL2:
            reg = 0x1a0
        elif dpll == IDT82P33831RegisterConst.DPLL3:
            reg = 0x220
        else:
            raise ValueError("DPLL index out of range: %d", dpll)

        if mode > HOLDOVER or mode < AUTO:
            raise ValueError("The Operation Mode is out of range (Auto(" + \
                              str(AUTO) + ") to Hold-over(" + str(HOLDOVER) +"))")

        self.reg_map[reg].setConfiguration(mode)
        self.logger.info("Successfully configured DPLL operation mode " + str(mode))

class IDT82P33831RegisterConst:

    # DPLL
    DPLL1 = 1
    DPLL2 = 2
    DPLL3 = 3

    # INPUT
    INPUT1 = 1
    INPUT2 = 2
    INPUT3 = 3
    INPUT4 = 4
    INPUT5 = 5
    INPUT6 = 6
    INPUT7 = 7
    INPUT8 = 8
    INPUT9 = 9
    INPUT10 = 10
    INPUT11 = 11
    INPUT12 = 12
    INPUT13 = 13
    INPUT14 = 14

class DPLLRegister(abc.ABC):

    BUS = 0
    ADDR = 0x53
    PAGE = 0x7F    
        
    I2C_ADDR_MUX_9546 = 0x75
    IDT82P33831_CHANL = 3

    @abc.abstractmethod
    def setConfiguration(self, data):
        pass

    @abc.abstractmethod
    def getConfiguration(self, data):
        return None

    def _get_channel_bus(self, channel):
        parent = None
        # Proto and Alpha doesn't have parent MUX
        hw_rev = self.cpld.get_hw_rev()
        if hw_rev == self.cpld.HARDWARE_REV_PROTO_STR:
            pass
        elif hw_rev == self.cpld.HARDWARE_REV_ALPHA_STR:
            pass
        else:
            parent = "9546_ROOT1"

        if parent is None:
            return SMBus(0)
        if self.i2c_mux[parent].ch_bus != None:
            bus_num = self.i2c_mux[parent].ch_bus[channel]
            return SMBus(bus_num)
        else:
            bus = SMBus(0)
            bus.write_byte_data(self.I2C_ADDR_MUX_9546, 0x0, 1 << channel)
            return bus

    def _close_channel_bus(self, bus):
        parent = None
        # Proto and Alpha doesn't have parent MUX
        hw_rev = self.cpld.get_hw_rev()
        if hw_rev == self.cpld.HARDWARE_REV_PROTO_STR:
            pass
        elif hw_rev == self.cpld.HARDWARE_REV_ALPHA_STR:
            pass
        else:
            parent = "9546_ROOT1"

        if parent != None and self.i2c_mux[parent].ch_bus is None:
            bus.write_byte_data(self.I2C_ADDR_MUX_9546, 0x0, 0x0)
        bus.close()

class DPLLSingleRegister(DPLLRegister):

    def __init__(self, bus, page, register):
        self.BUS = bus
        self.page = page
        self.register = register
        self.cpld = CPLD()
        self.i2c_mux = I2CMux().MUXs

    def setConfiguration(self, data):
        try:
            bus = self._get_channel_bus(DPLLRegister.IDT82P33831_CHANL)
        except:
            raise

        try:

            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, self.page)
            bus.write_byte_data(DPLLRegister.ADDR, self.register, data)
            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, 0)
        except:
            raise
        finally:
            self._close_channel_bus(bus)

    def getConfiguration(self):
        try:
            bus = self._get_channel_bus(DPLLRegister.IDT82P33831_CHANL)
        except:
            raise

        try:
            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, self.page)
            b = bus.read_byte_data(DPLLRegister.ADDR, self.register)
            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, 0)

            return b
        except:
            raise
        finally:
            self._close_channel_bus(bus)

class DPLLMultiRegister(DPLLRegister):

    def __init__(self, bus, page, register, length):
        if bus != 0:
            self.BUS = bus
        self.page = page
        self.register = register
        self.length = length
        self.cpld = CPLD()
        self.i2c_mux = I2CMux().MUXs

    def setConfiguration(self, data):
        # TODO: Check if data is list with right length
        try:
            bus = self._get_channel_bus(DPLLRegister.IDT82P33831_CHANL)
        except:
            raise

        try:
            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, self.page)
            for idx, datum in enumerate(data):
                bus.write_byte_data(DPLLRegister.ADDR, self.register+idx, datum)
            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, 0)
        except:
            raise
        finally:
            self._close_channel_bus(bus)

    def getConfiguration(self):
        data = []
        try:
            bus = self._get_channel_bus(DPLLRegister.IDT82P33831_CHANL)
        except:
            raise

        try:
            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, self.page)
            for idx in range(0, self.length):
                data.append(bus.read_byte_data(DPLLRegister.ADDR, self.register+idx))
            bus.write_byte_data(DPLLRegister.ADDR, DPLLRegister.PAGE, 0)

            return data
        except:
            raise
        finally:
            self._close_channel_bus(bus)

class APLLRegister:

    BUS = 0
    ADDR = 0x52

    def __init__(self, bus, register):
        self.BUS = bus
        self.register = register
        self.cpld = CPLD()
        self.i2c_mux = I2CMux().MUXs

    def _get_channel_bus(self, channel):
        parent = None
        # Proto and Alpha doesn't have parent MUX
        hw_rev = self.cpld.get_hw_rev()
        if hw_rev == self.cpld.HARDWARE_REV_PROTO_STR:
            pass
        elif hw_rev == self.cpld.HARDWARE_REV_ALPHA_STR:
            pass
        else:
            parent = "9546_ROOT1"

        if parent is None:
            return SMBus(self.BUS)
        if self.i2c_mux[parent].ch_bus != None:
            bus_num = self.i2c_mux[parent].ch_bus[channel]
            return SMBus(bus_num)
        else:
            bus = SMBus(self.BUS)
            bus.write_byte_data(DPLLRegister.I2C_ADDR_MUX_9546, 0x0, 1 << channel)
            return bus

    def _close_channel_bus(self, bus):
        parent = None
        # Proto and Alpha doesn't have parent MUX
        hw_rev = self.cpld.get_hw_rev()
        if hw_rev == self.cpld.HARDWARE_REV_PROTO_STR:
            pass
        elif hw_rev == self.cpld.HARDWARE_REV_ALPHA_STR:
            pass
        else:
            parent = "9546_ROOT1"

        if parent != None and self.i2c_mux[parent].ch_bus is None:
            bus.write_byte_data(DPLLRegister.I2C_ADDR_MUX_9546, 0x0, 0x0)
        bus.close()

    def setConfiguration(self, data):
        try:
            bus = self._get_channel_bus(DPLLRegister.IDT82P33831_CHANL)
        except:
            raise

        try:
            bus.write_byte_data(APLLRegister.ADDR, self.register, data)
        except:
            raise
        finally:
            self._close_channel_bus(bus)

    def getConfiguration(self):
        try:
            bus = self._get_channel_bus(DPLLRegister.IDT82P33831_CHANL)
        except:
            raise

        try:
            b = bus.read_byte_data(APLLRegister.ADDR, self.register)

            return b
        except:
            raise
        finally:
            self._close_channel_bus(bus)
