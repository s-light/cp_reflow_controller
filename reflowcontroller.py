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
            "auto_dim_display": 1,
            "display_brightness": 0.1,
        },
        "colors": {
            "off": (0, 0, 0),
            "done": (50, 255, 0),
            "warn": (255, 255, 0),
            "error": (255, 0, 0),
        },
    }
    config = {}

    def __init__(self):
        super(ReflowController, self).__init__()
        print("ReflowController")
        print("  https://github.com/s-light/cp_reflow_controller")
        print(42 * "*")
        self.load_profiles()
        self.load_config()
        # select stored profile
        if self.config["profile"] in self.profiles_names:
            self.profile_selected = self.profiles[self.config["profile"]]
        self.setup_hw()
        self.setup_colors()
        # setup things - run last as it uses other things..
        self.states_setup()

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
        self.profiles_names.sort()
        self.profile_selected = self.profiles[self.profiles_names[0]]

        # get_current_step

    # def profile_get_by_name(self, title):
    #     index = self.profiles_names.index(name)
    #     return self.profiles[index]
    #
    # def profile_get_by_name(self, name):
    #     # index = self.profiles_names.index(name)
    #     return self.profiles[name]

    def profile_get_next_name(self):
        print("self.profile_selected.__name__", self.profile_selected.__name__)
        index_current = self.profiles_names.index(self.profile_selected.__name__)
        index_new = index_current + 1
        if index_new >= len(self.profiles_names):
            index_new = 0
        return self.profiles_names[index_new]

    def profile_select_next(self):
        self.profile_selected = self.profiles[self.profile_get_next_name()]

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

    @property
    def heating(self):
        return self._heating.value

    @heating.setter
    def heating(self, value):
        self._heating.value = value
        return self._heating.value

    def setup_hw(self):
        self.spi = board.SPI()
        self.max31855_cs = digitalio.DigitalInOut(self.get_pin("max31855_cs_pin"))
        self.max31855 = adafruit_max31855.MAX31855(self.spi, self.max31855_cs)

        self._heating = digitalio.DigitalInOut(self.get_pin("heating_pin"))
        self._heating.direction = digitalio.Direction.OUTPUT
        self.temperature = None
        self.temperature_reference = None

        # https://circuitpython.readthedocs.io/projects/pybadger/en/latest/api.html
        pybadger.auto_dim_display(delay=self.config["hw"]["auto_dim_display"])
        pybadger.brightness = self.config["hw"]["display_brightness"]

        self.pixels = pybadger.pixels
        self.buttons = PyBadgeButtons()

    def pixels_all(self, color):
        for index, pixel in enumerate(self.pixels):
            self.pixels[index] = color

    def setup_colors(self):
        self.colors = self.config["colors"]

    ##########################################
    # state handling

    def switch_to_state(self, state):
        """switch to new state."""
        state_name_old = None
        if self.state_current:
            self.state_current.active = False
            state_name_old = self.state_current.name
        self.state_current = self.states[state]
        self.state_current.active = True
        state_name_new = self.state_current.name
        print("changed state from '{}' to '{}'".format(state_name_old, state_name_new))
        self.state_current.update()

    # standby
    def states_standby_enter(self):
        self.heating = False

    def states_standby_update(self):
        pass

    def states_standby_leave(self):
        pass

    # calibrate
    # def states_calibrate_enter(self):
    #     pass
    #
    # def states_calibrate_update(self):
    #     pass
    #
    # def states_calibrate_leave(self):
    #     self.switch_to_state("standby")

    # reflow_done
    def states_reflow_prepare_update(self):
        if self.buttons.start.rose:
            self.switch_to_state("reflow")

    # reflow_done
    def states_reflow_done_update(self):
        if self.buttons.select.rose:
            self.switch_to_state("standby")

    def states_reflow_done_leave(self):
        self.pixels_all((0, 0, 0))

    def states_setup(self):
        self.state_current = {}
        self.states = {
            # "standby": State(name="standby", enter=(lambda: pass),),
            "standby": State(
                name="standby",
                enter=self.states_standby_enter,
                update=self.states_standby_update,
                leave=self.states_standby_leave,
            ),
            "calibrate": State(
                name="calibrate",
                # enter=self.states_calibrate_enter,
                # update=self.states_calibrate_update,
                # leave=self.states_calibrate_leave,
            ),
            "reflow_prepare": State(
                name="reflow_prepare",
                # enter=self.states_reflow_prepare_enter,
                update=self.states_reflow_prepare_update,
                # leave=self.states_reflow_prepare_leave,
            ),
            "reflow": State(
                name="reflow",
                enter=self.reflowcycle_start,
                update=self.reflowcycle_update,
                leave=self.reflowcycle_finished,
            ),
            "reflow_done": State(
                name="reflow_done",
                # enter=self.states_reflow_done_enter,
                update=self.states_reflow_done_update,
                enter=self.states_reflow_done_leave,
                # leave=lambda: self.switch_to_state("standby"),
            ),
        }
        self.switch_to_state("standby")

    ##########################################
    # reflow

    def menu_reflowcycle_start(self):
        self.switch_to_state("reflow_prepare")

    def menu_reflowcycle_stop(self):
        self.switch_to_state("standby")

    # handling actuall reflow process
    def reflowcycle_start(self):
        self.profile_selected.start()

    def reflowcycle_update(self):
        # handle heating with currently selected profile..

        # handle heating
        temp_target = self.profile_selected.temp_get_current_proportional_target()
        # self.heating = False
        # TODO: s-light: Implement heating control
        # maybe as PID
        # maybe just as simple hysteresis check
        # with prelearned timing..

        if self.profile_selected.step_next_check_and_do() is None:
            # we reached the end of the reflow process
            self.switch_to_state("reflow_done")

    def reflowcycle_finished(self):
        self.heating = False
        self.pixels_all(self.color_done)

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
        profile_list = ""
        # for name, profile in self.profiles.items():
        #     profile_list += "  {}\n".format(profile.title)
        # ^--> random order..
        for name in self.profiles_names:
            current = ""
            if self.profiles[name] is self.profile_selected:
                current = "*"
            profile_list += "  {: 1}{}\n".format(
                current, self.profiles[name].title_short
            )
        print(
            "you can set some options:\n"
            "- 'p' select next profil\n"
            "{profile_list}"
            "- 'calibrate'\n"
            "- 'start' reflow cycle\n"
            "- 'stop'  reflow cycle\n"
            "".format(
                profile_list=profile_list,
            ),
            end="",
        )

    def check_input(self):
        """Check Input."""
        input_string = input()
        if "calibrate" in input_string:
            self.calibrate()
        if "start" in input_string:
            self.menu_reflowcycle_start()
        if "stop" in input_string:
            self.menu_reflowcycle_stop()
        if "p" in input_string:
            self.profile_select_next()
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
            # print("Button start")
            if self.state_current.name == "standby":
                self.switch_to_state("reflow_prepare")
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
        running = True
        while running:
            try:
                self.main_loop()
            except KeyboardInterrupt as e:
                print("KeyboardInterrupt - Stop Program.", e)
                running = False


##########################################
