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
from timing.ubx import ubx_utils
from timing.ubx.ubx_message import UBXMessage

class UBX_CFG_TP5(UBXMessage):

    class_id = [0x06, 0x31]

    def getAntennaCableDelay(self):
        delay = self.payload[4] + (self.payload[5]<<8)
        return delay

    def setAntennaCableDelay(self, delay):
        self.payload[4] = delay & 0b11111111
        self.payload[5] = delay >> 8

    @staticmethod
    def timePulseCommand(timePulse):
        cmd = []
        cmd += UBX_CFG_TP5.sync_char
        buf = []
        buf += UBX_CFG_TP5.class_id
        buf += [0x01, 0x00]
        buf += [timePulse]
        cmd += buf
        cmd += ubx_utils.getCheckSum(buf)

        return cmd
