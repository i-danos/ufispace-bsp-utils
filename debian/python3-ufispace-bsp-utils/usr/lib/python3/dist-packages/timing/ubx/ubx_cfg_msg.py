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

class UBX_CFG_MSG(UBXMessage):

    class_id = [0x06, 0x01]
    length = 8

    def __init__(self, msg, i2c, uart1, uart2, usb, spi):
        self.payload = []
        self.payload += msg     # message class id
        self.payload += [i2c]   # i2c   (1/0)
        self.payload += [uart1] # uart1 (1/0)
        self.payload += [uart2] # uart2 (1/0)
        self.payload += [usb]   # usb   (1/0)
        self.payload += [spi]   # spi   (1/0)
        self.payload += [0x00]  # sixth I/O port
