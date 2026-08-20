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

USB device in NEOM8T:
NEOM8T has many interfaces for communication.
Choose USB interface to write configuration/request to NEOM8T

This class provide interfaces to send UBX messages to NEOM8T

"""
import time
from multiprocessing.pool import ThreadPool

import usb.core
import usb.util

from common.logger import Logger
from timing.ubx import ubx_utils
from timing.ubx.ubx_command import UBXCommand
from timing.ubx.ubx_message import UBXMessage
from timing.ubx.ubx_cfg_msg import UBX_CFG_MSG
from timing.ubx.ubx_cfg_tp5 import UBX_CFG_TP5

class GPSUSB:

    idVendor = 0x1546
    idProduct = 0x01a8

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        # Find USB device
        usb_dev = usb.core.find(idVendor=GPSUSB.idVendor, idProduct=GPSUSB.idProduct)
        if usb_dev is None:
            raise ValueError('USB device not found')
        else:
            self.usb_dev = usb_dev

        # See if a kernel driver is active already, if so detach it and store a
        # flag so we can reattach when we are done
        if usb_dev.is_kernel_driver_active(0):
            self.usb_dev.detach_kernel_driver(0)

        # Set the active configuration. With no arguments, the first configuration
        # will be the active one
        # NOTE: This may cause error: [Errno 16] Resource busy
        self.usb_dev.set_configuration()

    def __del__(self):
        # Find USB device
        usb_dev = usb.core.find(idVendor=GPSUSB.idVendor, idProduct=GPSUSB.idProduct)
        
        # This is needed to release interface, otherwise attach_kernel_driver fails
        # due to "Resource busy"
        usb.util.dispose_resources(self.usb_dev)

        # Reattach device if needed
        # Prevent power on init error
        usb_dev.attach_kernel_driver(0)

    # Workaround: Write and read something to make function work
    def enable(self):
        cfg = self.usb_dev.get_active_configuration()
        intf = cfg[(1,0)]

        ep_out = usb.util.find_descriptor(
                intf,
                # match the first OUT endpoint
                custom_match = \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT)
        if ep_out is None:
            raise ValueError('EndpointAddress of USB device not found')

        # Write something. It is magic to make function work.
        nmea = UBX_CFG_MSG([0xF0, 0x01], 0, 0, 0, 0, 0)
        self._write(nmea.getMessage())

        # Read something. It is magic to make function work.
        self.clearBuffer()

    def _write(self, cmd):
        cfg = self.usb_dev.get_active_configuration()
        intf = cfg[(1,0)]

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

    def _read(self, class_id):
        cfg = self.usb_dev.get_active_configuration()
        intf = cfg[(1,0)]

        ep = usb.util.find_descriptor(
                intf,
                # match the first IN endpoint
                custom_match = \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_IN)
        if ep is None:
            raise ValueError('EndpointAddress of USB device not found')

        ack = False
        response = None

        read = True
            
        while read:
            try:
                resp = ep.read(500)
                self.logger.debug("GPS read: %s", resp)
                if len(resp) == 0:
                    continue

                msg = UBXMessage(resp)
                if msg.class_id == ubx_utils.CLASS_ACK_ACK:
                    ack = True
                    read = False
                elif msg.class_id == ubx_utils.CLASS_ACK_NAK:
                    ack = False
                    read = False
                elif msg.class_id == class_id:
                    ack = True
                    response = msg.getMessage()
                    read = False
            except:
                # Continuous read until timeout
                read = False
                self.logger.debug("Read command timeout")
                raise

        return (ack, response)

    def clearBuffer(self):
        cfg = self.usb_dev.get_active_configuration()
        intf = cfg[(1,0)]

        ep = usb.util.find_descriptor(
                intf,
                # match the first IN endpoint
                custom_match = \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_IN)
        if ep is None:
            raise ValueError('EndpointAddress of USB device not found')

        read = True
        while read:
            try:
                resp = ep.read(500)
                #self.logger.debug(resp)
            except:
                # Continuous read until timeout
                read = False

    def _gps_set(self, cmd):
        # Prepare to read
        with ThreadPool(processes=1) as pool:
            msg = UBXMessage(cmd)
            async_result = pool.apply_async(self._read, (msg.class_id,))

            # Write command
            self._write(cmd)

            (result, response) = async_result.get()

        if result is False:
            raise ValueError("Failed to set GPS configuration")

    def _gps_get(self, cmd):
        # Prepare to read
        with ThreadPool(processes=1) as pool:
            msg = UBXMessage(cmd)
            async_result = pool.apply_async(self._read, (msg.class_id,))

            # Write command
            self._write(cmd)

            (result, response) = async_result.get()

        if result is False:
            raise ValueError("Failed to get GPS configuration")

        return response

    def disableNMEAMessage(self):
        # In this implementation, GNTXT can not be disabled.
        # If it is an issue, use port configuration to disable all NMEA messages
        for i in [0, 1, 2, 3, 4, 5, 8]:
            nmea = UBX_CFG_MSG([0xF0, i], 0, 0, 0, 0, 0)
            self._write(nmea.getMessage())

        # Wait for reponse message gone
        # (This code maybe can be removed. Just for safety)

    def configureTimePulse2(self):
        self.configureTimePulse(UBXCommand.cmdCfgTP2)

    def configureUartTod(self):
        self.configureUart(UBXCommand.cmdCfgTod1)
        self.configureUart(UBXCommand.cmdCfgTod2)
        self.configureUart(UBXCommand.cmdCfgTod3)
        self.configureUart(UBXCommand.cmdCfgTod4)
        self.configureUart(UBXCommand.cmdCfgTod5)
        self.configureUart(UBXCommand.cmdCfgTod6)
        self.configureUart(UBXCommand.cmdCfgTod7)
        self.configureUart(UBXCommand.cmdCfgTod8)
        self.configureUart(UBXCommand.cmdCfgTod9)
        self.configureTimePulse(UBXCommand.cmdCfgTP2)
        self.configureUart(UBXCommand.cmdCfgTod10)
        self.configureUart(UBXCommand.cmdCfgUartZDAEn)


    def getTimePulseCfg(self, timePulse):
        cmd = UBX_CFG_TP5.timePulseCommand(timePulse)
        response = self._gps_get(cmd)

        return response

    def configureTimePulse(self, cmd):
        result = self._gps_set(cmd)

    def configureUart(self, cmd):
        result = self._gps_set(cmd)
        

