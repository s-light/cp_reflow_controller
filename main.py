#!/usr/bin/env python3
# coding=utf-8

"""
reflow controller.

HW: Adafruit PyBadge
"""


# import os
import sys

import json

import time
import board
import digitalio
import adafruit_max31855

from configdict import extend_deep

import profiles as myprofiles

##########################################
# globals


##########################################
# functions


##########################################
# main class


class ReflowController(object):
    """ReflowController."""

    spi = board.SPI()
    cs = digitalio.DigitalInOut(board.D5)
    max31855 = adafruit_max31855.MAX31855(spi, cs)

    heating = digitalio.DigitalInOut(board.D9)
    heating.direction = digitalio.Direction.OUTPUT

    profiles_names = []
    profiles = []

    config_defaults = {
        "profile": "?",
        "calibration": {"temperature": 30, "duration": 37},
    }
    config = {}

    def __init__(self):
        super(ReflowController, self).__init__()
        print("ReflowController")
        print("  https://github.com/s-light/cp_reflow_controller")
        print(42 * "*")
        # self.arg = arg
        self.load_profiles()
        self.load_config()
        # select stored profile
        if self.config["profile"] in self.profiles_names:
            self.profile_selected = self.profiles[self.config["profile"]]

    def load_profiles(self):
        self.profiles = {}
        # self.profiles_infos = myprofiles.load_all_submodules()
        # for profile_name, profile in self.profiles_infos.items():
        #     print(profile_name)
        (
            self.profiles_infos,
            self.profiles,
        ) = myprofiles.load_all_submodules_and_instantiate_all_classes()
        # print(
        #     "load_profiles:\n"
        #     "  profiles: {}\n"
        #     # "  infos: {}"
        #     "".format(
        #         self.profiles,
        #         # self.profiles_infos,
        #     )
        # )
        print("load_profiles:")
        for p_name, profile in self.profiles.items():
            print("  '{}': {}".format(p_name, profile))
        print()
        self.profiles_names = list(self.profiles.keys())
        self.profile_selected = self.profiles[self.profiles_names[0]]

        # get_current_step

    def load_config(self, filename="/config.json"):
        self.config = {}
        try:
            with open(filename, mode="r") as configfile:
                self.config = json.load(configfile)
                configfile.close()
        except OSError as e:
            # print(dir(e))
            # print(e.errno)
            if e.errno == 2:
                print(e)
                # print(e.strerror)
            else:
                raise e
        # extend with default config - thisway it is safe to use ;-)
        extend_deep(self.config, self.config_defaults.copy())

    def calibration(self):
        """calibration routin."""

        while True:
            # self.heating.value = not self.heating.value
            # time.sleep(1)
            self.heating.value = True
            time.sleep(0.2)
            self.heating.value = False
            time.sleep(1)


##########################################


def main():
    """Main handling."""
    print(42 * "*")
    print("Python Version: " + sys.version)
    print(42 * "*")
    myReflowController = ReflowController()
    print("profile_selected: ", myReflowController.profile_selected)


##########################################
if __name__ == "__main__":

    main()

##########################################
