#!/usr/bin/env python3
# coding=utf-8

"""
reflow controller.

HW: Adafruit PyBadge
"""


# import os
import sys

import profiles

##########################################
# globals

profiles_list = []

##########################################
# functions


##########################################


def main():
    """Main handling."""
    print(42 * "*")
    print("Python Version: " + sys.version)
    print(42 * "*")

    global profiles_list
    profiles_list = profiles.load_all_modules()

    for profile in profiles_list:
        print(profile)


##########################################
if __name__ == "__main__":

    main()

##########################################
