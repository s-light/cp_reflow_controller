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
    wait_duration = 5
    step_duration = 0.5
    for index in range(wait_duration * step_duration):
        print(".", end="")
        time.sleep(step_duration / wait_duration)
    print("")
    print(42 * "*")
    print("Python Version: " + sys.version)
    print("board: " + board.board_id)
    print(42 * "*")
    myReflowController = ReflowController()
    myReflowController.run()


##########################################
if __name__ == "__main__":
    main()

##########################################
