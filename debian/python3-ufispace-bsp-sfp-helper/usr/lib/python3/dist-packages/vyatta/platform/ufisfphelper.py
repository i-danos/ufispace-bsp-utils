#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019-2021, AT&T Intellectual Property.  All rights reserved.
#
# SPDX-License-Identifier: LGPL-2.1-only


import errno
import os
import select
import subprocess
from Interrupt_utility import InterruptUtility
from QSFP_utility import QSFPUtility
from SFP_utility import SFPUtility
from cpld.cpld import CPLD
from eeprom.eeprom import EEPRom
from vyatta.platform.basesfphelper import BaseSfpHelper
from vyatta.platform.basesfphelper import ModuleNotPresentException
from vyatta.phy.basephy import PhyNotFoundException

class UfiSfpHelper(BaseSfpHelper):

    def __init__(self, sfpd):
        self.sfp_plugged = dict.fromkeys(SFPUtility().VALID_PORTS, False)
        self.qsfp_plugged = dict.fromkeys(QSFPUtility().VALID_PORTS, False)
        self.sfpd = sfpd
        self.eeprom = EEPRom()

    class UfiBus():
        def __init__(self, resource, port):
            self.resource = resource
            self.port = port

        def read_word_data(self, addr, cmd):
            try:
                return self.resource.bus.read_word_data(addr, cmd)
            except OSError as e:
                if e.errno == errno.EBUSY:
                    self.resource.reset_mux(self.port)
                    raise PhyNotFoundException('module failed to respond; MUX reset')
                raise e

        def write_word_data(self, addr, cmd, val):
            try:
                self.resource.bus.write_word_data(addr, cmd, val)
            except OSError as e:
                if e.errno == errno.EBUSY:
                    self.resource.reset_mux(self.port)
                    raise PhyNotFoundException('module failed to respond; MUX reset')
                raise e

    class UfiBusResource():
        def __init__(self, parent, porttype, port):
            self.parent = parent
            self.porttype = porttype
            self.port = port
            self.eeprom = EEPRom()
            self.cpld = CPLD()

        def open(self):
            if self.porttype == 'SFP':
                return self.eeprom.get_sfp_bus(self.port)
            elif self.porttype == 'QSFP':
                return self.eeprom.get_qsfp_bus(self.port)
            else:
                raise Exception("unexpected port type {}".format(self.porttype))

        def close(self, bus):
            if self.porttype == 'SFP':
                return self.eeprom.close_sfp_bus(self.port, bus)
            elif self.porttype == 'QSFP':
                return self.eeprom.close_qsfp_bus(self.port, bus)
            else:
                raise Exception("unexpected port type {}".format(self.porttype))

        def reset_mux(self, port):
            if self.porttype == 'SFP':
                return self.cpld.mux_reset_by_sfp_port(port)
            elif self.porttype == 'QSFP':
                return self.cpld.mux_reset_by_qsfp_port(port)
            else:
                raise Exception("unexpected port type {}".format(self.porttype))

        def __enter__(self):
            self.bus = self.open()
            return self.parent.UfiBus(self, self.port)

        def __exit__(self, *args):
            self.close(self.bus)
            self.bus = None

    def get_bus(self, porttype, port):
        return self.UfiBusResource(self, porttype, port)

    def set_sfp_state(self, portname, enabled):
        if portname.startswith('xe'):
            port = int(portname[2:])
            SFPUtility().set_port_status(port, not enabled)
            # Disabling the port will have reset the PHY, so re-enable
            if enabled:
                self.set_sgmii_enabled('SFP', port)
        elif portname.startswith('ce'):
            # Attempt to extract the sub-port index if broken out.
            # Note: the sub-port number is 0-based.
            subportparts = portname[2:].split('p', 1)
            port = int(subportparts[0])
            subport = None
            if len(subportparts) > 1:
                subport = int(subportparts[1])
            # Unlike with SFPs where a pin status is changed, this
            # only works when the module is plugged in
            try:
                # send command to QSFP port to disable the Tx laser
                self.eeprom.set_tx_laser(port, enabled, subport)
            except OSError:
                raise ModuleNotPresentException('ce' + str(port))
        else:
            raise Exception("unexpected port type {}".format(portname))

    def query_eeprom(self, porttype, port):
        pages = []
        if porttype == 'SFP':
            a0_data = []
            try:
                a0_data = self.eeprom.dump_sfp_eeprom(port, page="A0")
            except OSError:
                raise ModuleNotPresentException(porttype + ' ' + str(port) + ' page A0 not available')
            pages.append(0xa0)
            # We don't support address changing, so treat that as no DDM info
            dmt_implemented = a0_data[self.DMT_BYTE] & (self.DMT_IMPL|self.DMT_ADDR_CHNG_REQ) == self.DMT_IMPL
            if dmt_implemented:
                pages.append(0xa2)
        elif porttype == 'QSFP':
            for page in range(4):
                # Assume that pages 00h - 03h are present
                pages.append(page)
        else:
            raise Exception("unexpected port type {}".format(porttype))
        return pages

    def read_eeprom(self, porttype, port, offset=None, length=None):
        data = []
        if porttype == 'SFP':
            if offset is None:
                offset = 0
            if length is None:
                length = 512
            for page in range((offset // 256) * 256, offset + length, 256):
                try:
                    if page == 0:
                        data += self.eeprom.dump_sfp_eeprom(port, page="A0")
                    else:
                        data += self.eeprom.dump_sfp_eeprom(port, page="A2")
                except OSError:
                    raise ModuleNotPresentException('xe' + str(port) + ' page ' + str(page) + ' not available')

            # Only required pages were retrieved, so now trim head and
            # tail appropriately
            data = data[offset % 256:offset % 256 + length]
        elif porttype == 'QSFP':
            if offset is None:
                offset = 0
            if length is None:
                length = 128 + 4 * 128
            # Handle lower and upper page 00h specially since these
            # are retrieved in one go
            if offset < 256:
                try:
                    data += self.eeprom.dump_qsfp_eeprom(port, 0)
                except OSError:
                    raise ModuleNotPresentException('ce' + str(port) + ' page 0  not available')
                # Handle offsets/lengths within the 256-length
                # page. Remainders will be dealt with below
                if offset // 128 == 1:
                    data = data[128:]
                if (length + offset) // 128 == 0:
                    data = data[:128]
            for page in range(max(((offset - 256) // 128) * 128, 0), offset - 256 + length, 128):
                try:
                    data += self.eeprom.dump_qsfp_eeprom(port, page // 128 + 1)
                except OSError:
                    raise ModuleNotPresentException('ce' + str(port) + ' page ' + str(page) + ' not available')
            # Only required pages were retrieved, so now trim head and
            # tail appropriately
            data = data[offset % 128:offset % 128 + length]
        else:
            raise Exception("unexpected port type {}".format(porttype))
        return bytes(data)

    def _walk_ports(self, sfp, qsfp):
        for port in SFPUtility().VALID_PORTS:
            presence = False
            try:
                presence = sfp.get_presence(port)["presence"] == "presence"
                # Need to clear by read presence/tx_fault/rx_lost
                rx_lost = sfp.get_rx_lost(port)["rx_lost"]
                tx_fault = sfp.get_tx_fault(port)["tx_flt"]
            except OSError:
                pass
            if presence != self.sfp_plugged[port]:
                self.sfp_plugged[port] = presence
                self.sfpd.on_sfp_presence_change('xe' + str(port),
                                                 'SFP', port, presence)

        for port in QSFPUtility().VALID_PORTS:
            presence = False
            try:
                presence = qsfp.get_presence(port)["presence"] == "presence"
            except OSError:
                pass
            if presence != self.qsfp_plugged[port]:
                self.qsfp_plugged[port] = presence
                self.sfpd.on_sfp_presence_change('ce' + str(port),
                                                 'QSFP', port, presence)

    def main_loop(self, file_evmask_tuple_list):
        p = select.poll()
        sfp = SFPUtility()
        qsfp = QSFPUtility()

        for (f, evmask) in file_evmask_tuple_list:
            p.register(f, evmask)

        # gather state at boot
        self._walk_ports(sfp, qsfp)
        self.sfpd.boot_walk_complete()

        # disable interrupts first, then load module
        interrupt_utility = InterruptUtility()
        # Global_Mask is for all interrupt Mask and Port_Mask is
        # for SFP/QSFP module interrupt. Disabling them means ALLOW
        # interrupt and ENABLE port interrupt
        interrupt_utility.disable_interrupt_mask("Global_Mask")
        interrupt_utility.disable_interrupt_mask("Port_Mask")

        # load module from here rather than the service, so that
        # it doesn't happen on !siad
        subprocess.call(['modprobe', 'gpio15_intr'])

        with open('/proc/GPIO15', 'r+') as proc:
            p.register(proc, select.POLLPRI)
            while True:
                # need to enable interrupts in the kmod after each wake up
                print(1, file=proc, flush=True)
                evtuple_list = p.poll()
                for (fd, event) in evtuple_list:
                    if fd == proc.fileno():
                        self._walk_ports(sfp, qsfp)
                    else:
                        self.sfpd.on_file_event(fd, event)

def new_helper(sfpd):
    return UfiSfpHelper(sfpd)
