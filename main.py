#!/usr/bin/env python3
# coding=utf-8

"""
reflow controller.

HW: Adafruit PyBadge
"""


# import os
import sys

import time
import board
import digitalio
import adafruit_max31855

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

    def __init__(self):
        super(ReflowController, self).__init__()
        # self.arg = arg
        self.load_profiles()

    def load_profiles(self):
        self.profiles = {}
        # self.profiles_infos = myprofiles.load_all_submodules()
        # for profile_name, profile in self.profiles_infos.items():
        #     print(profile_name)
        (
            self.profiles_infos,
            self.profiles,
        ) = myprofiles.load_all_submodules_and_instantiate_all_classes()
        print(
            "load_profiles:\n"
            "  profiles: {}\n"
            # "  infos: {}"
            "".format(
                self.profiles,
                # self.profiles_infos,
            )
        )
        self.profiles_names = list(self.profiles.keys())
        self.profile_selected = self.profiles[self.profiles_names[0]]

        # get_current_step

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
    # print("profiles_names", myReflowController.profiles_names)
    print("profile[0] name", myReflowController.profiles_names[0])
    print(myReflowController.profile_selected)


##########################################
if __name__ == "__main__":

    main()

##########################################
