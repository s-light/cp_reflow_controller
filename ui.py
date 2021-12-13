#!/usr/bin/env python3
# coding=utf-8

"""
all things UI:
display drawing and button handling

HW: Adafruit PyBadge
"""


# import os
# import sys

import time
import board
import supervisor
from adafruit_pybadger import pybadger
from buttons import PyBadgeButtons
import adafruit_max31855

from configdict import extend_deep

import profiles as myprofiles

##########################################
# functions


##########################################
# main classe


class ReflowControllerDisplay(object):
    """ReflowControllerDisplay."""

    config_defaults = {
        "display": {
            "max31855_cs_pin": "D5",
        },
    }
    config = {}

    def __init__(self, reflowcontroller):
        super(ReflowControllerDisplay, self).__init__()
        # print("ReflowControllerDisplay")
        self.reflowcontroller = reflowcontroller
        self.config = self.reflowcontroller.config
        self.setup_hw()

    def setup_hw(self):
        # https://circuitpython.readthedocs.io/projects/pybadger/en/latest/api.html
        pybadger.auto_dim_display(delay=self.config["hw"]["auto_dim_display"])

    ##########################################
    # main handling
    def updatae(self):
        # self.buttons.update()
        # if self.buttons.a.rose:
        #     print("Button A")
        # if self.buttons.b.rose:
        #     print("Button B")
        # if self.buttons.up.rose:
        #     print("Button up")
        # if self.buttons.down.rose:
        #     print("Button down")
        # if self.buttons.left.rose:
        #     print("Button left")
        # if self.buttons.right.rose:
        #     print("Button right")
        # if self.buttons.start.rose:
        #     print("Button start")
        # if self.buttons.select.rose:
        #     print("Button select")
        pass


##########################################
