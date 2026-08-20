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
SYNC_CHAR = [0xB5, 0x62]
CLASS_ACK_NAK = [0x05, 0x00]
CLASS_ACK_ACK = [0x05, 0x01]
CLASS_CFG_TP5 = [0x06, 0x31]

def cmdAckAck(class_id):
    ack = []
    ack += SYNC_CHAR
    buf = []
    buf += CLASS_ACK_ACK
    buf += [0x02, 0x00]
    buf += class_id
    ack += buf
    ack += getCheckSum(buf)

    return ack

def getCheckSum(buffer):
    ck_a = 0x00
    ck_b = 0x00
    for i in range(0,len(buffer)):
        ck_a = (ck_a + buffer[i])%256
        ck_b = (ck_b + ck_a)%256

    return [ck_a, ck_b]

def msgLength(msg):
    if len(msg) < 8:
        raise ValueError("Not UBX message")

    return msg[4]+(msg[5]<<8)
