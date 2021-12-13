#!/usr/bin/env python3
# coding=utf-8

"""
reflow controller.

HW: Adafruit PyBadge
"""


# import os
# import sys

import json

import time
import board
import digitalio
import supervisor
from adafruit_pybadger import pybadger
from buttons import PyBadgeButtons
import adafruit_max31855

from configdict import extend_deep

from state import State

import profiles as myprofiles

##########################################
# functions


##########################################
# main classe


class ReflowController(object):
    """ReflowController."""

    config_defaults = {
        "profile": "?",
        "calibration": {"temperature": 30, "duration": 37},
        "hw": {
            "max31855_cs_pin": "D5",
            "heating_pin": "D9",
            "auto_dim_display": 10,
        },
    }
    config = {}

    spi = None
    max31855_cs = None
    max31855 = None

    heating = None

    profiles_names = []
    profiles = []

    temperature = None
    temperature_reference = None

    states = None

    def __init__(self):
        super(ReflowController, self).__init__()
        print("ReflowController")
        print("  https://github.com/s-light/cp_reflow_controller")
        print(42 * "*")
        self.load_profiles()
        self.load_config()
        self.states_setup()
        # select stored profile
        if self.config["profile"] in self.profiles_names:
            self.profile_selected = self.profiles[self.config["profile"]]
        self.setup_hw()

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

    def get_pin(self, pin_name):
        board_pin_name = self.config["hw"][pin_name]
        return getattr(board, board_pin_name)

    def setup_hw(self):
        self.spi = board.SPI()
        self.max31855_cs = digitalio.DigitalInOut(self.get_pin("max31855_cs_pin"))
        self.max31855 = adafruit_max31855.MAX31855(self.spi, self.max31855_cs)

        self.heating = digitalio.DigitalInOut(self.get_pin("heating_pin"))
        self.heating.direction = digitalio.Direction.OUTPUT

        # https://circuitpython.readthedocs.io/projects/pybadger/en/latest/api.html
        pybadger.auto_dim_display(delay=self.config["hw"]["auto_dim_display"])

        self.pixels = pybadger.pixels
        self.buttons = PyBadgeButtons()

    ##########################################
    # state handling

    def switch_to_state(self, state):
        """switch to new state."""
        self.state_current.active = False
        self.state_current = self.states[state]
        self.state_current.active = True
        self.state_current.update()

    def states_standby_enter(self):
        pass

    def states_standby_leave(self):
        pass

    def states_standby_update(self):
        pass

    def states_calibrate_enter(self):
        pass

    def states_calibrate_leave(self):
        self.switch_to_state("standby")

    def states_calibrate_update(self):
        pass

    def states_reflow_enter(self):
        pass

    def states_reflow_leave(self):
        self.switch_to_state("standby")

    def states_reflow_update(self):
        pass

    def states_setup(self):
        self.states = {
            # "standby": State(name="standby", enter=(lambda: pass),),
            "standby": State(
                name="standby",
                enter=self.states_standby_enter,
                leave=self.states_standby_leave,
                update=self.states_standby_update,
            ),
            "calibrate": State(
                name="calibrate",
                enter=self.states_calibrate_enter,
                leave=self.states_calibrate_leave,
                update=self.states_calibrate_update,
            ),
            "reflow": State(
                name="reflow",
                enter=self.states_reflow_enter,
                leave=self.states_reflow_leave,
                update=self.states_reflow_update,
            ),
        }
        self.switch_to_state("standby")

    ##########################################
    # reflow

    def reflowcycle_update(self):
        # handle heating with currently selected profile..

        if self.profile_selected.step_next_check_and_do() is None:
            # we reached the end of the reflow process
            pass

    ##########################################
    # calibration functions
    def calibration(self):
        """calibration routin."""

        # for duration in range(60):
        for duration in range(10):
            # self.heating.value = not self.heating.value
            # time.sleep(1)
            self.heating.value = True
            time.sleep(0.2)
            self.heating.value = False
            time.sleep(0.8)

    ##########################################
    # menu

    def print_help(self):
        """Print Help."""
        print(
            "you can set some options:\n"
            "- select next profil: 'p' ({profile_selected})\n"
            "- start calibration cycle: 'calibrate'\n"
            "- start reflow cycle: 'start'\n"
            "- stop reflow cycle: 'stop'\n"
            "".format(
                # profile_selected=self.profile_selected.__name__,
                profile_selected=self.profile_selected.title,
            )
        )

    def check_input(self):
        """Check Input."""
        input_string = input()
        if "calibrate" in input_string:
            self.calibrate()
        if "start" in input_string:
            self.reflow_cycle_start()
        if "stop" in input_string:
            self.reflow_cycle_stop()
        if "p" in input_string:
            self.profile_select_next(input_string)
        # prepare new input
        self.print_help()
        print(">> ", end="")

    @staticmethod
    def input_parse_pixel_set(input_string):
        """parse pixel_set."""
        # row = 0
        # col = 0
        # value = 0
        # sep_pos = input_string.find(",")
        # sep_value = input_string.find(":")
        # try:
        #     col = int(input_string[1:sep_pos])
        # except ValueError as e:
        #     print("Exception parsing 'col': ", e)
        # try:
        #     row = int(input_string[sep_pos + 1 : sep_value])
        # except ValueError as e:
        #     print("Exception parsing 'row': ", e)
        # try:
        #     value = int(input_string[sep_value + 1 :])
        # except ValueError as e:
        #     print("Exception parsing 'value': ", e)
        # pixel_index = 0
        pass

    ##########################################
    # main handling

    def temperature_update(self):
        try:
            temperature_temp = self.max31855.temperature
            temperature_reference_temp = self.max31855.reference_temperature
        except RuntimeError as e:
            self.temperature = None
            self.temperature_reference = None
            print(e)
            if "short circuit to ground" in e:
                pass
            elif "short circuit to power" in e:
                pass
            elif "faulty reading" in e:
                pass
            elif "thermocouple not connected" in e:
                pass
            else:
                raise e
        else:
            if temperature_temp != self.temperature:
                self.temperature = temperature_temp
                self.temperature_reference = temperature_reference_temp
                print("Temperature: {:.02f}°C ".format(self.temperature))

    def check_buttons(self):
        self.buttons.update()
        if self.buttons.a.rose:
            print("Button A")
        if self.buttons.b.rose:
            print("Button B")
        if self.buttons.up.rose:
            print("Button up")
        if self.buttons.down.rose:
            print("Button down")
        if self.buttons.left.rose:
            print("Button left")
        if self.buttons.right.rose:
            print("Button right")
        if self.buttons.start.rose:
            print("Button start")
        if self.buttons.select.rose:
            print("Button select")

    def main_loop(self):
        self.temperature_update()
        self.state_current.update()
        self.check_buttons()
        if supervisor.runtime.serial_bytes_available:
            self.check_input()

    def run(self):
        print(42 * "*")
        print("loop")
        if supervisor.runtime.serial_connected:
            self.print_help()
        while True:
            self.main_loop()


##########################################
