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
"""

CP2130 in SIAD:
USB-to-SPI bridge for communicating with IDT82P2281

This class provide interfaces to control IDT82P2281

"""

import os
import sys

import usb.core
import usb.util

from common.logger import Logger

class CP2130:

    idVendor = 0x10c4
    idProduct = 0x87a0

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        # Find USB device (CP2130)
        usb_dev = usb.core.find(idVendor=CP2130.idVendor, idProduct=CP2130.idProduct)
        if usb_dev is None:
            raise ValueError("USB device not found")
        else:
            self.usb_dev = usb_dev

        # Set the active configuration. With no arguments, the first configuration
        # will be the active one
        # NOTE: This may cause error: [Errno 16] Resource busy
        # self.usb_dev.set_configuration()

    def __del__(self):
        pass

    def init(self):
        # Set clock of channel 0 to 1.5MHz
        self.usb_dev.ctrl_transfer(0x40, 0x31, 0, 0, [0x00, 0x0b])

    def _write_cmd(self, cmd):
        cfg = self.usb_dev.get_active_configuration()
        intf = cfg[(0,0)]
        ep = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match = \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT)
        if ep is None:
            raise ValueError('EndpointAddress of USB device not found')

        ep.write(cmd)

    def _read_cmd(self):
        cfg = self.usb_dev.get_active_configuration()
        intf = cfg[(0,0)]
        ep = usb.util.find_descriptor(
            intf,
            # match the first IN endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)
        if ep is None:
            raise ValueError("EndpointAddress of USB device not found")

        # We should give enough buffer side to read. 3 is OK. 100 is for safety.
        return ep.read(100)

    def _read_data(self, register):
        cmd = cmdGet(register)
        self._write_cmd(cmd)

        data = self._read_cmd()
        if len(data) < 3:
            raise ValueError("Data read from device is too few. Only ", len(data))

        return data[2]

    def get_operating_mode(self):
        data = self._read_data(T1Register.MODE_SEL)

        return data

    def set_operating_mode(self, mode):
        cmd = cmdSet(T1Register.MODE_SEL, mode)
        self._write_cmd(cmd)

    def software_reset(self):
        cmd = cmdSet(T1Register.SW_RESET, 0x00)
        self._write_cmd(cmd)

    def set_output_control_no_mclk(self):
        cmd = cmdSet(T1Register.RC_OC, 0x01)
        self._write_cmd(cmd)

    def get_interrupt_enable(self):
        data = self._read_data(T1Register.INTR_EN)
        return data

    def set_interrupt_enable(self, ie):
        cmd = cmdSet(T1Register.INTR_EN, ie)
        self._write_cmd(cmd)

    def get_line_status(self):
        data = self._read_data(T1Register.LINE_ST)
        return data

    def clear_interrupt_status(self, status):
        cmd = cmdSet(T1Register.INTR_ST, status)
        self._write_cmd(cmd)

    def set_cfg_transmit(self, cfg):
        cmd = cmdSet(T1Register.CFG_TSM, cfg)
        self._write_cmd(cmd)

    def set_term_cfg_tx_rx(self, cfg):
        cmd = cmdSet(T1Register.TERM_TXRX, cfg)
        self._write_cmd(cmd)

    def set_intr_tri_edge_sel(self, value):
        cmd = cmdSet(T1Register.INTR_TES, value)
        self._write_cmd(cmd)

def cmdGet(register):
    cmd = []
    cmd += [0x00, 0x00]             # Reserved
    cmd += [0x02]                   # Write Read
    cmd += [0x00]                   # Reserved
    cmd += [0x03, 0x00, 0x00, 0x00] # Write 3 bytes, little-endian
    cmd += [0x80, register, 0x00]
    return cmd

def cmdSet(register, config):
    cmd = []
    cmd += [0x00, 0x00]             # Reserved
    cmd += [0x01]                   # Write
    cmd += [0x00]                   # Reserved
    cmd += [0x03, 0x00, 0x00, 0x00] # Write 3 bytes, little-endian
    cmd += [0x00, register, config]
    return cmd

class T1Register:

    SW_RESET = 0x04                 # Software Reset
    MODE_SEL = 0x20                 # T1/J1 or E1 Mode
    CFG_TSM  = 0x23                 # Transmit Configuration
    TERM_TXRX= 0x32                 # Transmit and Receive Termination Cfg
    INTR_EN  = 0x33                 # Interrupt Enable Control
    INTR_TES = 0x35                 # Interrupt Trigger Edges Select
    LINE_ST  = 0x36                 # Line Status Reg 0
    INTR_ST  = 0x3A                 # Interrupt Status 0
    RC_OC    = 0x3E                 # Reference Clock Output Control

