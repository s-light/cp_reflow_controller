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
import random
import gc
import board
import digitalio

import adafruit_max31855

from configdict import extend_deep

from state import State

import ui

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
        },
        # all sub defaults for the UI are defined there.
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
        self.setup_states()
        self.setup_ui()

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
        # ProfileCalibration is an internal profile not available as user selection.
        self.profiles_names.remove("ProfileCalibration")
        self.profile_selected = self.profiles[self.profiles_names[0]]

        # get_current_step

    @property
    def profile_selected(self):
        return self._profile_selected

    @profile_selected.setter
    def profile_selected(self, profile):
        self._profile_selected = profile
        if hasattr(self, "ui"):
            self.ui.profile_selected = self._profile_selected
        return self._profile_selected

    # def profile_get_by_name(self, title):
    #     index = self.profiles_names.index(name)
    #     return self.profiles[index]
    #
    # def profile_get_by_name(self, name):
    #     # index = self.profiles_names.index(name)
    #     return self.profiles[name]

    def profile_get_next_name(self):
        # print("self.profile_selected.__name__", self.profile_selected.__name__)
        try:
            index_current = self.profiles_names.index(self.profile_selected.__name__)
        except ValueError as e:
            if "object not in sequence" in e.msg:
                index_current = 99
            else:
                raise e
        index_new = index_current + 1
        if index_new >= len(self.profiles_names):
            index_new = 0
        return self.profiles_names[index_new]

    def profile_select_next(self):
        self.profile_selected = self.profiles[self.profile_get_next_name()]

    def profile_select_calibration(self):
        self.profile_selected = self.profiles["ProfileCalibration"]

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
        if self._heating.value != value:
            self._heating.value = value
            # something changed!
            self.ui.show_heater_state(value)
        return self._heating.value

    def setup_hw(self):
        self.spi = board.SPI()
        self.max31855_cs = digitalio.DigitalInOut(self.get_pin("max31855_cs_pin"))
        self.max31855 = adafruit_max31855.MAX31855(self.spi, self.max31855_cs)

        self._heating = digitalio.DigitalInOut(self.get_pin("heating_pin"))
        self._heating.direction = digitalio.Direction.OUTPUT
        self.temperature = None
        self.temperature_reference = None
        self.temperature_changed = False
        self.temperature_difference = None
        self.temp_current_proportional_target = None

    def setup_ui(self):
        self.ui = ui.ReflowControllerUI(reflowcontroller=self)

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
        print("rc state: '{}' -> '{}'".format(state_name_old, state_name_new))
        self.state_current.update()

    def setup_states(self):
        self.state_current = {}
        self.states = {
            "standby": State(
                name="standby",
                enter=self.states_standby_enter,
                update=self.states_standby_update,
                leave=self.states_standby_leave,
            ),
            "calibrate": State(
                name="calibrate",
                enter=self.calibrate_start,
                update=self.calibrate_update,
                leave=self.calibrate_finished,
            ),
            "reflow": State(
                name="reflow",
                enter=self.reflow_start,
                update=self.reflow_update,
                leave=self.reflow_finished,
            ),
        }
        self.switch_to_state("standby")

    # standby
    def states_standby_enter(self):
        self.heating = False

    def states_standby_update(self):
        pass

    def states_standby_leave(self):
        pass

    ##########################################
    # heating managment

    def handle_heating(self):
        """Handle heating."""
        if self.temperature and self.temp_current_proportional_target:
            # temp = self.temperature
            diff = self.temperature_difference
            # target = self.temp_current_proportional_target
            hysteresis = 2
            if diff > hysteresis:
                self.heating = True
            else:
                self.heating = False
            # TODO: s-light: Implement heating control
            # maybe as PID
            # maybe just as simple hysteresis check
            # with prelearned timing..
            pass
        else:
            self.heating = False

    ##########################################
    # reflow

    # handling actuall reflow process
    def reflow_start(self):
        self.profile_selected.start()

    def reflow_update(self):
        # handle heating with currently selected profile..
        self.handle_heating()

        profile_running = self.profile_selected.step_next_check_and_do()
        # print("profile_running", profile_running)
        if profile_running is False:
            # we reached the end of the reflow process
            self.switch_to_state("standby")
        # if self.profile_selected.step_next_check_and_do() is False:
        #     # we reached the end of the reflow process
        #     self.switch_to_state("reflow_done")

    def reflow_finished(self):
        self.heating = False
        self.ui.switch_to_state("reflow_done")

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

    # calibrate
    def calibrate_start(self):
        self.profile_selected.start()

    def calibrate_update(self):
        # TODO: s-light: implement calibration routine
        self.reflow_update()

    def calibrate_finished(self):
        self.heating = False
        self.ui.switch_to_state("calibration_done")

    ##########################################
    # main handling

    def temperature_update(self):
        self.temperature = None
        self.temperature_reference = None
        self.temp_current_proportional_target = None
        self.temperature_difference = None
        self.temperature_changed = False
        # try:
        #     temperature_temp = self.max31855.temperature
        #     temperature_reference_temp = self.max31855.reference_temperature
        # except RuntimeError as e:
        #     print(e)
        #     if "short circuit to ground" in e:
        #         pass
        #     elif "short circuit to power" in e:
        #         pass
        #     elif "faulty reading" in e:
        #         pass
        #     elif "thermocouple not connected" in e:
        #         pass
        #     else:
        #         raise e
        # else:
        #     if self.profile_selected:
        #         # temp_target = self.profile_selected.temp_current_proportional_target
        #         self.temp_current_proportional_target = (
        #             self.profile_selected.temp_current_proportional_target_get()
        #         )
        #
        #     if temperature_temp != self.temperature:
        #         self.temperature = temperature_temp
        #         self.temperature_reference = temperature_reference_temp
        #         self.temperature_changed = True
        #         # print("Temperature: {:.02f}°C ".format(self.temperature))
        #
        #     if self.temp_current_proportional_target:
        #         self.temperature_difference = (
        #             self.temp_current_proportional_target - self.temperature
        #         )

        # fake temp
        # temp_target = self.profile_selected.temp_current_proportional_target
        self.temp_current_proportional_target = (
            self.profile_selected.temp_current_proportional_target_get()
        )
        if self.temp_current_proportional_target:
            temp_current_fake = self.temp_current_proportional_target + random.randint(
                -10, 20
            )
        else:
            temp_current_fake = 0
        # clamp to range
        temp_current_fake = max(0, temp_current_fake)
        temp_current_fake = min(self.profile_selected.max_temperatur, temp_current_fake)
        if temp_current_fake != self.temperature:
            self.temperature = temp_current_fake
            self.temperature_reference = 20
            # self.temperature_changed = True

        if self.temp_current_proportional_target:
            self.temperature_difference = (
                self.temp_current_proportional_target - self.temperature
            )

    def main_loop(self):
        gc.collect()
        self.temperature_update()
        self.state_current.update()
        self.ui.update()
        # self.check_buttons()
        # if supervisor.runtime.serial_bytes_available:
        #     self.check_input()

    def run(self):
        print(42 * "*")
        print("run")
        # if supervisor.runtime.serial_connected:
        self.ui.print_help()
        running = True
        while running:
            try:
                self.main_loop()
            except KeyboardInterrupt as e:
                print("KeyboardInterrupt - Stop Program.", e)
                running = False


##########################################
