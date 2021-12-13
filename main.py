#!/usr/bin/env python3
# coding=utf-8

"""
reflow controller.

HW: Adafruit PyBadge
"""


# import os
import sys
from reflowcontroller import ReflowController

##########################################
# globals

##########################################


def main():
    """Main handling."""
    print(42 * "*")
    print("Python Version: " + sys.version)
    print(42 * "*")
    myReflowController = ReflowController()
    print("profile_selected: ", myReflowController.profile_selected)
    myReflowController.run()


##########################################
if __name__ == "__main__":
    main()

##########################################
