#!/usr/bin/env python3
# coding=utf-8

"""
debounced buttons for PyBadge

HW: Adafruit PyBadge
"""

from adafruit_pybadger import pybadger
from adafruit_debouncer import Debouncer

##########################################
# main class


class PyBadgeButtons(object):
    """PyBadgeButtons - debounced."""

    def __init__(self):
        super(PyBadgeButtons, self).__init__()
        self.setup_hw()

        # https://learn.adafruit.com/debouncer-library-python-circuitpython-buttons-sensors/advanced-debouncing
        self.a = Debouncer(lambda: pybadger.button.a)
        self.b = Debouncer(lambda: pybadger.button.b)
        self.up = Debouncer(lambda: pybadger.button.up)
        self.down = Debouncer(lambda: pybadger.button.down)
        self.left = Debouncer(lambda: pybadger.button.left)
        self.right = Debouncer(lambda: pybadger.button.right)
        self.start = Debouncer(lambda: pybadger.button.start)
        self.select = Debouncer(lambda: pybadger.button.select)

        self.buttons = {}
        self.buttons["a"] = self.a
        self.buttons["b"] = self.b
        self.buttons["up"] = self.up
        self.buttons["down"] = self.down
        self.buttons["left"] = self.left
        self.buttons["right"] = self.right
        self.buttons["start"] = self.start
        self.buttons["select"] = self.select

    def update(self):
        """update all debouncer objects."""
        for button_name, button in self.buttons.items():
            button.update()
