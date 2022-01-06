#!/usr/bin/env python3
# coding=utf-8

"""
reflow controller.

HW: Adafruit PyBadge
"""


# import os
import time
import sys
import board
from reflowcontroller import ReflowController

##########################################
# globals

##########################################


def main():
    """Main handling."""
    for index in range(10):
        print(".", end="")
        time.sleep(0.5 / 10)
    print("")
    print(42 * "*")
    print("Python Version: " + sys.version)
    print("board: " + board.board_id)
    print(42 * "*")
    myReflowController = ReflowController()
    myReflowController.print("profile_selected: ", myReflowController.profile_selected)
    myReflowController.run()


##########################################
if __name__ == "__main__":
    main()

##########################################
