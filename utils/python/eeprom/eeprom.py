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
import os
import sys
from time import sleep

from common.logger import Logger
from i2c_mux.i2c_mux import I2CMux
from gpio.ioexp import IOExpander
from smbus import SMBus
from cpld.cpld import CPLD
from protocol.i2c import I2C

class DATA_INFO:
    SFP = {
        "list":[
            ["Identifier",   1, "hex"],
            ["Extend_ID",    1, "dec"],
            ["Connector",    1, "hex"],
            ["Transceiver",  8, "str"],
            ["Encoding",     1, "dec"],
            ["Baudrate",     1, "dec"],
            ["Rate_ID",      1, "dec"],
            ["Length_9u_km", 1, "dec"],
            ["Length_9u",    1, "dec"],
            ["Length_50u",   1, "dec"],
            ["Length_62_5u", 1, "dec"],
            ["Length_Cu",    1, "dec"],
            ["reserve2",     1, "hex"],
            ["Vendor_Nme",  16, "str"],
            ["reserve3",     1, "hex"],
            ["Vendor_OUI",   3, "hex"],
            ["Vendor_PN",   16, "str"],
            ["vendor_Rev",   4, "hex"],
            ["Wavelength",   2, "hex"],
            ["reserve4",     1, "hex"],
            ["CC_Base",      1, "dec"],
            ["Options",      2, "hex"],
            ["BR_Max",       1, "dec"],
            ["BR_Min",       1, "dec"],
            ["Serial_No",   16, "str"],
            ["Date_Code",    8, "str"],
            ["reserve5",     3, "hex"],
            ["CC_ext",       1, "dec"],
            ["Vendor_Specific", 16, "str"]            
        ]
    }
    
    QSFP = {
        "list":[
            ["Low_Memory",         127, "str"],
            ["Page_Sel",             1, "hex"],
            ["Identifier",           1, "hex"],
            ["Extend_ID",            1, "dec"],
            ["Connector",            1, "hex"],
            ["Transceiver",          8, "str"],
            ["Encoding",             1, "dec"],
            ["Baudrate",             1, "dec"],
            ["Ext_Baudrate",         1, "dec"],
            ["Length_smf",           1, "dec"],
            ["Length_e_50u",         1, "dec"],
            ["Length_50u",           1, "dec"],
            ["Length_62_5u",         1, "dec"],
            ["Length_Cu",            1, "dec"],
            ["dev_tech",             1, "hex"],
            ["Vendor_Nme",          16, "str"],
            ["Ext_Transceiver",      1, "hex"],
            ["Vendor_OUI",           3, "hex"],
            ["Vendor_PN",           16, "str"],
            ["vendor_Rev",           2, "hex"],
            ["Wavelength",           2, "hex"],
            ["Wavelength_tolerance", 2, "hex"],
            ["Max_case_temp",        1, "dec"],
            ["CC_base",              1, "dec"],
            ["Options",              4, "hex"],
            ["Serial_No",           16, "str"],
            ["Date_Code",            8, "str"],
            ["Diag_Mon_Type",        1, "hex"],
            ["Enhanced_Option",      1, "hex"],
            ["reserve",              1, "hex"],
            ["CC_ext",               1, "dec"],
            ["Vendor_Specific",     32, "str"]            
        ]
    }

