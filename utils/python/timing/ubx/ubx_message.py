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

class UBXMessage:

    sync_char = [0xB5, 0x62]
    class_id = [0x00, 0x00]
    length = 0
    payload = []

    def __init__(self, msg):
        self.class_id = [ msg[2], msg[3] ]
        self.length = msg[4]+(msg[5]<<8)
        self.payload = msg[6:(6+self.length)]
        pass

    def getPayload(self):
        return self.payload

    def getMessage(self):
        msg = []
        msg += self.sync_char
        buf = []
        buf += self.class_id
        buf += [self.length&0b0000000011111111]
        buf += [self.length&0b1111111100000000]
        buf += self.getPayload()
        msg += buf
        msg += ubx_utils.getCheckSum(buf)
        return msg

