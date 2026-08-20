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

class UBX_CFG_PRT(UBXMessage):

    class_id = [0x06, 0x00]

    def transPortClass(self):
        if self.length == 20: # TODO: Change to use port id
            return UBX_CFG_PRT_UART(self.getMessage())
        else:
            raise ValueError("Not handled message length: ", self.length)

    @staticmethod
    def portConfigCommand(portId):
        cmd = []
        cmd += UBX_CFG_PRT.sync_char
        buf = []
        buf += UBX_CFG_PRT.class_id
        buf += [0x01, 0x00]
        buf += [portId]
        cmd += buf
        cmd += ubx_utils.getCheckSum(buf)

        return cmd

class UBX_CFG_PRT_UART(UBX_CFG_PRT):

    def getBaudRate(self):
        rate = self.payload[8]
        rate |= (self.payload[9]<<8)
        rate |= (self.payload[10]<<16)
        rate |= (self.payload[11]<<24)

        return rate

    def setBaudRate(self, rate):
        self.payload[8] = rate&0b11111111
        self.payload[9] = (rate>>8)&0b11111111
        self.payload[10] = (rate>>16)&0b11111111
        self.payload[11] = (rate>>24)&0b11111111

