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
import time

from common.logger import Logger
from smbus import SMBus
from i2c_mux.i2c_mux import I2CMux

class PCA953x:
    I2C_ADDR_9546_ROOT = 0x76
    I2C_ADDR_9546_ROOT1 = 0x75

    def __init__(self, dev_info, i2c_mux):
        self.name = dev_info["name"]
        self.address = dev_info["address"]
        self.pins = dev_info["pins"]
        self.init_cfg = dev_info["init_cfg"]
        self.i2c_mux = i2c_mux.MUXs
        self.parent = dev_info["parent"]

    def get_channel_bus(self, channel):
        if self.parent is None:
            return SMBus(0)
        else:
            if self.i2c_mux[self.parent].ch_bus != None:
                bus_num = self.i2c_mux[self.parent].ch_bus[channel]
                return SMBus(bus_num)
            else:
                bus = SMBus(0)
                if self.parent == "9546_ROOT":
                    bus.write_byte_data(self.I2C_ADDR_9546_ROOT, 0x0, 1 << channel)
                else:
                    bus.write_byte_data(self.I2C_ADDR_9546_ROOT1, 0x0, 1 << channel)
                return bus

    def close_channel_bus(self, bus):
        if not self.parent is None and self.i2c_mux[self.parent].ch_bus is None:
            if self.parent == "9546_ROOT":
                bus.write_byte_data(self.I2C_ADDR_9546_ROOT, 0x0, 0x0)
            else:
                bus.write_byte_data(self.I2C_ADDR_9546_ROOT1, 0x0, 0x0)
        bus.close()

class PCA9535(PCA953x):

    NAME = "pca9535"
    
class PCA9535_CMD:
    
    PCA9535_REG_PORT0_IN = 0
    PCA9535_REG_PORT1_IN = 1
    PCA9535_REG_PORT0_OUT = 2
    PCA9535_REG_PORT1_OUT = 3
    PCA9535_REG_PORT0_POL_INVER = 4
    PCA9535_REG_PORT1_POL_INVER = 5
    PCA9535_REG_PORT0_CONF = 6
    PCA9535_REG_PORT1_CONF = 7

class PCA9539(PCA953x):

    NAME = "pca9539"

