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
import importlib
from time import sleep

from common.logger import Logger
from const.const import Led
from const.const import CPLDConst
from cpld.cpld_reg import CPLDCPUReg
from protocol.lpc import LPC
from protocol.lpc import LPCDevType
from smbus import SMBus
from i2c_mux.i2c_mux import I2CMux

class PCA9535_CMD:
    
    PCA9535_REG_PORT0_IN = 0
    PCA9535_REG_PORT1_IN = 1
    PCA9535_REG_PORT0_OUT = 2
    PCA9535_REG_PORT1_OUT = 3
    PCA9535_REG_PORT0_POL_INVER = 4
    PCA9535_REG_PORT1_POL_INVER = 5
    PCA9535_REG_PORT0_CONF = 6
    PCA9535_REG_PORT1_CONF = 7

class CPLD:

    MODEL_ID_EXTEND_BOARD_ID = 0b1110
    # Proto, Alpha
    MODEL_ID_SIAD_30P = 0b0110
    MODEL_ID_SIAD_30P_STR = "SIAD_TELCO_SWITCH_28+2P"
    # Beta
    MODEL_ID_SIAD_34P = 0b0000
    MODEL_ID_SIAD_34P_STR = "SIAD_TELCO_SWITCH_28+2P"
    MODEL_ID_SIAD_32P = 0b0001
    MODEL_ID_SIAD_32P_STR = "SIAD_TELCO_SWITCH_28+2P"

    HARDWARE_REV_PROTO = 0b00
    HARDWARE_REV_ALPHA = 0b10
    HARDWARE_REV_BETA  = 0b01
    HARDWARE_REV_PVT   = 0b11

    HARDWARE_REV_PROTO_STR = "Proto"
    HARDWARE_REV_ALPHA_STR = "Alpha"
    HARDWARE_REV_BETA_STR  = "Beta"
    HARDWARE_REV_PVT_STR   = "PVT"

    BUILD_REV_A1 = 0b00
    BUILD_REV_A2 = 0b10
    BUILD_REV_A3 = 0b01
    BUILD_REV_A4 = 0b11

    BUILD_REV_A1_STR = "A1"
    BUILD_REV_A2_STR = "A2"
    BUILD_REV_A3_STR = "A3"
    BUILD_REV_A4_STR = "A4"

    I2C_ADDR_9546_ROOT = 0x75
    I2C_ADDR_BRD_ID_CHAL = 2
    I2C_ADDR_BRD_ID = 0x20
    
    InterruptMaskConst = {
        "Global_Mask": {
            "name": "Global_Mask", "bit": 0, "default": 0 },
        "Fan_Mask": {
            "name": "Fan_Mask", "bit": 1, "default": 0 },
        "NMI_Mask": {
            "name": "NMI_Mask", "bit": 2, "default": 0 },
        "MACPHY_Mask": {
            "name": "MACPHY_Mask", "bit": 3, "default": 0 },
        "SyncE_PTP_Mask": {
            "name": "SyncE_PTP_Mask", "bit": 4, "default": 0 },
        "Port_Mask": {
            "name": "Port_Mask", "bit": 5, "default": 0 },
        "Miscel_Mask": {
            "name": "Miscel_Mask", "bit": 6, "default": 0 }, 
        "Reserve": {
            "name": "Reserve", "bit": 7, "default": 0 },   
    }
    
    BMCResetMaskConst = {
        "SYS": {
            "name": "SYS", "bit": 0, "default": 1 },
        "DDR3": {
            "name": "DDR3", "bit": 2, "default": 1 },
    }
    
    MUXResetMaskConst = {
        "RST_I2C_MUX1": {
            "name": "RST_I2C_MUX1", "bit": 0, "default": 1 },
        "RST_I2C_MUX2": {
            "name": "RST_I2C_MUX2", "bit": 1, "default": 1 },
        "RST_I2C_MUX3": {
            "name": "RST_I2C_MUX3", "bit": 2, "default": 1 },
        "RST_I2C_MUX4": {
            "name": "RST_I2C_MUX4", "bit": 3, "default": 1 },
        "RST_I2C_MUX5": {
            "name": "RST_I2C_MUX5", "bit": 4, "default": 1 },
        "RST_I2C_MUX6": {
            "name": "RST_I2C_MUX6", "bit": 5, "default": 1 },
        "RST_I2C_MUX7": {
            "name": "RST_I2C_MUX7", "bit": 6, "default": 1 },
        "RST_I2C_MUX8": {
            "name": "RST_I2C_MUX8", "bit": 7, "default": 1 },
    }
    
    PowerCtrlMaskConst = {
        "PWR_OFF_MAC": {
            "name": "PWR_OFF_MAC", "bit": 0, "default": 0 },
        "Reserve": {
            "name": "Reserve", "bit": 1, "default": 0 },
        "Reserve": {
            "name": "Reserve", "bit": 2, "default": 0 },
        "USB_PWR_EN": {
            "name": "USB_PWR_EN", "bit": 3, "default": 1 },
        "BMC_HEATER_PW": {
            "name": "BMC_HEATER_PW", "bit": 4, "default": 1 },
        "Reserve": {
            "name": "Reserve", "bit": 5, "default": 1 },
        "Reserve": {
            "name": "Reserve", "bit": 6, "default": 1 },
        "Reserve": {
            "name": "Reserve", "bit": 7, "default": 1 },
    }
    
    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.lpc = LPC()
        self.i2c_mux = I2CMux().MUXs
        # Get hardware version
        board_id = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD, 0x00)
        hw_rev = (board_id & 0b00001100) >> 2
        if hw_rev < self.HARDWARE_REV_BETA:
            module = importlib.import_module('cpld.cpld_reg')
            my_class = getattr(module, 'CPLDMBRegProto')
            self.CPLDMBReg = my_class()
        else:
            module = importlib.import_module('cpld.cpld_reg')
            my_class = getattr(module, 'CPLDMBReg')
            self.CPLDMBReg = my_class()
            my_class = getattr(module, 'SMBUSMEMReg')
            self.SMBUSMEMReg = my_class()

    def init(self):
        muxs = ["RST_I2C_MUX3","RST_I2C_MUX4","RST_I2C_MUX5","RST_I2C_MUX6","RST_I2C_MUX7","RST_I2C_MUX2"]

        for mux in muxs:
            self.mux_reset_set(mux)
            sleep(0.000005)
            self.mux_reset_unset(mux)
            sleep(0.000005)
            self.logger.info("Reset MUX: "+mux)

    def deinit(self):
        pass

    def get_channel_bus(self, channel):
        if self.i2c_mux["9546_ROOT1"].ch_bus != None:
            bus_num = self.i2c_mux["9546_ROOT1"].ch_bus[channel]
            return SMBus(bus_num)
        else:
            bus = SMBus(0)
            bus.write_byte_data(self.I2C_ADDR_9546_ROOT, 0x0, 1 << channel)
            return bus

    def close_channel_bus(self, bus):
        if self.i2c_mux["9546_ROOT1"].ch_bus is None:
            bus.write_byte_data(self.I2C_ADDR_9546_ROOT, 0x0, 0x0)
        bus.close()

    ########## FOR CPLD UTILITY ##########
    def check_hw_rev_mux(self):
        try:
            bus = self.get_channel_bus(0)
            self.close_channel_bus(bus)
            
            return "EXIST"
        except Exception as e:
            self.logger.error("Get MUX fail (it's alpha board), error: " + str(e))
            return "NOT_EXIST"   
                
    def get_brd_id_info(self):
        bus = self.get_channel_bus(self.I2C_ADDR_BRD_ID_CHAL)
        try:
            brd_info = bus.read_byte_data(self.I2C_ADDR_BRD_ID, PCA9535_CMD.PCA9535_REG_PORT1_IN)
            
            return brd_info
        finally:
            if bus != None:
                self.close_channel_bus(bus)
        
    def get_board_id(self):
        try:
            hw_rev_mux = self.check_hw_rev_mux()
            if hw_rev_mux == "NOT_EXIST":
                board_id = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_BOARD_ID)
            elif hw_rev_mux == "EXIST":
                board_id = self.get_brd_id_info()
            else:
                raise ValueError("This HW rev is not supported")

            build_rev = board_id & 0b00000011
            hw_rev = (board_id & 0b00001100) >> 2
            model_id = (board_id & 0b11110000) >> 4

            if model_id == self.MODEL_ID_EXTEND_BOARD_ID:
                extend_board_id = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                                  self.CPLDMBReg.REG_BOARD_EXTEND_BOARD_ID)
                model_id = extend_board_id & 0b00001111

            if model_id == self.MODEL_ID_SIAD_30P:
                id = self.MODEL_ID_SIAD_30P_STR
            elif model_id == self.MODEL_ID_SIAD_34P:
                id = self.MODEL_ID_SIAD_34P_STR
            elif model_id == self.MODEL_ID_SIAD_32P:
                id = self.MODEL_ID_SIAD_32P_STR
            else:
                id = "unknown"

            return id
        except Exception as e:
            self.logger.error("Get board id fail, error: " + str(e))
            raise

    def get_hw_rev(self):
        try:
            hw_rev_mux = self.check_hw_rev_mux()
            if hw_rev_mux == "NOT_EXIST":
                board_id = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_BOARD_ID)
            elif hw_rev_mux == "EXIST":
                board_id = self.get_brd_id_info()
            else:
                raise ValueError("This HW rev is not supported")

            hw_rev = (board_id & 0b00001100) >> 2

            if hw_rev == self.HARDWARE_REV_PROTO:
                rev = self.HARDWARE_REV_PROTO_STR
            elif hw_rev == self.HARDWARE_REV_ALPHA:
                rev = self.HARDWARE_REV_ALPHA_STR
            elif hw_rev == self.HARDWARE_REV_BETA:
                rev = self.HARDWARE_REV_BETA_STR
            elif hw_rev == self.HARDWARE_REV_PVT:
                rev = self.HARDWARE_REV_PVT_STR
            else:
                rev = "unknown"

            return rev
        except Exception as e:
            self.logger.error("Get hardware revision fail, error: " + str(e))
            raise

    def get_build_rev(self):
        try:
            hw_rev_mux = self.check_hw_rev_mux()
            if hw_rev_mux == "NOT_EXIST":
                board_id = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_BOARD_ID)
            elif hw_rev_mux == "EXIST":
                board_id = self.get_brd_id_info()
            else:
                raise ValueError("This HW rev is not supported")

            build_rev = board_id & 0b00000011

            if build_rev == self.BUILD_REV_A1:
                rev = self.BUILD_REV_A1_STR
            elif build_rev == self.BUILD_REV_A2:
                rev = self.BUILD_REV_A2_STR
            elif build_rev == self.BUILD_REV_A3:
                rev = self.BUILD_REV_A3_STR
            elif build_rev == self.BUILD_REV_A4:
                rev = self.BUILD_REV_A4_STR
            else:
                rev = "unknown"

            return rev
        except Exception as e:
            self.logger.error("Get build revision fail, error: " + str(e))
            raise

    def get_cpu_board_cpld_revision(self):
        try:
            cpld_ver = self.lpc.regGet(LPCDevType.CPLD_ON_CPU_BOARD,
                                       CPLDCPUReg.REG_CPLD_REVISION)
            return cpld_ver
        except Exception as e:
            self.logger.error("Get CPU board CPLD revision fail, error: " + str(e))
            raise

    def get_main_board_code_version(self):
        try:
            cpld_ver = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_CODE_VERSION)
            return cpld_ver
        except Exception as e:
            self.logger.error("Get main board CPLD revision fail, error: " + str(e))
            raise

    def set_uart_source(self, source):
        try:
            multi_intf_sel = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                             self.CPLDMBReg.REG_MULTI_INTF_SEL)

            if source == CPLDConst.UART_SOURCE_CPU:
                multi_intf_sel &= ~0b00000010
            else:
                multi_intf_sel |= 0b00000010

            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                            self.CPLDMBReg.REG_MULTI_INTF_SEL, multi_intf_sel)
        except Exception as e:
            if source == CPLDConst.UART_SOURCE_CPU:
                self.logger.error("Set UART source to CPU fail, error: " + str(e))
            else:
                self.logger.error("Set UART source to BMC fail, error: " + str(e))
            raise

    def get_uart_source(self):
        try:
            multi_intf_sel = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                             self.CPLDMBReg.REG_MULTI_INTF_SEL)

            uart_source = (multi_intf_sel & 0b00000010) >> 1

            return uart_source
        except Exception as e:
            self.logger.error("Get UART source fail, error: " + str(e))
            raise

    def mask_timing_interrupt(self):
        try:
            intr_mask = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                        self.CPLDMBReg.REG_INTR_MASK)
            intr_mask = intr_mask | 0b00010000
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                        self.CPLDMBReg.REG_INTR_MASK, intr_mask)
        except Exception as e:
            self.logger.error("Mask timing interrupt fail, error: " + str(e))
            raise

    ########## FOR LED ##########
    def _set_led_status_color(self, target, status, color):
        try:
            if target == Led.SYSTEM:
                sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                          self.CPLDMBReg.REG_SYS_LED1)

                if status == Led.STATUS_OFF:
                    sys_led &= ~0b01000000
                else:
                    sys_led |= 0b01000000

                if color == Led.COLOR_YELLOW:
                    sys_led &= ~0b10000000
                else:
                    sys_led |= 0b10000000

                self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                self.CPLDMBReg.REG_SYS_LED1, sys_led)
            elif target == Led.GPS:
                sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                          self.CPLDMBReg.REG_SYS_LED1)

                if status == Led.STATUS_OFF:
                    sys_led &= ~0b00000100
                else:
                    sys_led |= 0b00000100

                if color == Led.COLOR_YELLOW:
                    sys_led &= ~0b00001000
                else:
                    sys_led |= 0b00001000

                self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                self.CPLDMBReg.REG_SYS_LED1, sys_led)
            elif target == Led.SYNC:
                sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                          self.CPLDMBReg.REG_SYS_LED1)

                if status == Led.STATUS_OFF:
                    sys_led &= ~0b00000001
                else:
                    sys_led |= 0b00000001

                if color == Led.COLOR_YELLOW:
                    sys_led &= ~0b00000010
                else:
                    sys_led |= 0b00000010

                self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                self.CPLDMBReg.REG_SYS_LED1, sys_led)
            else:
                raise ValueError("This LED type is not supported")
        except Exception as e:
            self.logger.error("Set LED status/color fail, error: " + str(e))
            raise

    def _set_led_blink_status(self, target, blink_status):
        try:
            system_led_blinking = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                                  self.CPLDMBReg.REG_SYS_LED_BLINKING)

            if target == Led.SYSTEM:
                if blink_status == Led.BLINK_STATUS_SOLID:
                    system_led_blinking &= ~0b00001000
                else:
                    system_led_blinking |= 0b00001000
            elif target == Led.GPS:
                if blink_status == Led.BLINK_STATUS_SOLID:
                    system_led_blinking &= ~0b00000010
                else:
                    system_led_blinking |= 0b00000010
            elif target == Led.SYNC:
                if blink_status == Led.BLINK_STATUS_SOLID:
                    system_led_blinking &= ~0b00000001
                else:
                    system_led_blinking |= 0b00000001
            else:
                raise ValueError("This LED type is not supported")

            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                            self.CPLDMBReg.REG_SYS_LED_BLINKING, system_led_blinking)
        except Exception as e:
            self.logger.error("Set LED blink status fail, error: " + str(e))
            raise

    def set_led(self, target, status, color, blink_status):
        try:
            self._set_led_status_color(target, status, color)
            self._set_led_blink_status(target, blink_status)
        except Exception as e:
            self.logger.error("Set LED fail, error: " + str(e))
            raise

    def _get_system_led_status(self):
        try:
            status = {}

            sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_SYS_LED1)
            system_led_blinking = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                                  self.CPLDMBReg.REG_SYS_LED_BLINKING)

            status["status"] = (sys_led & 0b01000000) >> 6
            status["color"] = (sys_led & 0b10000000) >> 7
            status["blink_status"] = (system_led_blinking & 0b00001000) >> 3

            return status
        except Exception as e:
            self.logger.error("Get LED(SYSTEM) status fail, error: " + str(e))
            raise

    def _get_power_led_status(self):
        try:
            status = {}

            sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_SYS_LED2)
            system_led_blinking = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                                  self.CPLDMBReg.REG_SYS_LED_BLINKING)

            status["status"] = (sys_led & 0b00000001)
            status["color"] = (sys_led & 0b00000010) >> 1
            status["blink_status"] = (system_led_blinking & 0b00010000) >> 4

            return status
        except Exception as e:
            self.logger.error("Get LED(POWER) status fail, error: " + str(e))
            raise

    def _get_fans_led_status(self):
        try:
            status = {}

            sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_SYS_LED1)
            system_led_blinking = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                                  self.CPLDMBReg.REG_SYS_LED_BLINKING)

            status["status"] = (sys_led & 0b00010000) >> 4
            status["color"] = (sys_led & 0b00100000) >> 5
            status["blink_status"] = (system_led_blinking & 0b00000100) >> 2

            return status
        except Exception as e:
            self.logger.error("Get FAN LEDs status fail, error: " + e)
            raise

    def _get_gps_led_status(self):
        try:
            status = {}

            sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_SYS_LED1)
            system_led_blinking = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                                  self.CPLDMBReg.REG_SYS_LED_BLINKING)

            status["status"] = (sys_led & 0b00000100) >> 2
            status["color"] = (sys_led & 0b00001000) >> 3
            status["blink_status"] = (system_led_blinking & 0b00000010) >> 1

            return status
        except Exception as e:
            self.logger.error("Get LED(GPS) status fail, error: " + str(e))
            raise

    def _get_sync_led_status(self):
        try:
            status = {}

            sys_led = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_SYS_LED1)
            system_led_blinking = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                                  self.CPLDMBReg.REG_SYS_LED_BLINKING)

            status["status"] = (sys_led & 0b00000001)
            status["color"] = (sys_led & 0b00000010) >> 1
            status["blink_status"] = (system_led_blinking & 0b00000001)

            return status
        except Exception as e:
            self.logger.error("Get LED(SYNC) status fail, error: " + str(e))
            raise

    def get_led_status(self, target):
        try:
            if target == Led.SYSTEM:
                status = self._get_system_led_status()
            elif target == Led.POWER:
                status = self._get_power_led_status()
            elif target == Led.FAN:
                status = self._get_fans_led_status()
            elif target == Led.GPS:
                status = self._get_gps_led_status()
            elif target == Led.SYNC:
                status = self._get_sync_led_status()
            else:
                raise ValueError("This LED type is not supported")

            return status
        except Exception as e:
            raise

    ########## FOR INTERRUPT UTILITY ##########
    def get_nmi_interrupt(self):
        try:
            interrupts = {}

            pwr_sts = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_POWER_STATUS)
            interrupts["PSU1_PRSNT"] = (pwr_sts & 0b01000000) >> 6
            interrupts["PSU2_PRSNT"] = (pwr_sts & 0b10000000) >> 7

            fan_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_FAN_INTR)
            interrupts["INT_FAN1"] = (fan_int & 0b00000001)
            interrupts["INT_FAN2"] = (fan_int & 0b00000010) >> 1
            interrupts["INT_FAN3"] = (fan_int & 0b00000100) >> 2
            interrupts["INT_FAN4"] = (fan_int & 0b00001000) >> 3
            interrupts["INT_FAN5"] = (fan_int & 0b00010000) >> 4

            nmi_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_NMI_INTR)
            interrupts["INT_FAN_CARD"] = (nmi_int & 0b00000001)
            interrupts["INT_HWM_NMI"]  = (nmi_int & 0b00000010) >> 1
            interrupts["INT_PSU1"]     = (nmi_int & 0b00000100) >> 2
            interrupts["INT_PSU2"]     = (nmi_int & 0b00001000) >> 3

            misc_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_MISC_INTR)
            interrupts['INT_TSEN_NMI'] = (misc_int & 0b00000010) >> 1

            access_bmc_heater_flag = 0
            hw_rev = self.get_hw_rev()
            build_rev = self.get_build_rev()
            if hw_rev == self.HARDWARE_REV_ALPHA_STR:
                access_bmc_heater_flag = 0
            elif hw_rev == self.HARDWARE_REV_BETA_STR:
                if build_rev == self.BUILD_REV_A1_STR:
                    access_bmc_heater_flag = 0
                elif build_rev == self.BUILD_REV_A2_STR:
                    access_bmc_heater_flag = 0
                else:
                    access_bmc_heater_flag = 1
            else:
                access_bmc_heater_flag = 1
                
            if access_bmc_heater_flag == 1:
                interrupts["BMC_HEATER_INTR"] = (nmi_int & 0b00010000) >> 4

            return interrupts
        except Exception as e:
            raise

    def get_ethernet_mac_phy_status_interrupt(self):
        try:
            interrupts = {}

            mac_phy_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                          self.CPLDMBReg.REG_MAC_PHY_INTR)
            interrupts["INT_MAC"]  = (mac_phy_int & 0b00000001)
            interrupts["INT_PHY1"] = (mac_phy_int & 0b00000010) >> 1
            interrupts["INT_PHY3"] = (mac_phy_int & 0b00000100) >> 2

            pll_lock = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_PLL_LOCK)
            interrupts["MAC_COREPLL_LOCK"] = (pll_lock & 0b00010000) >> 4
            interrupts["MAC_MCUPLL_LOCK"] = (pll_lock & 0b00100000) >> 5

            return interrupts
        except Exception as e:
            raise

    def get_synce_ptp_status_interrupt(self):
        try:
            interrupts = {}

            pll_lock = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_PLL_LOCK)
            interrupts["SMU_DPLL1_LOCK"] = (pll_lock & 0b00000001)
            interrupts["SMU_DPLL2_LOCK"] = (pll_lock & 0b00000010) >> 1
            interrupts["SMU_DPLL3_LOCK"] = (pll_lock & 0b00000100) >> 2

            smu_input_lost = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                             self.CPLDMBReg.REG_SMU_INPUT_LOST)
            interrupts["SMU_INPUT1_LOS"] = (smu_input_lost & 0b00000010) >> 1

            synce_ptp_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                            self.CPLDMBReg.REG_SYNCE_PTP_INTR)
            interrupts["INT_CJA_INTR"] = (synce_ptp_int & 0b00000001)
            interrupts["INT_CJA_LOL"]  = (synce_ptp_int & 0b00000010) >> 1
            interrupts["INT1_GNSS"]    = (synce_ptp_int & 0b00001000) >> 3
            interrupts["INT_BITS"]     = (synce_ptp_int & 0b00010000) >> 4

            misc_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_MISC_INTR)
            interrupts["INT_SMU"]        = (misc_int & 0b00001000) >> 3

            return interrupts
        except Exception as e:
            raise

    def get_port_status_interrupt(self):
        try:
            interrupts = {}

            port_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_PORT_INTR)
            interrupts["INT_SFP_FLT_N0"] = (port_int & 0b00000001)
            interrupts["INT_SFP_FLT_N1"] = (port_int & 0b00000010) >> 1
            interrupts["INT_SFP_LOS_N0"] = (port_int & 0b00000100) >> 2
            interrupts["INT_SFP_LOS_N1"] = (port_int & 0b00001000) >> 3
            interrupts["INT_SFP_ABS_N0"] = (port_int & 0b00010000) >> 4
            interrupts["INT_SFP_ABS_N1"] = (port_int & 0b00100000) >> 5
            interrupts["INT_QSFP28"]     = (port_int & 0b01000000) >> 6

            pwr_oc = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                     self.CPLDMBReg.REG_PORT_OVER_CURRENT)
            interrupts["SFP_PWR_OC_GP1"] = (pwr_oc & 0b00000001)
            interrupts["SFP_PWR_OC_GP2"] = (pwr_oc & 0b00000010) >> 1
            interrupts["SFP_PWR_OC_GP3"] = (pwr_oc & 0b00000100) >> 2
            interrupts["QSFP28_PWR_OC"]  = (pwr_oc & 0b00001000) >> 3
            interrupts["SFP28_PWR_OC"]   = (pwr_oc & 0b00010000) >> 4

            return interrupts
        except Exception as e:
            raise

    def get_cpld_alarm_interrupt(self):
        try:
            interrupts = {}

            nmi_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_NMI_INTR)
            interrupts["INT_HWM_NMI"] = (nmi_int & 0b00000010) >> 1

            pwr_oc = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                     self.CPLDMBReg.REG_PORT_OVER_CURRENT)
            interrupts["USB_PWR_OC"] = (pwr_oc & 0b00100000) >> 5

            misc_int = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                       self.CPLDMBReg.REG_MISC_INTR)
            interrupts['INT_TSEN_ALERT'] = (misc_int & 0b00000001)
            interrupts['INT_TSEN_NMI']   = (misc_int & 0b00000010) >> 1
            interrupts['INT_HWM_ALERT']  = (misc_int & 0b00010000) >> 4

            return interrupts
        except Exception as e:
            raise

    ########## FOR TIMING UTILITY ##########
    def bits_hardware_reset(self, op):
        try:
            misc_reset = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                         self.CPLDMBReg.REG_MISC_RESET)
            if op == 0:
                misc_reset &= ~0b00100000
            else:
                misc_reset |= 0b00100000

            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                            self.CPLDMBReg.REG_MISC_RESET, misc_reset)
        except Exception as e:
            self.logger.error("BITS hardware reset fail, error:" + str(e))
            raise

    def smu_hardware_reset(self, op):
        try:
            misc_reset = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                         self.CPLDMBReg.REG_MISC_RESET)
            if op == 0:
                misc_reset &= ~0b00000100
            else:
                misc_reset |= 0b00000100

            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                            self.CPLDMBReg.REG_MISC_RESET, misc_reset)
        except Exception as e:
            self.logger.error("SMU hardware reset fail, error:" + str(e))
            raise

    def ptp_control_configure_receive(self):
        try:
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                            self.CPLDMBReg.REG_PTP_CONTROL, 0x00)
        except Exception as e:
            self.logger.error("PTP control to configure as receiver fail, error:" + str(e))
            raise

    def host_status_smbus_alert_clear(self):
        try:
            # Clear 0xF000 bit 5
            hst_sts = self.lpc.regGet(LPCDevType.SMBUS_MEM, 0x0)
            hst_sts = hst_sts | 0x20
            self.lpc.regSet(LPCDevType.SMBUS_MEM, 0x0, hst_sts)
        except Exception as e:
            self.logger.error("Host status smbus alert clear fail, error:" + str(e))
            raise        

    def interrupt_mask_enable(self, input_str):
        try:
            for key, value in self.InterruptMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
            
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                        self.CPLDMBReg.REG_INTR_MASK)
            data = data | (1<<bit)
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                        self.CPLDMBReg.REG_INTR_MASK, data)
        except Exception as e:
            self.logger.error("Enable interrupt mask fail, error:" + str(e))
            raise 
     
    def interrupt_mask_disable(self, input_str):
        try:
            for key, value in self.InterruptMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
            
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                        self.CPLDMBReg.REG_INTR_MASK)
            data = data & ~(1<<bit)
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                        self.CPLDMBReg.REG_INTR_MASK, data)
        except Exception as e:
            self.logger.error("Disable interrupt mask fail, error:" + str(e))
            raise 
            
    def interrupt_mask_get(self):
        try:            
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                        self.CPLDMBReg.REG_INTR_MASK)
            
            info = {}
            for key, value in self.InterruptMaskConst.items(): 
                bit = value["bit"]
                name = value["name"]   
                if data & (1<<bit) > 0:
                    info[name] = 1
                else:
                    info[name] = 0
                    
            return info

        except Exception as e:
            self.logger.error("Get interrupt mask fail, error:" + str(e))
            raise             
            
    def bmc_power_get(self):
        try:
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                      self.CPLDMBReg.REG_POWER_STATUS)
            power_st = (data & 0b00000100) >> 2

            return power_st
        except Exception as e:
            self.logger.error("Get BMC power status fail, error: " + str(e))
            raise
            
    def bmc_reset_set(self, input_str):
        try:
            for key, value in self.BMCResetMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
                    
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_BMC_RESET)
            data = data & ~(1<<bit)
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_BMC_RESET, data)
        except Exception as e:
            self.logger.error("Set BMC reset fail, error:" + str(e))
            raise 
            
    def bmc_reset_unset(self, input_str):
        try:
            for key, value in self.BMCResetMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
                    
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_BMC_RESET)
            data = data | (1<<bit)
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_BMC_RESET, data)
        except Exception as e:
            self.logger.error("Unset BMC reset fail, error:" + str(e))
            raise            
           
    def mux_reset_set(self, input_str):
        try:
            for key, value in self.MUXResetMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
                    
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_I2C_IOEXP_RESET)
            data = data & ~(1<<bit)
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_I2C_IOEXP_RESET, data)
        except Exception as e:
            self.logger.error("Set MUX reset fail, error:" + str(e))
            raise

    def mux_reset_unset(self, input_str):
        try:
            for key, value in self.MUXResetMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
                    
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_I2C_IOEXP_RESET)
            data = data | (1<<bit)
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_I2C_IOEXP_RESET, data)
        except Exception as e:
            self.logger.error("Unset MUX reset fail, error:" + str(e))
            raise

    def mux_reset_by_sfp_port(self, port_num):
        try:
            if (port_num >= 0 and port_num <= 7):
                mux = "RST_I2C_MUX3"
            elif (port_num >= 8 and port_num <= 15):
                mux = "RST_I2C_MUX4"
            elif (port_num >= 16 and port_num <= 23):
                mux = "RST_I2C_MUX5"
            elif (port_num >= 24 and port_num <= 27):
                mux = "RST_I2C_MUX6"
            else:
                self.logger.error("Invalid port number: " + str(port_num))
                return

            self.mux_reset_set(mux)
            sleep(0.000005)
            self.mux_reset_unset(mux)
            sleep(0.000005)

            #Also reset parent MUX of this MUX
            mux = "RST_I2C_MUX2"
            
            self.mux_reset_set(mux)
            sleep(0.000005)
            self.mux_reset_unset(mux)
            sleep(0.000005)

            self.logger.warning("Reset parent mux OK for SFP port " + str(port_num))
        except Exception as e:
            self.logger.error("Reset parent mux error for SFP port " + str(port_num))
            raise

    def mux_reset_by_qsfp_port(self, port_num):
        try:
            mux = "RST_I2C_MUX7"

            self.mux_reset_set(mux)
            sleep(0.000005)
            self.mux_reset_unset(mux)
            sleep(0.000005)

            #Also reset parent MUX of this MUX
            mux = "RST_I2C_MUX2"

            self.mux_reset_set(mux)
            sleep(0.000005)
            self.mux_reset_unset(mux)
            sleep(0.000005)

            self.logger.warning("Reset parent mux OK for QSFP port " + str(port_num))
        except Exception as e:
            self.logger.error("Reset parent mux error for QSFP port " + str(port_num))
            raise
         
    def power_ctrl_set(self, input_str):
        try:
            for key, value in self.PowerCtrlMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
                    
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_POWER_CONTROL)
            if input_str == "PWR_OFF_MAC":
                data = data & ~(1<<bit)
            else:
                data = data | (1<<bit)
                
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_POWER_CONTROL, data)
        except Exception as e:
            self.logger.error("Enable power control fail, error:" + str(e))
            raise

    def power_ctrl_unset(self, input_str):
        try:
            for key, value in self.PowerCtrlMaskConst.items():     
                if input_str == key:
                    bit = value["bit"]
                    name = value["name"]
                    default_value = value["default"]
                    break
                    
            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_POWER_CONTROL)

            if input_str == "PWR_OFF_MAC":
                data = data | (1<<bit)
            else:
                data = data & ~(1<<bit)
                
            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                    self.CPLDMBReg.REG_POWER_CONTROL, data)
        except Exception as e:
            self.logger.error("Disable power control fail, error:" + str(e))
            raise 

    def tod_output_set(self, status):
        try:
            if status == 1:
                value = 0b00001111
            elif status == 0:
                value = 0b00000000
            else:
                raise ValueError("Usage error! Please input 1 for Enable, 0 for Disable")

            data = self.lpc.regGet(LPCDevType.CPLD_ON_MAIN_BOARD,
                                   self.CPLDMBReg.REG_PTP_CONTROL)

            data &= 0b11110000
            data |= value

            self.lpc.regSet(LPCDevType.CPLD_ON_MAIN_BOARD,
                            self.CPLDMBReg.REG_PTP_CONTROL, data)
        except Exception as e:
            self.logger.error("TOD output fail, error:" + str(e))
            raise

    def smbus_intr_enable(self):
        try:
                        
            data = self.lpc.regGet(LPCDevType.SMBUS_MEM, self.SMBUSMEMReg.REG_SLAVE_CMD)
            data = data & ~(1<<2)
            self.lpc.regSet(LPCDevType.SMBUS_MEM, self.SMBUSMEMReg.REG_SLAVE_CMD, data)
        except Exception as e:
            self.logger.error("Enable smbus interrupt fail, error:" + str(e))
            raise 
     
    def smbus_intr_disable(self):
        try:
                        
            data = self.lpc.regGet(LPCDevType.SMBUS_MEM, self.SMBUSMEMReg.REG_SLAVE_CMD)
            data = data | (1<<2)
            self.lpc.regSet(LPCDevType.SMBUS_MEM, self.SMBUSMEMReg.REG_SLAVE_CMD, data)
        except Exception as e:
            self.logger.error("Disable smbus interrupt fail, error:" + str(e))
            raise