class EEPRom:

    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"

    I2C_BUS_CPU_EEPROM = 0

    I2C_ADDR_MUX_9546 = 0x76
    I2C_ADDR_QSFP_MUX_9546 = 0x70
    I2C_ADDR_SFP_MUX_9548_1 = 0x71
    I2C_ADDR_SFP_MUX_9548_2 = 0x72
    I2C_ADDR_SFP_MUX_9548_3 = 0x73
    I2C_ADDR_SFP_MUX_9548_4 = 0x74

    I2C_ADDR_EEPROM_Alpha_CPU  = 0x51
    I2C_ADDR_EEPROM_Beta_CPU  = 0x57
    I2C_ADDR_EEPROM_SFP_A0  = 0x50
    I2C_ADDR_EEPROM_SFP_A2  = 0x51
    I2C_ADDR_EEPROM_QSFP_A0 = 0x50
    I2C_ADDR_EEPROM_QSFP_A2 = 0x51

    CPU_EEPROM_SIZE = 256
    CPU_EEPROM_PAGE_SIZE = 0x10
    CPU_EEPROM_PAGE_MASK = CPU_EEPROM_PAGE_SIZE - 1
    
    SFP_QSFP_CHANEL = 0x08
    SFP_EEPROM_SIZE = 256
    SFP_EEPROM_PAGE_SIZE = 0x10
    SFP_EEPROM_PAGE_MASK = SFP_EEPROM_PAGE_SIZE - 1
    QSFP_EEPROM_SIZE = 256
    QSFP_EEPROM_PAGE_SIZE = 0x10
    QSFP_EEPROM_PAGE_MASK = SFP_EEPROM_PAGE_SIZE - 1

    QSFP_EEPROM_TX_DISABLE = 0x56
    QSFP_EEPROM_TX_DISABLE_MASK = 0x0F
    QSFP_EEPROM_TX_ENABLE_MASK = 0x00
    QSFP_EEPROM_PAGE_SELECT = 0x7F
    QSFP_EEPROM_UPPER_PAGE_00 = 0x0
    QSFP_EEPROM_UPPER_PAGE_01 = 0x1
    QSFP_EEPROM_UPPER_PAGE_02 = 0x2
    QSFP_EEPROM_UPPER_PAGE_03 = 0x3
    QSFP_EEPROM_LOWER_PAGE_SIZE = 128

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.i2c_mux = I2CMux().MUXs
        self.ioexp = IOExpander()
        self.cpld = CPLD()
        
    def set_tx_laser(self, port_num, enable, sub_port=None):
        i2c_address = self.I2C_ADDR_EEPROM_SFP_A0
        mask = 0

        bus = self.get_qsfp_bus(port_num)

        try:
            if sub_port == None:
                if enable:
                    mask = self.QSFP_EEPROM_TX_ENABLE_MASK
                else:
                    mask = self.QSFP_EEPROM_TX_DISABLE_MASK
            else:
                mask = bus.read_byte_data(i2c_address,
                                          self.QSFP_EEPROM_TX_DISABLE)
                if enable:
                    mask &= ~(1 << sub_port)
                else:
                    mask |= (1 << sub_port)

            bus.write_byte_data(i2c_address, self.QSFP_EEPROM_TX_DISABLE, mask)
        finally:
            bus.close()

    def _data_transfer(self, _len, _type, _data):
        
        output = ""
        if _type == "str":
            for i in range(_len):
                output = output + chr(_data[i])
        elif _type == "hex":
            output = "0x"
            for i in range(_len):
                output = output + hex(_data[i])[2:]
        else:
            for i in range(_len):
                output = output + str(_data[i])

        return output

    def _get_sfp_mux_channel(self, port_num):
        # Normal channel conversion
        return port_num % 8
        
    def _get_qsfp_mux_channel(self, port_num):
        ch = port_num % 8
        # Customize channel
        if ch == 0:
            chanl = 3
        elif ch == 1:
            chanl = 2
        else:
            chanl = 0

        return chanl
            
    def _get_sfp_mux(self, port_num):
        port_grp = int(port_num / 8)

        if port_grp == 0:      # P0~P7
            mux = "9548_SFP1"
        elif port_grp == 1:    # P8~P15
            mux = "9548_SFP2"
        elif port_grp == 2:    # P16~P23
            mux = "9548_SFP3"
        else:                  # P24~P27
            mux = "9548_SFP4"

        return mux

    def init(self):
        pass

    def _get_sfp_qsfp_bus(self, mux, channel):
        if self.i2c_mux[mux].ch_bus != None:
            bus_num = self.i2c_mux[mux].ch_bus[channel]
            return SMBus(bus_num)
        else:
            bus = SMBus(0)
            bus.write_byte_data(self.I2C_ADDR_MUX_9546, 0x0, self.SFP_QSFP_CHANEL)
            if mux == "9548_SFP1":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_1
            elif mux == "9548_SFP2":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_2
            elif mux == "9548_SFP3":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_3
            elif mux == "9548_SFP4":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_4
            else: # "9546_QSFP"
                mux_addr = self.I2C_ADDR_QSFP_MUX_9546
            bus.write_byte_data(mux_addr, 0x0, 1 << channel)
            return bus

    def _close_sfp_qsfp_bus(self, bus, mux):
        if self.i2c_mux[mux].ch_bus is None:
            if mux == "9548_SFP1":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_1
            elif mux == "9548_SFP2":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_2
            elif mux == "9548_SFP3":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_3
            elif mux == "9548_SFP4":
                mux_addr = self.I2C_ADDR_SFP_MUX_9548_4
            else: # "9546_QSFP"
                mux_addr = self.I2C_ADDR_QSFP_MUX_9546
            bus.write_byte_data(mux_addr, 0x0, 0x0)
            bus.write_byte_data(self.I2C_ADDR_MUX_9546, 0x0, 0x0)
        bus.close()

    def get_sfp_bus(self, port_num):
        mux = self._get_sfp_mux(port_num)
        mux_chanl = self._get_sfp_mux_channel(port_num)

        return self._get_sfp_qsfp_bus(mux, mux_chanl)

    def close_sfp_bus(self, port_num, bus):
        mux = self._get_sfp_mux(port_num)

        self._close_sfp_qsfp_bus(bus, mux)

    def get_qsfp_bus(self, port_num):
        mux = "9546_QSFP"
        mux_chanl = self._get_qsfp_mux_channel(port_num)

        return self._get_sfp_qsfp_bus(mux, mux_chanl)

    def close_qsfp_bus(self, port_num, bus):
        mux = "9546_QSFP"

        self._close_sfp_qsfp_bus(bus, mux)

    def dump_cpu_eeprom(self):
        bus = None
        try:
            # Get the bus number of sysfs
            bus_num = self.I2C_BUS_CPU_EEPROM
            bus = SMBus(bus_num)

            offset = 0
            data = []
            while offset < self.CPU_EEPROM_SIZE:
                blk_off = offset & self.CPU_EEPROM_PAGE_MASK
                _len = self.CPU_EEPROM_SIZE - offset
                maxlen = self.CPU_EEPROM_PAGE_SIZE - (blk_off & self.CPU_EEPROM_PAGE_MASK)
                if _len > maxlen:
                    _len = maxlen

                # Send device select code
                # Proto and Alpha doesn't have parent MUX
                hw_rev = self.cpld.get_hw_rev()
                if hw_rev == self.cpld.HARDWARE_REV_PROTO_STR:
                    eeprom_addr = self.I2C_ADDR_EEPROM_Alpha_CPU 
                elif hw_rev == self.cpld.HARDWARE_REV_ALPHA_STR:
                    eeprom_addr = self.I2C_ADDR_EEPROM_Alpha_CPU 
                else:
                    eeprom_addr = self.I2C_ADDR_EEPROM_Beta_CPU
                    
                bus.write_byte_data(eeprom_addr, (offset>>8)&0xff, offset&0xff)
                for i in range(_len):
                    res = bus.read_byte(eeprom_addr)
                    data.append(res)

                offset = offset + _len

            return data
        except Exception as e:
            self.logger.error("Dump CPU EEPROM fail, error: " + str(e))
            raise
        finally:
            if bus != None:
                bus.close()

    def dump_sfp_eeprom(self, port_num, page = None):
        bus = None
        try:
            if page == None or page == "A0":
                i2c_address = self.I2C_ADDR_EEPROM_SFP_A0
            elif page == "A2":
                i2c_address = self.I2C_ADDR_EEPROM_SFP_A2
            
            bus = self.get_sfp_bus(port_num)

            offset = 0
            data = []
            
            while offset < self.SFP_EEPROM_SIZE:
                blk_off = offset & self.SFP_EEPROM_PAGE_MASK
                _len = self.SFP_EEPROM_SIZE - offset

                new_data = bus.read_i2c_block_data(i2c_address, offset, _len)
                data.extend(new_data[:_len] if _len < len(new_data) else new_data)

                offset += len(new_data)

            data_base = 0
            content = {}
            for j in range(len(DATA_INFO.SFP["list"])):
                
                data_str = []
                data_len = DATA_INFO.SFP["list"][j][1]
                data_type = DATA_INFO.SFP["list"][j][2]
                for k in range(data_len):
                    data_str.append(data[data_base+k])
                
                if ("reserve" not in DATA_INFO.SFP["list"][j][0]) and \
                   ("Vendor_Specific" not in DATA_INFO.SFP["list"][j][0]):
                   content.update({DATA_INFO.SFP["list"][j][0]: self._data_transfer(data_len, data_type, data_str)})
            
                data_base = data_base + data_len     

            return data
        except Exception as e:
            self.logger.error("Dump SFP port(" + str(port_num) + ") EEPROM fail, error: " + str(e))
            ### Error handle
            # Check if we also can't access other i2c devices
            i2c = I2C(0)
            i2c_status = i2c.check_status()
            if i2c_status == False:
                self.logger.error("SFP Port "+ str(port_num) + " might have transceiver issue, please check it")
            else:
                self.logger.error("Dump SFP port fail, but I2C bus is not busy")

            #Try to reset i2c mux
            cpld = CPLD()
            cpld.mux_reset_by_sfp_port(port_num)

            #Check i2c bus is normal or not
            recheck_count = 0
            while i2c_status == False and recheck_count < 3:
                i2c_status = i2c.check_status()
                recheck_count = recheck_count + 1
                sleep(0.01)

            if i2c_status == False:
                self.logger.error("I2C bus is still busy")
            else:
                self.logger.warning("I2C bus is normal")
            raise
        finally:         
            if bus != None:
                self.close_sfp_bus(port_num, bus)

    def dump_qsfp_eeprom(self, port_num, page = None):
        bus = None
        try:
            i2c_address = self.I2C_ADDR_EEPROM_QSFP_A0
            bus = self.get_qsfp_bus(port_num)

            offset = 0
            data = []
            
            # Write page selection to page select byte
            if page == 0:
                bus.write_byte_data(i2c_address, self.QSFP_EEPROM_PAGE_SELECT, self.QSFP_EEPROM_UPPER_PAGE_00)
            elif page == 1:
                bus.write_byte_data(i2c_address, self.QSFP_EEPROM_PAGE_SELECT, self.QSFP_EEPROM_UPPER_PAGE_01)
                offset = self.QSFP_EEPROM_LOWER_PAGE_SIZE
            elif page == 2:
                bus.write_byte_data(i2c_address, self.QSFP_EEPROM_PAGE_SELECT, self.QSFP_EEPROM_UPPER_PAGE_02)
                offset = self.QSFP_EEPROM_LOWER_PAGE_SIZE
            elif page == 3:
                bus.write_byte_data(i2c_address, self.QSFP_EEPROM_PAGE_SELECT, self.QSFP_EEPROM_UPPER_PAGE_03)
                offset = self.QSFP_EEPROM_LOWER_PAGE_SIZE

            while offset < self.QSFP_EEPROM_SIZE:
                blk_off = offset & self.QSFP_EEPROM_PAGE_MASK
                _len = self.QSFP_EEPROM_SIZE - offset

                new_data = bus.read_i2c_block_data(i2c_address, offset)
                data.extend(new_data[:_len] if _len < len(new_data) else new_data)

                offset += len(new_data)

            return data
        except Exception as e:
            self.logger.error("Dump QSFP port(" + str(port_num) + ") EEPROM fail, error: " + str(e))

            ### Error handle
            # Check if we also can't access other i2c devices
            i2c = I2C(0)
            i2c_status = i2c.check_status()
            if i2c_status == False:
                self.logger.error("QSFP Port "+ str(port_num) + " might have transceiver issue, please check it")
            else:
                self.logger.error("Dump QSFP port fail, but I2C bus is not busy")

            #Try to reset i2c mux
            cpld = CPLD()
            cpld.mux_reset_by_qsfp_port(port_num)
            
            #Check i2c bus is normal or not
            recheck_count = 0
            while i2c_status == False and recheck_count < 3:
                i2c_status = i2c.check_status()
                recheck_count = recheck_count + 1
                sleep(0.01)

            if i2c_status == False:
                self.logger.error("I2C bus is still busy")
            else:
                self.logger.warning("I2C bus is normal")
            raise
        finally:
            if bus != None:
                self.close_qsfp_bus(port_num, bus)
