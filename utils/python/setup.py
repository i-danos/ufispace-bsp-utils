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
from setuptools import setup
from distutils.core import setup
setup(name='SIAD_BSP_UTIL',
      version='3.0.13',
      packages=['','timing','common','const','cpld','eeprom','gpio','i2c_mux','protocol','timing.ubx'],
      install_requires=['pyusb', 'portio', 'smbus', 'serial']
      )
