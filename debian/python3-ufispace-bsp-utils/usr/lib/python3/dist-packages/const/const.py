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
from enum import IntEnum

class SFP(IntEnum):
    UNDETECTED = 0
    DETECTED = 1

class PortRate(IntEnum):
    Rate_1G = 0
    Rate_10G = 1

class PortStatus(IntEnum):
    ENABLED = 0
    DISABLED = 1

    QSFP_PRESENCE = 0
    QSFP_ABSENCE = 1

    SFP_PRESENCE = 0
    SFP_ABSENCE = 1

class Led(IntEnum):
    SYSTEM = 0
    POWER = 1
    FAN = 2
    GPS = 3
    SYNC = 4

    STATUS_OFF = 0
    STATUS_ON = 1

    COLOR_YELLOW = 0
    COLOR_GREEN = 1

    BLINK_STATUS_SOLID = 0
    BLINK_STATUS_BLINKING = 1

class CPLDConst(IntEnum):
    LOC_MB = 0
    LOC_CPU = 1

    UART_SOURCE_CPU = 0
    UART_SOURCE_BMC = 1

class LPMode(IntEnum):
    DISABLE = 0
    ENABLE = 1