class IOExpander:
    
    I2C_ADDR_TPS53667 = 0x61
    ROV_List = ['N/A' , '1.00' , '0.95' , 'N/A' , '1.04']
    TPS53667_voltage = [
        {"rov": "1.00", "vol": 0x0097},
        {"rov": "0.95", "vol": 0x008D},
        {"rov": "1.04", "vol": 0x009F}
    ]

    GPIO_BASE = 511
    SIAD_IOExpanders_Order_List = ['9539_CPU' , '9535_SFP1', '9535_SFP2',
                                   '9535_QSFP', '9535_SFP3', '9535_SFP4',
                                   '9535_SFP5', '9535_SFP6', '9535_SFP7',
                                   '9535_SFP8', '9535_SFP9', '9535_SFP10',
                                   '9535_BRD']
                                   
    ResetMaskConst = {
        "SYS": {
            "name": "SYS", "bit": 4, "default": 1 },
        "DDR3": {
            "name": "DDR3", "bit": 5, "default": 1 },
    }
                          
    SIAD_IOExpanders = {
        "9539_CPU": {
            "name": "pca9539_CPU", "address": 0x77, "parent": None, "channel": None, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE,    "direction": "in"},               # gpio511 IO_1.7 CPLD_THERMTRIP_L_LATCH
                {"gpio": GPIO_BASE-1,  "direction": "in"},               # gpio510 IO_1.6 SYS_PWROK
                {"gpio": GPIO_BASE-2,  "direction": "in"},               # gpio509 IO_1.5 SLP3_L
                {"gpio": GPIO_BASE-3,  "direction": "in"},               # gpio508 IO_1.4 SYS_RESET_L  (follow diag configuration as input)
                {"gpio": GPIO_BASE-4,  "direction": "in"},               # gpio507 IO_1.3 FP_IBMC_PWRBTN_OUT_L
                {"gpio": GPIO_BASE-5,  "direction": "in"},               # gpio506 IO_1.2 CPLD_PLTRST_L_LATCH
                {"gpio": GPIO_BASE-6,  "direction": "in"},               # gpio505 IO_1.1 SLP4_L
                {"gpio": GPIO_BASE-7,  "direction": "in"},               # gpio504 IO_1.0 CPLD_CLEAR_LATCH  (follow diag configuration as input)
                {"gpio": GPIO_BASE-8,  "direction": "in"},               # gpio503 IO_0.7 SMI_ACTIVE_L
                {"gpio": GPIO_BASE-9,  "direction": "in"},               # gpio502 IO_0.6 NMI_EVENT_L
                {"gpio": GPIO_BASE-10, "direction": "in"},               # gpio501 IO_0.5 CPLD_ERROR2_L_LATCH
                {"gpio": GPIO_BASE-11, "direction": "in"},               # gpio500 IO_0.4 CPLD_ERROR1_L_LATCH
                {"gpio": GPIO_BASE-12, "direction": "in"},               # gpio499 IO_0.3 CPLD_ERROR0_L_LATCH
                {"gpio": GPIO_BASE-13, "direction": "in"},               # gpio498 IO_0.2 CPLD_CATEER_L_LATCH
                {"gpio": GPIO_BASE-14, "direction": "in"},               # gpio497 IO_0.1 CPLD_PCHOT_L_LATCH
                {"gpio": GPIO_BASE-15, "direction": "in"}                # gpio496 IO_0.0 CPLD_PROCHOT_L_LATCH
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xff
        },
        "9535_SFP1": {
            "name": "pca9535_TX_DIS_1", "address": 0x22, "parent": "9546_ROOT", "channel": 0, "pins": 16,
            "port_idx": {
                "0": 8, "1": 9, "2": 10, "3": 11, "4": 12, "5": 13, "6": 14,
                "7": 15, "8": 0, "9": 1, "10": 2, "11": 3, "12": 4, "13": 5,
                "14": 6, "15": 7
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-16, "direction": "out", "value": 0},  # gpio495 IO_1.7 SFP+_P08_TX_DIS
                {"gpio": GPIO_BASE-17, "direction": "out", "value": 0},  # gpio494 IO_1.6 SFP+_P09_TX_DIS
                {"gpio": GPIO_BASE-18, "direction": "out", "value": 0},  # gpio493 IO_1.5 SFP+_P10_TX_DIS
                {"gpio": GPIO_BASE-19, "direction": "out", "value": 0},  # gpio492 IO_1.4 SFP+_P11_TX_DIS
                {"gpio": GPIO_BASE-20, "direction": "out", "value": 0},  # gpio491 IO_1.3 SFP+_P12_TX_DIS
                {"gpio": GPIO_BASE-21, "direction": "out", "value": 0},  # gpio490 IO_1.2 SFP+_P13_TX_DIS
                {"gpio": GPIO_BASE-22, "direction": "out", "value": 0},  # gpio489 IO_1.1 SFP+_P14_TX_DIS
                {"gpio": GPIO_BASE-23, "direction": "out", "value": 0},  # gpio488 IO_1.0 SFP+_P15_TX_DIS
                {"gpio": GPIO_BASE-24, "direction": "out", "value": 0},  # gpio487 IO_0.7 SFP+_P00_TX_DIS
                {"gpio": GPIO_BASE-25, "direction": "out", "value": 0},  # gpio486 IO_0.6 SFP+_P01_TX_DIS
                {"gpio": GPIO_BASE-26, "direction": "out", "value": 0},  # gpio485 IO_0.5 SFP+_P02_TX_DIS
                {"gpio": GPIO_BASE-27, "direction": "out", "value": 0},  # gpio484 IO_0.4 SFP+_P03_TX_DIS
                {"gpio": GPIO_BASE-28, "direction": "out", "value": 0},  # gpio483 IO_0.3 SFP+_P04_TX_DIS
                {"gpio": GPIO_BASE-29, "direction": "out", "value": 0},  # gpio482 IO_0.2 SFP+_P05_TX_DIS
                {"gpio": GPIO_BASE-30, "direction": "out", "value": 0},  # gpio481 IO_0.1 SFP+_P06_TX_DIS
                {"gpio": GPIO_BASE-31, "direction": "out", "value": 0}   # gpio480 IO_0.0 SFP+_P07_TX_DIS
            ],
            "config_0": 0x0, "config_1": 0x0, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0 
        },
        "9535_SFP2": {
            "name": "pca9535_TX_DIS_2", "address": 0x24, "parent": "9546_ROOT", "channel": 0, "pins": 16,
            "port_idx": {
                "24": 0, "25": 1, "26": 2, "27": 3, "16": 8, "17": 9, "18": 10,
                "19": 11, "20": 12, "21": 13, "22": 14, "23": 15
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-32, "direction": "out", "value": 0},  # gpio479 IO_1.7 SFP+_P24_TX_DIS
                {"gpio": GPIO_BASE-33, "direction": "out", "value": 0},  # gpio478 IO_1.6 SFP+_P25_TX_DIS
                {"gpio": GPIO_BASE-34, "direction": "out", "value": 0},  # gpio477 IO_1.5 SFP+_P26_TX_DIS
                {"gpio": GPIO_BASE-35, "direction": "out", "value": 0},  # gpio476 IO_1.4 SFP+_P27_TX_DIS
                {"gpio": GPIO_BASE-36, "direction": "out", "value": 0},  # gpio475 IO_1.3 NI
                {"gpio": GPIO_BASE-37, "direction": "out", "value": 0},  # gpio474 IO_1.2 NI
                {"gpio": GPIO_BASE-38, "direction": "out", "value": 0},  # gpio473 IO_1.1 NI
                {"gpio": GPIO_BASE-39, "direction": "out", "value": 0},  # gpio472 IO_1.0 NI
                {"gpio": GPIO_BASE-40, "direction": "out", "value": 0},  # gpio471 IO_0.7 SFP+_P16_TX_DIS
                {"gpio": GPIO_BASE-41, "direction": "out", "value": 0},  # gpio470 IO_0.6 SFP+_P17_TX_DIS
                {"gpio": GPIO_BASE-42, "direction": "out", "value": 0},  # gpio469 IO_0.5 SFP+_P18_TX_DIS
                {"gpio": GPIO_BASE-43, "direction": "out", "value": 0},  # gpio468 IO_0.4 SFP+_P19_TX_DIS
                {"gpio": GPIO_BASE-44, "direction": "out", "value": 0},  # gpio467 IO_0.3 SFP+_P20_TX_DIS
                {"gpio": GPIO_BASE-45, "direction": "out", "value": 0},  # gpio466 IO_0.2 SFP+_P21_TX_DIS
                {"gpio": GPIO_BASE-46, "direction": "out", "value": 0},  # gpio465 IO_0.1 SFP+_P22_TX_DIS
                {"gpio": GPIO_BASE-47, "direction": "out", "value": 0}   # gpio464 IO_0.0 SFP+_P23_TX_DIS
            ],
            "config_0": 0x0, "config_1": 0x0, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9535_QSFP": {
            "name": "pca9535_QSFP", "address": 0x21, "parent": "9546_ROOT", "channel": 0, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-48, "direction": "out", "value": 0},  # gpio463 IO_1.7 NI
                {"gpio": GPIO_BASE-49, "direction": "out", "value": 0},  # gpio462 IO_1.6 NI
                {"gpio": GPIO_BASE-50, "direction": "out", "value": 1},  # gpio461 IO_1.5 QSFP28_P1_RST_N
                {"gpio": GPIO_BASE-51, "direction": "out", "value": 1},  # gpio460 IO_1.4 QSFP28_P2_RST_N
                {"gpio": GPIO_BASE-52, "direction": "out", "value": 0},  # gpio459 IO_1.3 NI
                {"gpio": GPIO_BASE-53, "direction": "out", "value": 0},  # gpio458 IO_1.2 NI
                {"gpio": GPIO_BASE-54, "direction": "out", "value": 0},  # gpio457 IO_1.1 QSFP28_P1_LPMODE
                {"gpio": GPIO_BASE-55, "direction": "out", "value": 0},  # gpio456 IO_1.0 QSFP28_P2_LPMODE
                {"gpio": GPIO_BASE-56, "direction": "out", "value": 0},  # gpio455 IO_0.7 NI
                {"gpio": GPIO_BASE-57, "direction": "out", "value": 0},  # gpio454 IO_0.6 NI
                {"gpio": GPIO_BASE-58, "direction": "in"},               # gpio453 IO_0.5 QSFP28_P1_PRSNT_N
                {"gpio": GPIO_BASE-59, "direction": "in"},               # gpio452 IO_0.4 QSFP28_P2_PRSNT_N
                {"gpio": GPIO_BASE-60, "direction": "out", "value": 0},  # gpio451 IO_0.3 NI
                {"gpio": GPIO_BASE-61, "direction": "out", "value": 0},  # gpio450 IO_0.2 NI
                {"gpio": GPIO_BASE-62, "direction": "in"},               # gpio449 IO_0.1 QSFP28_P1_INT_N
                {"gpio": GPIO_BASE-63, "direction": "in"}                # gpio448 IO_0.0 QSFP28_P2_INT_N
            ],
            "config_0": 0x33, "config_1": 0x00, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x30
        },
        "9535_SFP3": {
            "name": "pca9535_TX_FLT_1", "address": 0x26, "parent": "9546_ROOT", "channel": 1, "pins": 16,
            "port_idx": {
                "0": 8, "1": 9, "2": 10, "3": 11, "4": 12, "5": 13, "6": 14,
                "7": 15, "8": 0, "9": 1, "10": 2, "11": 3, "12": 4, "13": 5,
                "14": 6, "15": 7
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-64, "direction": "in"},  # gpio447 IO_1.7 SFP+_P08_TX_FLT
                {"gpio": GPIO_BASE-65, "direction": "in"},  # gpio446 IO_1.6 SFP+_P09_TX_FLT
                {"gpio": GPIO_BASE-66, "direction": "in"},  # gpio445 IO_1.5 SFP+_P10_TX_FLT
                {"gpio": GPIO_BASE-67, "direction": "in"},  # gpio444 IO_1.4 SFP+_P11_TX_FLT
                {"gpio": GPIO_BASE-68, "direction": "in"},  # gpio443 IO_1.3 SFP+_P12_TX_FLT
                {"gpio": GPIO_BASE-69, "direction": "in"},  # gpio442 IO_1.2 SFP+_P13_TX_FLT
                {"gpio": GPIO_BASE-70, "direction": "in"},  # gpio441 IO_1.1 SFP+_P14_TX_FLT
                {"gpio": GPIO_BASE-71, "direction": "in"},  # gpio440 IO_1.0 SFP+_P15_TX_FLT
                {"gpio": GPIO_BASE-72, "direction": "in"},  # gpio439 IO_0.7 SFP+_P00_TX_FLT
                {"gpio": GPIO_BASE-73, "direction": "in"},  # gpio438 IO_0.6 SFP+_P01_TX_FLT
                {"gpio": GPIO_BASE-74, "direction": "in"},  # gpio437 IO_0.5 SFP+_P02_TX_FLT
                {"gpio": GPIO_BASE-75, "direction": "in"},  # gpio436 IO_0.4 SFP+_P03_TX_FLT
                {"gpio": GPIO_BASE-76, "direction": "in"},  # gpio435 IO_0.3 SFP+_P04_TX_FLT
                {"gpio": GPIO_BASE-77, "direction": "in"},  # gpio434 IO_0.2 SFP+_P05_TX_FLT
                {"gpio": GPIO_BASE-78, "direction": "in"},  # gpio433 IO_0.1 SFP+_P06_TX_FLT
                {"gpio": GPIO_BASE-79, "direction": "in"}   # gpio432 IO_0.0 SFP+_P07_TX_FLT
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xff
        },
        "9535_SFP4": {
            "name": "pca9535_TX_FLT_2", "address": 0x27, "parent": "9546_ROOT", "channel": 1, "pins": 16,
            "port_idx": {
                "24": 0, "25": 1, "26": 2, "27": 3, "16": 8, "17": 9, "18": 10,
                "19": 11, "20": 12, "21": 13, "22": 14, "23": 15
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-80, "direction": "in"},  # gpio431 IO_1.7 SFP+_P24_TX_FLT
                {"gpio": GPIO_BASE-81, "direction": "in"},  # gpio430 IO_1.6 SFP+_P25_TX_FLT
                {"gpio": GPIO_BASE-82, "direction": "in"},  # gpio429 IO_1.5 SFP+_P26_TX_FLT
                {"gpio": GPIO_BASE-83, "direction": "in"},  # gpio428 IO_1.4 SFP+_P27_TX_FLT
                {"gpio": GPIO_BASE-84, "direction": "out", "value": 0},  # gpio427 IO_1.3 NI
                {"gpio": GPIO_BASE-85, "direction": "out", "value": 0},  # gpio426 IO_1.2 NI
                {"gpio": GPIO_BASE-86, "direction": "out", "value": 0},  # gpio425 IO_1.1 NI
                {"gpio": GPIO_BASE-87, "direction": "out", "value": 0},  # gpio424 IO_1.0 NI
                {"gpio": GPIO_BASE-88, "direction": "in"},  # gpio423 IO_0.7 SFP+_P16_TX_FLT
                {"gpio": GPIO_BASE-89, "direction": "in"},  # gpio422 IO_0.6 SFP+_P17_TX_FLT
                {"gpio": GPIO_BASE-90, "direction": "in"},  # gpio421 IO_0.5 SFP+_P18_TX_FLT
                {"gpio": GPIO_BASE-91, "direction": "in"},  # gpio420 IO_0.4 SFP+_P19_TX_FLT
                {"gpio": GPIO_BASE-92, "direction": "in"},  # gpio419 IO_0.3 SFP+_P20_TX_FLT
                {"gpio": GPIO_BASE-93, "direction": "in"},  # gpio418 IO_0.2 SFP+_P21_TX_FLT
                {"gpio": GPIO_BASE-94, "direction": "in"},  # gpio417 IO_0.1 SFP+_P22_TX_FLT
                {"gpio": GPIO_BASE-95, "direction": "in"}   # gpio416 IO_0.0 SFP+_P23_TX_FLT
            ],
            "config_0": 0xff, "config_1": 0xf0, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xf0
        },
        "9535_SFP5": {
            "name": "pca9535_RATE_SEL_1", "address": 0x25, "parent": "9546_ROOT", "channel": 1, "pins": 16,
            "port_idx": {
                "0": 8, "1": 9, "2": 10, "3": 11, "4": 12, "5": 13, "6": 14,
                "7": 15, "8": 0, "9": 1, "10": 2, "11": 3, "12": 4, "13": 5,
                "14": 6, "15": 7
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-96,  "direction": "out", "value": 1},  # gpio415 IO_1.7 SFP+_P08_RATE_SEL
                {"gpio": GPIO_BASE-97,  "direction": "out", "value": 1},  # gpio414 IO_1.6 SFP+_P09_RATE_SEL
                {"gpio": GPIO_BASE-98,  "direction": "out", "value": 1},  # gpio413 IO_1.5 SFP+_P10_RATE_SEL
                {"gpio": GPIO_BASE-99,  "direction": "out", "value": 1},  # gpio412 IO_1.4 SFP+_P11_RATE_SEL
                {"gpio": GPIO_BASE-100, "direction": "out", "value": 1},  # gpio411 IO_1.3 SFP+_P12_RATE_SEL
                {"gpio": GPIO_BASE-101, "direction": "out", "value": 1},  # gpio410 IO_1.2 SFP+_P13_RATE_SEL
                {"gpio": GPIO_BASE-102, "direction": "out", "value": 1},  # gpio409 IO_1.1 SFP+_P14_RATE_SEL
                {"gpio": GPIO_BASE-103, "direction": "out", "value": 1},  # gpio408 IO_1.0 SFP+_P15_RATE_SEL
                {"gpio": GPIO_BASE-104, "direction": "out", "value": 1},  # gpio407 IO_0.7 SFP+_P00_RATE_SEL
                {"gpio": GPIO_BASE-105, "direction": "out", "value": 1},  # gpio406 IO_0.6 SFP+_P01_RATE_SEL
                {"gpio": GPIO_BASE-106, "direction": "out", "value": 1},  # gpio405 IO_0.5 SFP+_P02_RATE_SEL
                {"gpio": GPIO_BASE-107, "direction": "out", "value": 1},  # gpio404 IO_0.4 SFP+_P03_RATE_SEL
                {"gpio": GPIO_BASE-108, "direction": "out", "value": 1},  # gpio403 IO_0.3 SFP+_P04_RATE_SEL
                {"gpio": GPIO_BASE-109, "direction": "out", "value": 1},  # gpio402 IO_0.2 SFP+_P05_RATE_SEL
                {"gpio": GPIO_BASE-110, "direction": "out", "value": 1},  # gpio401 IO_0.1 SFP+_P06_RATE_SEL
                {"gpio": GPIO_BASE-111, "direction": "out", "value": 1}   # gpio400 IO_0.0 SFP+_P07_RATE_SEL
            ],
            "config_0": 0x0, "config_1": 0x0, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xff
        },
        "9535_SFP6": {
            "name": "pca9535_RATE_SEL_2", "address": 0x23, "parent": "9546_ROOT", "channel": 1, "pins": 16,
            "port_idx": {
                "24": 0, "25": 1, "26": 2, "27": 3, "16": 8, "17": 9, "18": 10,
                "19": 11, "20": 12, "21": 13, "22": 14, "23": 15
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-112, "direction": "out", "value": 1},  # gpio399 IO_1.7 SFP+_P24_RATE_SEL
                {"gpio": GPIO_BASE-113, "direction": "out", "value": 1},  # gpio398 IO_1.6 SFP+_P25_RATE_SEL
                {"gpio": GPIO_BASE-114, "direction": "out", "value": 1},  # gpio397 IO_1.5 SFP+_P26_RATE_SEL
                {"gpio": GPIO_BASE-115, "direction": "out", "value": 1},  # gpio396 IO_1.4 SFP+_P27_RATE_SEL
                {"gpio": GPIO_BASE-116, "direction": "out", "value": 1},  # gpio395 IO_1.3 NI
                {"gpio": GPIO_BASE-117, "direction": "out", "value": 1},  # gpio394 IO_1.2 NI
                {"gpio": GPIO_BASE-118, "direction": "out", "value": 1},  # gpio393 IO_1.1 NI
                {"gpio": GPIO_BASE-119, "direction": "out", "value": 1},  # gpio392 IO_1.0 NI
                {"gpio": GPIO_BASE-120, "direction": "out", "value": 1},  # gpio391 IO_0.7 SFP+_P16_RATE_SEL
                {"gpio": GPIO_BASE-121, "direction": "out", "value": 1},  # gpio390 IO_0.6 SFP+_P17_RATE_SEL
                {"gpio": GPIO_BASE-122, "direction": "out", "value": 1},  # gpio389 IO_0.5 SFP+_P18_RATE_SEL
                {"gpio": GPIO_BASE-123, "direction": "out", "value": 1},  # gpio388 IO_0.4 SFP+_P19_RATE_SEL
                {"gpio": GPIO_BASE-124, "direction": "out", "value": 1},  # gpio387 IO_0.3 SFP+_P20_RATE_SEL
                {"gpio": GPIO_BASE-125, "direction": "out", "value": 1},  # gpio386 IO_0.2 SFP+_P21_RATE_SEL
                {"gpio": GPIO_BASE-126, "direction": "out", "value": 1},  # gpio385 IO_0.1 SFP+_P22_RATE_SEL
                {"gpio": GPIO_BASE-127, "direction": "out", "value": 1}   # gpio384 IO_0.0 SFP+_P23_RATE_SEL
            ],
            "config_0": 0x0, "config_1": 0x0, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xff
        },
        "9535_SFP7": {
            "name": "pca9535_ABS_1", "address": 0x20, "parent": "9546_ROOT", "channel": 2, "pins": 16,
            "port_idx": {
                "0": 8, "1": 9, "2": 10, "3": 11, "4": 12, "5": 13, "6": 14,
                "7": 15, "8": 0, "9": 1, "10": 2, "11": 3, "12": 4, "13": 5,
                "14": 6, "15": 7
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-128, "direction": "in"},  # gpio383 IO_1.7 SFP+_P08_MODE_ABS
                {"gpio": GPIO_BASE-129, "direction": "in"},  # gpio382 IO_1.6 SFP+_P09_MODE_ABS
                {"gpio": GPIO_BASE-130, "direction": "in"},  # gpio381 IO_1.5 SFP+_P10_MODE_ABS
                {"gpio": GPIO_BASE-131, "direction": "in"},  # gpio380 IO_1.4 SFP+_P11_MODE_ABS
                {"gpio": GPIO_BASE-132, "direction": "in"},  # gpio379 IO_1.3 SFP+_P12_MODE_ABS
                {"gpio": GPIO_BASE-133, "direction": "in"},  # gpio378 IO_1.2 SFP+_P13_MODE_ABS
                {"gpio": GPIO_BASE-134, "direction": "in"},  # gpio377 IO_1.1 SFP+_P14_MODE_ABS
                {"gpio": GPIO_BASE-135, "direction": "in"},  # gpio376 IO_1.0 SFP+_P15_MODE_ABS
                {"gpio": GPIO_BASE-136, "direction": "in"},  # gpio375 IO_0.7 SFP+_P00_MODE_ABS
                {"gpio": GPIO_BASE-137, "direction": "in"},  # gpio374 IO_0.6 SFP+_P01_MODE_ABS
                {"gpio": GPIO_BASE-138, "direction": "in"},  # gpio373 IO_0.5 SFP+_P02_MODE_ABS
                {"gpio": GPIO_BASE-139, "direction": "in"},  # gpio372 IO_0.4 SFP+_P03_MODE_ABS
                {"gpio": GPIO_BASE-140, "direction": "in"},  # gpio371 IO_0.3 SFP+_P04_MODE_ABS
                {"gpio": GPIO_BASE-141, "direction": "in"},  # gpio370 IO_0.2 SFP+_P05_MODE_ABS
                {"gpio": GPIO_BASE-142, "direction": "in"},  # gpio369 IO_0.1 SFP+_P06_MODE_ABS
                {"gpio": GPIO_BASE-143, "direction": "in"}   # gpio368 IO_0.0 SFP+_P07_MODE_ABS
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xff
        },
        "9535_SFP8": {
            "name": "pca9535_ABS_2", "address": 0x22, "parent": "9546_ROOT", "channel": 2, "pins": 16,
            "port_idx": {
                "24": 0, "25": 1, "26": 2, "27": 3, "16": 8, "17": 9, "18": 10,
                "19": 11, "20": 12, "21": 13, "22": 14, "23": 15
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-144, "direction": "in"},  # gpio367 IO_1.7 SFP+_P24_MODE_ABS
                {"gpio": GPIO_BASE-145, "direction": "in"},  # gpio366 IO_1.6 SFP+_P25_MODE_ABS
                {"gpio": GPIO_BASE-146, "direction": "in"},  # gpio365 IO_1.5 SFP+_P26_MODE_ABS
                {"gpio": GPIO_BASE-147, "direction": "in"},  # gpio364 IO_1.4 SFP+_P27_MODE_ABS
                {"gpio": GPIO_BASE-148, "direction": "out", "value": 0},  # gpio363 IO_1.3 NI
                {"gpio": GPIO_BASE-149, "direction": "out", "value": 0},  # gpio362 IO_1.2 NI
                {"gpio": GPIO_BASE-150, "direction": "out", "value": 0},  # gpio361 IO_1.1 NI
                {"gpio": GPIO_BASE-151, "direction": "out", "value": 0},  # gpio360 IO_1.0 NI
                {"gpio": GPIO_BASE-152, "direction": "in"},  # gpio359 IO_0.7 SFP+_P16_MODE_ABS
                {"gpio": GPIO_BASE-153, "direction": "in"},  # gpio358 IO_0.6 SFP+_P17_MODE_ABS
                {"gpio": GPIO_BASE-154, "direction": "in"},  # gpio357 IO_0.5 SFP+_P18_MODE_ABS
                {"gpio": GPIO_BASE-155, "direction": "in"},  # gpio356 IO_0.4 SFP+_P19_MODE_ABS
                {"gpio": GPIO_BASE-156, "direction": "in"},  # gpio355 IO_0.3 SFP+_P20_MODE_ABS
                {"gpio": GPIO_BASE-157, "direction": "in"},  # gpio354 IO_0.2 SFP+_P21_MODE_ABS
                {"gpio": GPIO_BASE-158, "direction": "in"},  # gpio353 IO_0.1 SFP+_P22_MODE_ABS
                {"gpio": GPIO_BASE-159, "direction": "in"}   # gpio352 IO_0.0 SFP+_P23_MODE_ABS
            ],
            "config_0": 0xff, "config_1": 0xf0, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xf0
        },
        "9535_SFP9": {
            "name": "pca9535_RX_LOS_1", "address": 0x21, "parent": "9546_ROOT", "channel": 2, "pins": 16,
            "port_idx": {
                "0": 8, "1": 9, "2": 10, "3": 11, "4": 12, "5": 13, "6": 14,
                "7": 15, "8": 0, "9": 1, "10": 2, "11": 3, "12": 4, "13": 5,
                "14": 6, "15": 7
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-160, "direction": "in"},  # gpio351 IO_1.7 SFP+_P08_RX_LOS
                {"gpio": GPIO_BASE-161, "direction": "in"},  # gpio350 IO_1.6 SFP+_P09_RX_LOS
                {"gpio": GPIO_BASE-162, "direction": "in"},  # gpio349 IO_1.5 SFP+_P10_RX_LOS
                {"gpio": GPIO_BASE-163, "direction": "in"},  # gpio348 IO_1.4 SFP+_P11_RX_LOS
                {"gpio": GPIO_BASE-164, "direction": "in"},  # gpio347 IO_1.3 SFP+_P12_RX_LOS
                {"gpio": GPIO_BASE-165, "direction": "in"},  # gpio346 IO_1.2 SFP+_P13_RX_LOS
                {"gpio": GPIO_BASE-166, "direction": "in"},  # gpio345 IO_1.1 SFP+_P14_RX_LOS
                {"gpio": GPIO_BASE-167, "direction": "in"},  # gpio344 IO_1.0 SFP+_P15_RX_LOS
                {"gpio": GPIO_BASE-168, "direction": "in"},  # gpio343 IO_0.7 SFP+_P00_RX_LOS
                {"gpio": GPIO_BASE-169, "direction": "in"},  # gpio342 IO_0.6 SFP+_P01_RX_LOS
                {"gpio": GPIO_BASE-170, "direction": "in"},  # gpio341 IO_0.5 SFP+_P02_RX_LOS
                {"gpio": GPIO_BASE-171, "direction": "in"},  # gpio340 IO_0.4 SFP+_P03_RX_LOS
                {"gpio": GPIO_BASE-172, "direction": "in"},  # gpio339 IO_0.3 SFP+_P04_RX_LOS
                {"gpio": GPIO_BASE-173, "direction": "in"},  # gpio338 IO_0.2 SFP+_P05_RX_LOS
                {"gpio": GPIO_BASE-174, "direction": "in"},  # gpio337 IO_0.1 SFP+_P06_RX_LOS
                {"gpio": GPIO_BASE-175, "direction": "in"}   # gpio336 IO_0.0 SFP+_P07_RX_LOS
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xff
        },
        "9535_SFP10": {
            "name": "pca9535_RX_LOS_2", "address": 0x24, "parent": "9546_ROOT", "channel": 2, "pins": 16,
            "port_idx": {
                "24": 0, "25": 1, "26": 2, "27": 3, "16": 8, "17": 9, "18": 10,
                "19": 11, "20": 12, "21": 13, "22": 14, "23": 15
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-176, "direction": "in"},  # gpio335 IO_1.7 SFP+_P24_RX_LOS
                {"gpio": GPIO_BASE-177, "direction": "in"},  # gpio334 IO_1.6 SFP+_P25_RX_LOS
                {"gpio": GPIO_BASE-178, "direction": "in"},  # gpio333 IO_1.5 SFP+_P26_RX_LOS
                {"gpio": GPIO_BASE-179, "direction": "in"},  # gpio332 IO_1.4 SFP+_P27_RX_LOS
                {"gpio": GPIO_BASE-180, "direction": "out", "value": 0},  # gpio331 IO_1.3 NI
                {"gpio": GPIO_BASE-181, "direction": "out", "value": 0},  # gpio330 IO_1.2 NI
                {"gpio": GPIO_BASE-182, "direction": "out", "value": 0},  # gpio329 IO_1.1 NI
                {"gpio": GPIO_BASE-183, "direction": "out", "value": 0},  # gpio328 IO_1.0 NI
                {"gpio": GPIO_BASE-184, "direction": "in"},  # gpio327 IO_0.7 SFP+_P16_RX_LOS
                {"gpio": GPIO_BASE-185, "direction": "in"},  # gpio326 IO_0.6 SFP+_P17_RX_LOS
                {"gpio": GPIO_BASE-186, "direction": "in"},  # gpio325 IO_0.5 SFP+_P18_RX_LOS
                {"gpio": GPIO_BASE-187, "direction": "in"},  # gpio324 IO_0.4 SFP+_P19_RX_LOS
                {"gpio": GPIO_BASE-188, "direction": "in"},  # gpio323 IO_0.3 SFP+_P20_RX_LOS
                {"gpio": GPIO_BASE-189, "direction": "in"},  # gpio322 IO_0.2 SFP+_P21_RX_LOS
                {"gpio": GPIO_BASE-190, "direction": "in"},  # gpio321 IO_0.1 SFP+_P22_RX_LOS
                {"gpio": GPIO_BASE-191, "direction": "in"}   # gpio320 IO_0.0 SFP+_P23_RX_LOS
            ],
            "config_0": 0xff, "config_1": 0xf0, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0xff, "output_port_1": 0xf0
        },
        "9535_BRD": {
            "name": "pca9535_brd_id", "address": 0x20, "parent": "9546_ROOT1", "channel": 2, "pins": 16,
            "port_idx": {
                "24": 0, "25": 1, "26": 2, "27": 3, "16": 8, "17": 9, "18": 10,
                "19": 11, "20": 12, "21": 13, "22": 14, "23": 15
            },
            "init_cfg": [
                {"gpio": GPIO_BASE-192, "direction": "in"},  # gpio335 IO_1.7 SKU_ID3
                {"gpio": GPIO_BASE-193, "direction": "in"},  # gpio334 IO_1.6 SKU_ID2
                {"gpio": GPIO_BASE-194, "direction": "in"},  # gpio333 IO_1.5 SKU_ID1
                {"gpio": GPIO_BASE-195, "direction": "in"},  # gpio332 IO_1.4 SKU_ID0
                {"gpio": GPIO_BASE-196, "direction": "in"},  # gpio331 IO_1.3 HW_REV_ID0
                {"gpio": GPIO_BASE-197, "direction": "in"},  # gpio330 IO_1.2 HW_REV_ID1
                {"gpio": GPIO_BASE-198, "direction": "in"},  # gpio329 IO_1.1 BUILD_ID0
                {"gpio": GPIO_BASE-199, "direction": "in"},  # gpio328 IO_1.0 BUILD_ID1
                {"gpio": GPIO_BASE-200, "direction": "in"},  # gpio327 IO_0.7 INT_ALRM3_N
                {"gpio": GPIO_BASE-201, "direction": "in"},  # gpio326 IO_0.6 INT_ALRM2_N
                {"gpio": GPIO_BASE-202, "direction": "in", "value": 1},  # gpio325 IO_0.5 RST_BMC_DDR3_X86_N # config in->out when apply
                {"gpio": GPIO_BASE-203, "direction": "in", "value": 1},  # gpio324 IO_0.4 RST_BMC_SYS_X86_L # config in->out when apply
                {"gpio": GPIO_BASE-204, "direction": "out", "value": 0},  # gpio323 IO_0.3 NI
                {"gpio": GPIO_BASE-205, "direction": "in"},  # gpio322 IO_0.2 MAC_VCORE_ROV2
                {"gpio": GPIO_BASE-206, "direction": "in"},  # gpio321 IO_0.1 MAC_VCORE_ROV1
                {"gpio": GPIO_BASE-207, "direction": "in"}   # gpio320 IO_0.0 MAC_VCORE_ROV0
            ],
            "config_0": 0xf7, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x38, "output_port_1": 0xff
        }
    }

    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"
    PATH_SYS_GPIO = "/sys/class/gpio"

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.IOExpanders = self.SIAD_IOExpanders
        self.ordered_ioexps = self.SIAD_IOExpanders_Order_List
        self.i2c_mux = I2CMux()

        for ioexp_name in self.ordered_ioexps:
            if ioexp_name == "9539_CPU":
                ioexp = PCA9539(self.IOExpanders[ioexp_name], self.i2c_mux)
            else:
                ioexp = PCA9535(self.IOExpanders[ioexp_name], self.i2c_mux)
            self.IOExpanders[ioexp_name]["ioexp"] = ioexp

    def _create_sysfs(self, path_parent, ioexp):
        try:
            sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + str(ioexp.bus_num) +\
                         "-" + hex(ioexp.address)[2:].zfill(4)
            if os.path.exists(sysfs_path):
                self.logger.info(ioexp.name + " is already exist")
                return

            with open(path_parent + "/new_device", 'w') as f:
                f.write(ioexp.NAME + " " + hex(ioexp.address))
            self.logger.info("Register " + ioexp.name + " in sysfs")
        except Exception as e:
            self.logger.error("Register IOExpander " + ioexp.name + " error: " + str(e))
            raise

    def _export_gpio(self, ioexp, pin, gpio_num):
        try:
            if (os.path.exists(self.PATH_SYS_GPIO + "/gpio" + str(gpio_num))):
                self.logger.info(ioexp.name + "(pin:" + str(pin) + ") is already exist")
            else:
                with open(self.PATH_SYS_GPIO + "/export", "w") as f:
                    f.write(str(gpio_num))
                self.logger.info("Export " + ioexp.name + "(pin:" + str(pin) + ") at GPIO " + str(gpio_num))
        except Exception as e:
            self.logger.error("Export GPIO for " + ioexp.name + "(pin:" + str(pin) + ") error: " + str(e))
            raise

    def _init_gpio(self, ioexp, pin, gpio_num):
        try:
            if (os.path.exists(self.PATH_SYS_GPIO + "/gpio" + str(gpio_num))):
                # Set direction
                with open(self.PATH_SYS_GPIO + "/gpio" + str(gpio_num) + "/direction", "w") as f:
                    f.write(ioexp.init_cfg[pin]["direction"])
                self.logger.info("Set " + ioexp.name + "(pin:" + str(pin) + ") direction: " + ioexp.init_cfg[pin]["direction"])

                # If no "value" in dict, means this pin is for input, config next one
                key = "value"
                if key not in ioexp.init_cfg[pin]:
                    return

                # This pin is for output, set initial value
                with open(self.PATH_SYS_GPIO + "/gpio" + str(gpio_num) + "/value", "w") as f:
                    f.write(str(ioexp.init_cfg[pin]["value"]))
                self.logger.info("Set " + ioexp.name + "(pin:" + str(pin) + ") output value: " + str(ioexp.init_cfg[pin]["value"]))
            else:
                self.logger.warning(ioexp.name + "(pin:" + str(pin) + ") is not exported yet")
        except Exception as e:
            self.logger.error("Initialize " + ioexp.name + "(pin:" + str(pin) + ") fail, error: " + str(e))
            raise

    def _clear_interrupt(self, ioexp):
        try:
            if ioexp.name == "pca9535_QSFP":
                # Read QSFP28_P1_INT_N, QSFP28_P2_INT_N to clear interrupts
                need_clear_pin = (self.GPIO_BASE-62, self.GPIO_BASE-63)
            elif ioexp.name == "pca9535_TX_FLT_1":
                # Read all pca9535_TX_FLT_1 pins to clear TX_FLT interrupts
                need_clear_pin = (self.GPIO_BASE-72, self.GPIO_BASE-73,
                                  self.GPIO_BASE-74, self.GPIO_BASE-75,
                                  self.GPIO_BASE-76, self.GPIO_BASE-77,
                                  self.GPIO_BASE-78, self.GPIO_BASE-79,
                                  self.GPIO_BASE-64, self.GPIO_BASE-65,
                                  self.GPIO_BASE-65, self.GPIO_BASE-67,
                                  self.GPIO_BASE-68, self.GPIO_BASE-69,
                                  self.GPIO_BASE-70, self.GPIO_BASE-71)
            elif ioexp.name == "pca9535_TX_FLT_2":
                # Read all pca9535_TX_FLT_2 pins to clear TX_FLT interrupts
                need_clear_pin = (self.GPIO_BASE-88, self.GPIO_BASE-89,
                                  self.GPIO_BASE-90, self.GPIO_BASE-91,
                                  self.GPIO_BASE-92, self.GPIO_BASE-93,
                                  self.GPIO_BASE-94, self.GPIO_BASE-95,
                                  self.GPIO_BASE-80, self.GPIO_BASE-81,
                                  self.GPIO_BASE-82, self.GPIO_BASE-83)
            elif ioexp.name == "pca9535_ABS_1":
                # Read all pca9535_ABS_1 pins to clear MODE_ABS interrupts
                need_clear_pin = (self.GPIO_BASE-136, self.GPIO_BASE-137,
                                  self.GPIO_BASE-138, self.GPIO_BASE-139,
                                  self.GPIO_BASE-140, self.GPIO_BASE-141,
                                  self.GPIO_BASE-142, self.GPIO_BASE-143,
                                  self.GPIO_BASE-128, self.GPIO_BASE-129,
                                  self.GPIO_BASE-130, self.GPIO_BASE-131,
                                  self.GPIO_BASE-132, self.GPIO_BASE-133,
                                  self.GPIO_BASE-134, self.GPIO_BASE-135)
            elif ioexp.name == "pca9535_ABS_2":
                # Read all pca9535_ABS_2 pins to clear MODE_ABS interrupts
                need_clear_pin = (self.GPIO_BASE-152, self.GPIO_BASE-153,
                                  self.GPIO_BASE-154, self.GPIO_BASE-155,
                                  self.GPIO_BASE-156, self.GPIO_BASE-157,
                                  self.GPIO_BASE-158, self.GPIO_BASE-159,
                                  self.GPIO_BASE-144, self.GPIO_BASE-145,
                                  self.GPIO_BASE-146, self.GPIO_BASE-147)
            elif ioexp.name == "pca9535_RX_LOS_1":
                # Read all pca9535_RX_LOS_1 pins to clear RX_LOS interrupts
                need_clear_pin = (self.GPIO_BASE-168, self.GPIO_BASE-169,
                                  self.GPIO_BASE-170, self.GPIO_BASE-171,
                                  self.GPIO_BASE-172, self.GPIO_BASE-173,
                                  self.GPIO_BASE-174, self.GPIO_BASE-175,
                                  self.GPIO_BASE-160, self.GPIO_BASE-161,
                                  self.GPIO_BASE-162, self.GPIO_BASE-163,
                                  self.GPIO_BASE-164, self.GPIO_BASE-165,
                                  self.GPIO_BASE-166, self.GPIO_BASE-167)
            elif ioexp.name == "pca9535_RX_LOS_2":
                # Read all pca9535_RX_LOS_2 pins to clear RX_LOS interrupts
                need_clear_pin = (self.GPIO_BASE-184, self.GPIO_BASE-185,
                                  self.GPIO_BASE-186, self.GPIO_BASE-187,
                                  self.GPIO_BASE-188, self.GPIO_BASE-189,
                                  self.GPIO_BASE-190, self.GPIO_BASE-191,
                                  self.GPIO_BASE-176, self.GPIO_BASE-177,
                                  self.GPIO_BASE-178, self.GPIO_BASE-179)
            else:
                need_clear_pin = ()

            for pin in need_clear_pin:
                with open(self.PATH_SYS_GPIO + "/gpio" + str(pin) + "/value") as f:
                    f.read()
        except Exception as e:
            raise

    def _remove_sysfs(self, path_parent, dev_info):
        try:
            with open(path_parent + "/delete_device", 'w') as f:
                f.write(hex(dev_info["address"]))
            self.logger.info("Un-register " + dev_info["name"])
        except FileNotFoundError:
            # Target is not exist
            # To ignore such exception
            pass
        except Exception as e:
            raise

    def init(self):        
        # Create sysfs, export gpio and initial gpio
        for ioexp_name in self.ordered_ioexps:
            try:
                dev_addr = self.IOExpanders[ioexp_name]["address"]
                mux_chanl = self.IOExpanders[ioexp_name]["channel"]
                ioexp = self.IOExpanders[ioexp_name]["ioexp"]

                bus = ioexp.get_channel_bus(mux_chanl)

                # Set commnad config 0 & 1
                bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_CONF, self.IOExpanders[ioexp_name]["config_0"])
                bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_CONF, self.IOExpanders[ioexp_name]["config_1"])
                
                # Set commnad polarity 0 & 1
                bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_POL_INVER, self.IOExpanders[ioexp_name]["polarity_inv_0"])
                bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_POL_INVER, self.IOExpanders[ioexp_name]["polarity_inv_1"])
                
                # Set commnad output 0 & 1
                bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT, self.IOExpanders[ioexp_name]["output_port_0"])
                bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT, self.IOExpanders[ioexp_name]["output_port_1"])

                #if self.IOExpanders[ioexp_name]["parent"] is None:
                #    bus_num = 0
                #else:
                #    bus_num = i2c_mux[self.IOExpanders[ioexp_name]["parent"]].ch_bus[self.IOExpanders[ioexp_name]["channel"]]
                #if ioexp_name == "9539_CPU":
                #    ioexp = PCA9539(self.IOExpanders[ioexp_name], bus_num)
                #else:
                #    ioexp = PCA9535(self.IOExpanders[ioexp_name], bus_num)

                #self.logger.debug("Create sysfs for " + ioexp.name)
                #path_parent = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(ioexp.bus_num)
                #self._create_sysfs(path_parent, ioexp)

                #for i in range(ioexp.pins):
                #    self.logger.info("Export gpio " + str(ioexp.init_cfg[i]["gpio"]) + " for " + ioexp.name + " pin: " + str(i))
                #    self._export_gpio(ioexp, i, ioexp.init_cfg[i]["gpio"])
                #    self._init_gpio(ioexp, i, ioexp.init_cfg[i]["gpio"])

                # 20180312 Issue from diag:
                # After power up, there are false interrupt occur
                # read them to clean
                # Including QSFP: int, SFP: TX_FLT, MODE_ABS, RX_LOS
                bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_IN)
                bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_IN)

            except Exception as e:
                raise
            finally:
                if bus != None:
                    ioexp.close_channel_bus(bus)

    def deinit(self):
        try:
            pass
        except Exception as e:
            raise

    def qsfp_get_presence(self, port_num):
        try:
            mux_chanl = self.IOExpanders["9535_QSFP"]["channel"]
            dev_addr = self.IOExpanders["9535_QSFP"]["address"]
            ioexp = self.IOExpanders["9535_QSFP"]["ioexp"]
            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_IN)

            if port_num == 0:
                # gpio453 IO_0.5 QSFP28_P1_PRSNT_N
                return ((data & 0x20) >> 5)
            else:
                # gpio453 IO_0.4 QSFP28_P2_PRSNT_N
                return ((data & 0x10) >> 4)
                
        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def qsfp_set_lp_mode(self, port_num, cfg):
        try:
            dev_addr = self.IOExpanders["9535_QSFP"]["address"]
            mux_chanl = self.IOExpanders["9535_QSFP"]["channel"]
            ioexp = self.IOExpanders["9535_QSFP"]["ioexp"]
            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT)
            
            # Define output data
            if port_num == 0:
                if cfg == 0:
                    data = data & 0xfd
                else:
                    data = data | 0x02
            else:
                if cfg == 0:
                    data = data & 0xfe
                else:
                    data = data | 0x01
                    
            # Set data
            bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT, data)
            
        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def qsfp_get_lp_mode(self, port_num):
        try:
            dev_addr = self.IOExpanders["9535_QSFP"]["address"]
            mux_chanl = self.IOExpanders["9535_QSFP"]["channel"]
            ioexp = self.IOExpanders["9535_QSFP"]["ioexp"]
            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT)
            
            if port_num == 0:
                # gpio453 IO_0.5 QSFP28_P1_PRSNT_N
                return ((data & 0x02) >> 1)
            else:
                # gpio453 IO_0.4 QSFP28_P2_PRSNT_N
                return ((data & 0x01) >> 0)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def qsfp_reset_port(self, port_num):
        try:
            dev_addr = self.IOExpanders["9535_QSFP"]["address"]
            mux_chanl = self.IOExpanders["9535_QSFP"]["channel"]
            ioexp = self.IOExpanders["9535_QSFP"]["ioexp"]
            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            ori_data = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT)
            
            # define output data
            if port_num == 0:
                data = ori_data & 0xdf
            else:
                data = ori_data & 0xef
                    
            # Set data
            bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT, data)
            time.sleep(2)  # By sff-8436, the execution of a reset is max 2000ms
            bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT, ori_data)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def sfp_get_presence(self, port_num):
        try:
            if port_num <= 15:
                dev_addr = self.IOExpanders["9535_SFP7"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP7"]["channel"]
                ioexp = self.IOExpanders["9535_SFP7"]["ioexp"]
            else:
                dev_addr = self.IOExpanders["9535_SFP8"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP8"]["channel"]
                ioexp = self.IOExpanders["9535_SFP8"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data0 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_IN)
            data1 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_IN)

            if port_num <= 7:
                return ((data0 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 8 and port_num <= 15:
                return ((data1 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 16 and port_num <= 23: 
                return ((data0>> 7-(port_num%8)) & 0x1)
            else:
                return ((data1 >> 7-(port_num%8)) & 0x1)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def sfp_get_rx_lost(self, port_num):
        try:
            if port_num <= 15:
                dev_addr = self.IOExpanders["9535_SFP9"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP9"]["channel"]
                ioexp = self.IOExpanders["9535_SFP9"]["ioexp"]
            else:
                dev_addr = self.IOExpanders["9535_SFP10"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP10"]["channel"]
                ioexp = self.IOExpanders["9535_SFP10"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data0 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_IN)
            data1 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_IN)

            if port_num <= 7:
                return ((data0 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 8 and port_num <= 15:
                return ((data1 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 16 and port_num <= 23: 
                return ((data0 >> 7-(port_num%8)) & 0x1)
            else:
                return ((data1 >> 7-(port_num%8)) & 0x1)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def sfp_get_tx_flt(self, port_num):
        try:
            if port_num <= 15:
                dev_addr = self.IOExpanders["9535_SFP3"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP3"]["channel"]
                ioexp = self.IOExpanders["9535_SFP3"]["ioexp"]
            else:
                dev_addr = self.IOExpanders["9535_SFP4"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP4"]["channel"]
                ioexp = self.IOExpanders["9535_SFP4"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data0 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_IN)
            data1 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_IN)

            if port_num <= 7:
                return ((data0 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 8 and port_num <= 15:
                return ((data1 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 16 and port_num <= 23: 
                return ((data0 >> 7-(port_num%8)) & 0x1)
            else:
                return ((data1 >> 7-(port_num%8)) & 0x1)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def sfp_set_port_rate(self, port_num, cfg):
        try:
            if port_num <= 15:
                dev_addr = self.IOExpanders["9535_SFP5"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP5"]["channel"]
                ioexp = self.IOExpanders["9535_SFP5"]["ioexp"]
            else:
                dev_addr = self.IOExpanders["9535_SFP6"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP6"]["channel"]
                ioexp = self.IOExpanders["9535_SFP6"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data0 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT)
            data1 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT)

            # Define output data
            if port_num <= 7:
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data0
                else:
                    data = (0x1 << 7-(port_num%8)) | data0
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT0_OUT
            elif port_num >= 8 and port_num <= 15:
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data1
                else:
                    data = (0x1 << 7-(port_num%8)) | data1
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT1_OUT
            elif port_num >= 16 and port_num <= 23: 
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data0
                else:
                    data = (0x1 << 7-(port_num%8)) | data0
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT0_OUT
            else:
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data1
                else:
                    data = (0x1 << 7-(port_num%8)) | data1
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT1_OUT

            # Set data
            bus.write_byte_data(dev_addr, pca9535_cmd, data)
            
        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def sfp_get_port_rate(self, port_num):
        try:
            if port_num <= 15:
                dev_addr = self.IOExpanders["9535_SFP5"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP5"]["channel"]
                ioexp = self.IOExpanders["9535_SFP5"]["ioexp"]
            else:
                dev_addr = self.IOExpanders["9535_SFP6"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP6"]["channel"]
                ioexp = self.IOExpanders["9535_SFP6"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data0 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT)
            data1 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT)

            if port_num <= 7:
                return ((data0 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 8 and port_num <= 15:
                return ((data1 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 16 and port_num <= 23: 
                return ((data0 >> 7-(port_num%8)) & 0x1)
            else:
                return ((data1 >> 7-(port_num%8)) & 0x1)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)
                
    def sfp_set_port_status(self, port_num, cfg):
        try:
            bus = SMBus(0)
            
            if port_num <= 15:
                dev_addr = self.IOExpanders["9535_SFP1"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP1"]["channel"]
                ioexp = self.IOExpanders["9535_SFP1"]["ioexp"]
            else:
                dev_addr = self.IOExpanders["9535_SFP2"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP2"]["channel"]
                ioexp = self.IOExpanders["9535_SFP2"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data0 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT)
            data1 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT)

            # Define output data
            if port_num <= 7:
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data0
                else:
                    data = (0x1 << 7-(port_num%8)) | data0
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT0_OUT
            elif port_num >= 8 and port_num <= 15:
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data1
                else:
                    data = (0x1 << 7-(port_num%8)) | data1
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT1_OUT
            elif port_num >= 16 and port_num <= 23: 
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data0
                else:
                    data = (0x1 << 7-(port_num%8)) | data0
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT0_OUT
            else:
                if cfg == 0:
                    data = ((0x1 << 7-(port_num%8)) ^ 0xff) & data1
                else:
                    data = (0x1 << 7-(port_num%8)) | data1
                pca9535_cmd = PCA9535_CMD.PCA9535_REG_PORT1_OUT

            # Set data
            bus.write_byte_data(dev_addr, pca9535_cmd, data)
            
        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)
               
    def sfp_get_port_status(self, port_num):
        try:
            if port_num <= 15:
                dev_addr = self.IOExpanders["9535_SFP1"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP1"]["channel"]
                ioexp = self.IOExpanders["9535_SFP1"]["ioexp"]
            else:
                dev_addr = self.IOExpanders["9535_SFP2"]["address"]
                mux_chanl = self.IOExpanders["9535_SFP2"]["channel"]
                ioexp = self.IOExpanders["9535_SFP2"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data0 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT)
            data1 = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT1_OUT)

            if port_num <= 7:
                return ((data0 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 8 and port_num <= 15:
                return ((data1 >> 7-(port_num%8)) & 0x1)
            elif port_num >= 16 and port_num <= 23: 
                return ((data0 >> 7-(port_num%8)) & 0x1)
            else:
                return ((data1 >> 7-(port_num%8)) & 0x1)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)
                
    def bmc_reset_set(self, input_target):
        try:
            dev_addr = self.IOExpanders["9535_BRD"]["address"]
            mux_chanl = self.IOExpanders["9535_BRD"]["channel"]
            ioexp = self.IOExpanders["9535_BRD"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT)
            config = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_CONF)
            
            if input_target == 'all':
                sys_bit = self.ResetMaskConst["SYS"]["bit"]
                ddr_bit = self.ResetMaskConst["DDR3"]["bit"]
                
                data = data & ~((1<<sys_bit) | (1<<ddr_bit))
                config = config & ~((1<<sys_bit) | (1<<ddr_bit))
            else:
                for key, value in self.ResetMaskConst.items():     
                    if input_target == key:
                        bit = value["bit"]
                        name = value["name"]
                        default_value = value["default"]
                        break
                            
                data = data & ~(1<<bit)
                config = config & ~(1<<bit)
            
            # Set config (input -> output)
            bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_CONF, config)
            
            # Set data
            bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT, data)
            
        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)
    
    def rov_get_voltage(self):
        try:
            dev_addr = self.IOExpanders["9535_BRD"]["address"]
            mux_chanl = self.IOExpanders["9535_BRD"]["channel"]
            ioexp = self.IOExpanders["9535_BRD"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)

            # Get data
            data = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_IN)
                
            # Ignore the left 4 bit
            data = data & 0x07
            
            #return Rov valtage
            if data < len(self.ROV_List):
                return self.ROV_List[data]
            else:
                self.logger.error("ROV value " + str(data) + " is not in list")
                raise ValueError("ROV value " + str(data) + " is not in list")
            
        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)

    def rov_set_voltage(self, rov):
        try:
            dev_addr = self.IOExpanders["9535_BRD"]["address"]
            mux_chanl = self.IOExpanders["9535_BRD"]["channel"]
            ioexp = self.IOExpanders["9535_BRD"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)

            # Set voltage
            setok = 0
            for element in self.TPS53667_voltage:
                if element["rov"] == rov:
                    #0x21 is TPS53667's VOUT register
                    bus.write_word_data(self.I2C_ADDR_TPS53667, 0x21, element["vol"])
                    setok = 1
                    self.logger.info("Set ROV voltage as " + rov)

            if setok == 0:
                self.logger.error("Can not set ROV voltage as " + rov)
                raise ValueError("Can not set ROV voltage as " + rov)

        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)
            
    def bmc_reset_unset(self, input_target):
        try:
            bus = SMBus(0)
            
            dev_addr = self.IOExpanders["9535_BRD"]["address"]
            mux_chanl = self.IOExpanders["9535_BRD"]["channel"]
            ioexp = self.IOExpanders["9535_BRD"]["ioexp"]

            bus = ioexp.get_channel_bus(mux_chanl)
            
            # Get data
            data = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT)
            config = bus.read_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_CONF)

            if input_target == 'all':
                sys_bit = self.ResetMaskConst["SYS"]["bit"]
                ddr_bit = self.ResetMaskConst["DDR3"]["bit"]
                
                data = data | ((1<<sys_bit) | (1<<ddr_bit))
                config = config | ((1<<sys_bit) | (1<<ddr_bit))
            else:
                for key, value in self.ResetMaskConst.items():     
                    if input_target == key:
                        bit = value["bit"]
                        name = value["name"]
                        default_value = value["default"]
                        break
                            
                data = data | (1<<bit)
                config = config | (1<<bit)
                
            # Set data
            bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_OUT, data)
            
            # Set config (output -> input)
            bus.write_byte_data(dev_addr, PCA9535_CMD.PCA9535_REG_PORT0_CONF, config)
            
        except Exception as e:
            raise
            
        finally:
            if bus != None:
                ioexp.close_channel_bus(bus)
