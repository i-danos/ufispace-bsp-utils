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
class CPLDMBRegProto(object):
    REG_BOARD_ID               = 0x00
    REG_BOARD_EXTEND_BOARD_ID  = 0x01
    REG_CODE_VERSION           = 0x02
    REG_PLL_LOCK               = 0x03
    REG_SMU_INPUT_LOST         = 0x04
    REG_FAN_PRESENT            = 0x05
    REG_MULTI_INTF_SEL         = 0x06
    REG_PTP_CONTROL            = 0x07
    REG_POWER_STATUS           = 0x08
    REG_POWER_CONTROL          = 0x09
    REG_PORT_OVER_CURRENT      = 0x0A
    REG_FAN_INTR               = 0x0B
    REG_NMI_INTR               = 0x0C
    REG_MAC_PHY_INTR           = 0x0D
    REG_SYNCE_PTP_INTR         = 0x0E
    REG_PORT_INTR              = 0x0F
    REG_MISC_INTR              = 0x10
    REG_INTR_MASK              = 0x11
    REG_RESET_STATUS           = 0x12
    REG_I2C_IOEXP_RESET        = 0x13
    REG_BMC_RESET              = 0x14
    REG_MAC_PHY_PLL_TPM_RESET  = 0x15
    REG_MISC_RESET             = 0x16
    REG_GLOBAL_RESET           = 0x17
    REG_SYS_LED1               = 0x18
    REG_SYS_LED2               = 0x19
    REG_SYS_LED_BLINKING       = 0x1A
    REG_FAN_BOARD_LED1         = 0x1B
    REG_FAN_BOARD_LED2         = 0x1C
    REG_FAN_BOARD_LED_BLINKING = 0x1D

class CPLDMBReg(object):
    REG_BOARD_ID               = 0x00
    REG_BOARD_EXTEND_BOARD_ID  = 0x01
    REG_CODE_VERSION           = 0x02
    REG_PLL_LOCK               = 0x03
    REG_SMU_INPUT_LOST         = 0x04
    REG_FAN_PRESENT            = 0x05
    REG_MULTI_INTF_SEL         = 0x06
    REG_PTP_CONTROL            = 0x07
    REG_POWER_STATUS           = 0x08
    REG_POWER_CONTROL          = 0x09
    REG_PORT_OVER_CURRENT      = 0x0A
    REG_FAN_INTR               = 0x0B
    REG_NMI_INTR               = 0x0C
    REG_MAC_PHY_INTR           = 0x0D
    REG_SYNCE_PTP_INTR         = 0x0E
    REG_PORT_INTR              = 0x0F
    REG_MISC_INTR              = 0x10
    REG_INTR_MASK              = 0x11
    REG_RESET_STATUS           = 0x12
    REG_I2C_IOEXP_RESET        = 0x13
    REG_BMC_RESET              = 0x14
    REG_MAC_PHY_PLL_TPM_RESET  = 0x15
    REG_MISC_RESET             = 0x16
    REG_GLOBAL_RESET           = 0x17
    REG_SYS_LED1               = 0x18
    REG_SYS_LED2               = 0x19
    REG_SYS_LED_BLINKING       = 0x1A
    REG_FAN4_FAN5_TACH_IN_CTRL = 0x1B
    REG_GNSS_STATUS_REGISTER   = 0x1C

class CPLDCPUReg(object):
    REG_CPLD_REVISION = 0x00

class SMBUSMEMReg(object):
    REG_SLAVE_CMD = 0x11

