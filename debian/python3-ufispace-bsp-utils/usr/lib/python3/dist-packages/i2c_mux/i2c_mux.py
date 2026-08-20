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

from common.logger import Logger

class PCA954x:
    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"

    def __init__(self, name, address, bus_num, bus_of_channel):
        self.name = self.NAME + " " + name
        self.address = address
        self.bus_num = bus_num
        self.potential_ch_bus = bus_of_channel

    @property
    def ch_bus(self):
        # Detect whether the system is using device per mux channel,
        # or otherwise one global i2c device
        if os.path.exists(self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.potential_ch_bus[0])):
            return self.potential_ch_bus
        else:
            return None

class PCA9548(PCA954x):

    NAME = "pca9548"
    CHANNEL_MAX = 8

class PCA9546(PCA954x):

    NAME = "pca9546"
    CHANNEL_MAX = 4

class I2CMux:

    # MUX Addr
    I2C_ADDR_9546_ROOT = 0x76
    I2C_ADDR_9548_SFP1 = 0x71
    I2C_ADDR_9548_SFP2 = 0x72
    I2C_ADDR_9548_SFP3 = 0x73
    I2C_ADDR_9548_SFP4 = 0x74
    I2C_ADDR_9546_QSFP = 0x70
    I2C_ADDR_9546_ROOT1 = 0x75

    NUM_I801_DEVICE = 0
    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()

        # MUX PCA9546 ROOT
        self.NUM_MUX_9546_ROOT = (self.NUM_I801_DEVICE + 1,
                                  self.NUM_I801_DEVICE + 2,
                                  self.NUM_I801_DEVICE + 3,
                                  self.NUM_I801_DEVICE + 4)
        # MUX PCA9548#1 SFP#1
        self.NUM_MUX_9548_SFP1 = (self.NUM_I801_DEVICE + 5,
                                  self.NUM_I801_DEVICE + 6,
                                  self.NUM_I801_DEVICE + 7,
                                  self.NUM_I801_DEVICE + 8,
                                  self.NUM_I801_DEVICE + 9,
                                  self.NUM_I801_DEVICE + 10,
                                  self.NUM_I801_DEVICE + 11,
                                  self.NUM_I801_DEVICE + 12)
        # MUX PCA9548#2 SFP#2
        self.NUM_MUX_9548_SFP2 = (self.NUM_I801_DEVICE + 13,
                                  self.NUM_I801_DEVICE + 14,
                                  self.NUM_I801_DEVICE + 15,
                                  self.NUM_I801_DEVICE + 16,
                                  self.NUM_I801_DEVICE + 17,
                                  self.NUM_I801_DEVICE + 18,
                                  self.NUM_I801_DEVICE + 19,
                                  self.NUM_I801_DEVICE + 20)
        # MUX PCA9548#3 SFP#3
        self.NUM_MUX_9548_SFP3 = (self.NUM_I801_DEVICE + 21,
                                  self.NUM_I801_DEVICE + 22,
                                  self.NUM_I801_DEVICE + 23,
                                  self.NUM_I801_DEVICE + 24,
                                  self.NUM_I801_DEVICE + 25,
                                  self.NUM_I801_DEVICE + 26,
                                  self.NUM_I801_DEVICE + 27,
                                  self.NUM_I801_DEVICE + 28)
        # MUX PCA9548#4 SFP#4
        self.NUM_MUX_9548_SFP4 = (self.NUM_I801_DEVICE + 29,
                                  self.NUM_I801_DEVICE + 30,
                                  self.NUM_I801_DEVICE + 31,
                                  self.NUM_I801_DEVICE + 32,
                                  self.NUM_I801_DEVICE + 33,
                                  self.NUM_I801_DEVICE + 34,
                                  self.NUM_I801_DEVICE + 35,
                                  self.NUM_I801_DEVICE + 36)
        # MUX PCA9546 QSFP
        self.NUM_MUX_9546_QSFP = (self.NUM_I801_DEVICE + 37,
                                  self.NUM_I801_DEVICE + 38,
                                  self.NUM_I801_DEVICE + 39,
                                  self.NUM_I801_DEVICE + 40)

        self.NUM_MUX_9546_ROOT1 = (self.NUM_I801_DEVICE + 41,
                                   self.NUM_I801_DEVICE + 42,
                                   self.NUM_I801_DEVICE + 43,
                                   self.NUM_I801_DEVICE + 44)

        # MUX Alias
        self.I2C_BUS_MUX_ROOT = self.NUM_I801_DEVICE
        self.I2C_BUS_MUX_SFP = self.NUM_MUX_9546_ROOT[3]
        self.I2C_BUS_MUX_QSFP = self.NUM_MUX_9546_ROOT[3]
        self.I2C_BUS_MUX_ROOT1 = self.NUM_I801_DEVICE

        # Sysfs path
        self.PATH_MUX_9546_ROOT_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9546_ROOT[0])
        self.PATH_MUX_9546_ROOT_PARENT = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_MUX_ROOT)
        self.PATH_MUX_9548_SFP_1_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_SFP1[0])
        self.PATH_MUX_9548_SFP_2_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_SFP2[0])
        self.PATH_MUX_9548_SFP_3_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_SFP3[0])
        self.PATH_MUX_9548_SFP_4_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_SFP4[0])
        self.PATH_MUX_9548_SFP_PARENT = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_MUX_SFP)
        self.PATH_MUX_9546_QSFP_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9546_QSFP[0])
        self.PATH_MUX_9546_QSFP_PARENT = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_MUX_QSFP)
        self.PATH_MUX_9546_ROOT1_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9546_ROOT1[0])
        self.PATH_MUX_9546_ROOT1_PARENT = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_MUX_ROOT1)

        self.MUXs = {
            "9546_ROOT": PCA9546("ROOT", self.I2C_ADDR_9546_ROOT, self.I2C_BUS_MUX_ROOT, self.NUM_MUX_9546_ROOT),
            "9548_SFP1": PCA9548("SFP1", self.I2C_ADDR_9548_SFP1, self.I2C_BUS_MUX_SFP, self.NUM_MUX_9548_SFP1),
            "9548_SFP2": PCA9548("SFP2", self.I2C_ADDR_9548_SFP2, self.I2C_BUS_MUX_SFP, self.NUM_MUX_9548_SFP2),
            "9548_SFP3": PCA9548("SFP3", self.I2C_ADDR_9548_SFP3, self.I2C_BUS_MUX_SFP, self.NUM_MUX_9548_SFP3),
            "9548_SFP4": PCA9548("SFP4", self.I2C_ADDR_9548_SFP4, self.I2C_BUS_MUX_SFP, self.NUM_MUX_9548_SFP4),
            "9546_QSFP": PCA9546("QSFP", self.I2C_ADDR_9546_QSFP, self.I2C_BUS_MUX_QSFP, self.NUM_MUX_9546_QSFP),
            "9546_ROOT1": PCA9546("ROOT1", self.I2C_ADDR_9546_ROOT1, self.I2C_BUS_MUX_ROOT1, self.NUM_MUX_9546_ROOT1)
        }

    def _create_sysfs(self, path_ch0, path_parent, i2c_mux):
        try:
            if os.path.exists(path_ch0):
                self.logger.info(i2c_mux.NAME + " is already exist")
            else:
                with open(path_parent + "/new_device", 'w') as f:
                    self.logger.info(i2c_mux.NAME + " " + hex(i2c_mux.address))
                    f.write(i2c_mux.NAME + " " + hex(i2c_mux.address))
                # By default the pca954x driver doesn't deselect the
                # mux at the end of transactions making it unsafe with
                # multiple muxes in the system. Work around that by
                # telling it to deselect after each transaction for
                # each channel, which is defined by the value -2.
                with open(path_ch0 + "/mux_device/idle_state", 'w') as f:
                    f.write("-2")
                self.logger.info("Register " + i2c_mux.name + " in sysfs")
        except Exception as e:
            self.logger.error("Register MUX " + i2c_mux.name + " to sysfs fail, error: ", str(e))
            raise

    def init(self):
        # MUX 9546 ROOT
        try:
            self._create_sysfs(self.PATH_MUX_9546_ROOT_CHAN0,
                               self.PATH_MUX_9546_ROOT_PARENT,
                               self.MUXs["9546_ROOT"])
        except Exception as e:
            self.logger.error("Create MUX PCA9546 ROOT fail, error: ", str(e))
            raise

        # MUX 9548 SFP1
        try:
            self._create_sysfs(self.PATH_MUX_9548_SFP_1_CHAN0,
                               self.PATH_MUX_9548_SFP_PARENT,
                               self.MUXs["9548_SFP1"])
        except Exception as e:
            self.logger.error("Create MUX 9548 SFP1 fail, error: ", str(e))
            raise

        # MUX 9548 SFP2
        try:
            self._create_sysfs(self.PATH_MUX_9548_SFP_2_CHAN0,
                               self.PATH_MUX_9548_SFP_PARENT,
                               self.MUXs["9548_SFP2"])
        except Exception as e:
            self.logger.error("Create MUX 9548 SFP2 fail, error: ", str(e))
            raise

        # MUX 9548 SFP3
        try:
            self._create_sysfs(self.PATH_MUX_9548_SFP_3_CHAN0,
                               self.PATH_MUX_9548_SFP_PARENT,
                               self.MUXs["9548_SFP3"])
        except Exception as e:
            self.logger.error("Create MUX 9548 SFP3 fail, error: ", str(e))
            raise

        # MUX 9548 SFP4
        try:
            self._create_sysfs(self.PATH_MUX_9548_SFP_4_CHAN0,
                               self.PATH_MUX_9548_SFP_PARENT,
                               self.MUXs["9548_SFP4"])
        except Exception as e:
            self.logger.error("Create MUX 9548 SFP4 fail, error: ", str(e))
            raise

        # MUX 9546 QSFP
        try:
            self._create_sysfs(self.PATH_MUX_9546_QSFP_CHAN0,
                               self.PATH_MUX_9546_QSFP_PARENT,
                               self.MUXs["9546_QSFP"])
        except Exception as e:
            self.logger.error("Create MUX 9546 QSFP fail, error: ", str(e))
            raise

        try:
            self._create_sysfs(self.PATH_MUX_9546_ROOT1_CHAN0,
                               self.PATH_MUX_9546_ROOT1_PARENT,
                               self.MUXs["9546_ROOT1"])
        except Exception as e:
            self.logger.error("Create MUX 9546 ROOT1 fail, error: ", str(e))
            raise

    def deinit(self):
        pass
