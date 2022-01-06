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

# import random
import gc
import board
import digitalio
import pwmio

import adafruit_max31855

from configdict import extend_deep

import helper

from state import State

import pid
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
            "max31855_cs_pin": "D4",
            "heater_pin": "D12",
        },
        "pid": {
            "update_intervall": 0.1,
            "P_gain": 10.0,
            "I_gain": 0.1,
            "D_gain": 1.0,
        },
        # all sub defaults for the UI are defined there.
    }
    config = {}

    def __init__(self):
        super(ReflowController, self).__init__()
        # self.print is later replaced by the ui module.
        self.print = lambda *args: print(*args)

        self.print("ReflowController")
        self.print("  https://github.com/s-light/cp_reflow_controller")
        self.print(42 * "*")
        self.load_profiles()
        self.load_config()
        # select stored profile
        if self.config["profile"] in self.profiles_names:
            self.profile_selected = self.profiles[self.config["profile"]]
        self.setup_hw()
        self.heater_setup()
        self.setup_states()
        self.setup_ui()

    def load_profiles(self):
        self.profiles = {}
        # self.profiles_infos = myprofiles.load_all_submodules()
        # for profile_name, profile in self.profiles_infos.items():
        #     self.print(profile_name)
        (
            self.profiles_infos,
            self.profiles,
        ) = myprofiles.load_all_submodules_and_instantiate_all_classes()
        # self.print(
        #     "load_profiles:\n"
        #     "  profiles: {}\n"
        #     # "  infos: {}"
        #     "".format(
        #         self.profiles,
        #         # self.profiles_infos,
        #     )
        # )
        self.print("load_profiles:")
        for p_name, profile in self.profiles.items():
            self.print("  '{}': {}".format(p_name, profile))
        self.print()
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
        # self.print("self.profile_selected.__name__", self.profile_selected.__name__)
        try:
            index_current = self.profiles_names.index(self.profile_selected.__name__)
        except ValueError as e:
            if "object not in sequence" in e.args[0]:
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
            # self.print(dir(e))
            # self.print(e.errno)
            if e.errno == 2:
                self.print(e)
                # self.print(e.strerror)
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

        self.temperature = None
        self.temperature_reference = None
        self.temperature_changed = False
        self.temperature_change_last = False
        self.temperature_list = []

        self.temperature_update()
        # A6 is connected to meassure battery voltage
        # analogio.AnalogIn(board.A6)

    def setup_ui(self):
        self.ui = ui.ReflowControllerUI(reflowcontroller=self)

    ##########################################
    # helper

    ##########################################
    # heating managment
    # self.heater_target is the api to set and get the current target value for the pid controller
    # self.heater_pwm is the mostly internal direct access to the heater output in 0..1 format
    # self._heater_pwm is the raw pwm output

    def pid_update_output(self, value):
        # value is in the range of 0.0 .. 1.0
        self.heater_pwm = value
        # here we could also implement a cooling fan -
        # if the output goes below 0.0

    def pid_update_input(self):
        return self.temperature

    def heater_setup(self):
        # self._heater_pwm = digitalio.DigitalInOut(self.get_pin("heater_pin"))
        # self._heater_pwm.direction = digitalio.Direction.OUTPUT
        self._heater_pwm = pwmio.PWMOut(self.get_pin("heater_pin"), frequency=300)
        # manually set heater off
        self._heater_pwm.duty_cycle = 65535
        self.pid = pid.PID(
            self.pid_update_input,
            self.pid_update_output,
            update_intervall=self.config["pid"]["update_intervall"],
            P_gain=self.config["pid"]["P_gain"],
            I_gain=self.config["pid"]["I_gain"],
            D_gain=self.config["pid"]["D_gain"],
            # debug_out_print=True,
        )
        self.heater_target = False
        # self.print("heater_setup done:", self.heater)

    @property
    def heater_pwm(self):
        # return not self._heater_pwm.value
        value_inverted = self._heater_pwm.duty_cycle / 65535
        value = 1.0 - value_inverted
        return value

    @heater_pwm.setter
    def heater_pwm(self, value):
        # digital io
        # invert value
        # value = not value
        # if self._heater_pwm.value != value:
        #     self._heater_pwm.value = value
        #     # something changed!
        #     if hasattr(self, "ui"):
        #         self.ui.show_heater_state(not value)
        # return not self._heater_pwm.value
        # pwm io
        value = helper.limit(value, 0.0, 1.0)
        value_inverted = 1.0 - value
        duty_cycle = int(65535 * value_inverted)
        if self._heater_pwm.duty_cycle != duty_cycle:
            self._heater_pwm.duty_cycle = duty_cycle
            # something changed!
            if hasattr(self, "ui"):
                self.ui.show_heater_state(value, self._heater_pwm.duty_cycle)
        # return self._heater_pwm.duty_cycle
        return value

    @property
    def heater_target(self):
        return self.pid.set_point

    @heater_target.setter
    def heater_target(self, value):
        # self.print("heater_target.setter: value", value, end="")
        if value is False or value is None:
            if self.temperature_reference:
                value = self.temperature_reference
            else:
                # fallback to 18°C
                value = 18
        # self.print(" →", value)
        self.pid.set_point = value
        return value

    def set_heater_target_to_profile_target(self):
        target = self.profile_selected.temp_current_proportional_target_get()
        if target:
            if target < self.temperature_reference:
                target = self.temperature_reference
        else:
            target = False
        self.heater_target = target
        return target

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
        self.print("rc state: '{}' -> '{}'".format(state_name_old, state_name_new))
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
        self.heater_target = False

    def states_standby_update(self):
        pass

    def states_standby_leave(self):
        pass

    ##########################################
    # reflow

    # handling actuall reflow process
    def reflow_start(self):
        self.profile_selected.start(temperature_min=self.temperature_reference)

    def reflow_update(self):
        # handle heater_target with currently selected profile..
        self.set_heater_target_to_profile_target()
        profile_running = self.profile_selected.step_next_check_and_do(
            myprint=self.print
        )
        # self.print("profile_running", profile_running)
        if profile_running is False:
            # we reached the end of the reflow process
            self.switch_to_state("standby")
        # if self.profile_selected.step_next_check_and_do() is False:
        #     # we reached the end of the reflow process
        #     self.switch_to_state("reflow_done")

    def reflow_finished(self):
        self.heater_target = False
        self.ui.switch_to_state("reflow_done")

    ##########################################
    # calibration functions
    def calibrate_start(self):
        self.profile_selected.start(temperature_min=self.temperature_reference)

    def calibrate_update(self):
        """
        Calibrate / Analyse Heater behavior.

        what do we want to get?!
        StepTime?
        """
        self.reflow_update()

    def calibrate_finished(self):
        self.heater_target = False
        self.ui.switch_to_state("calibration_done")

    ##########################################
    # main handling

    def temperature_filter_update(self, temperature):
        self.temperature_list.append(temperature)
        if len(self.temperature_list) > 4:
            del self.temperature_list[0]
        # diff = max(self.temperature_list) - min(self.temperature_list)
        average = sum(self.temperature_list) / len(self.temperature_list)
        return average
        # return diff, average

    def temperature_update_on_change(self, temperature_read):
        # temp_average = self.temperature_filter_update(temperature_read)
        # temp_diff, temp_average = self.temperature_filter_update(temperature_read)
        # self.print(
        #     "temp_diff:    {:.02f}°C \n"
        #     "temp_average: {:.02f}°C \n"
        #     "temperature:  {}°C \n"
        #     "".format(
        #         temp_diff,
        #         temp_average,
        #         self.temperature,
        #     ),
        #     # end="",
        # )
        # if temp_average != self.temperature:
        #     self.temperature = temp_average
        if temperature_read != self.temperature:
            self.temperature = temperature_read
            temp_diff = abs(self.temperature_change_last - self.temperature)
            if temp_diff >= 0.3:
                # self.print(
                #     "temp_diff:    {:.02f}°C \n"
                #     "temperature_change_last:  {:.02f}°C \n"
                #     # "temp_average: {:.02f}°C \n"
                #     "temperature:  {:.02f}°C \n"
                #     "".format(
                #         temp_diff,
                #         self.temperature_change_last,
                #         # temp_average,
                #         self.temperature,
                #     ),
                #     # end="",
                # )
                # self.print("temp_diff:    {:.02f}°C \n" "".format(temp_diff))
                # if hasattr(self, "ui"):
                #     self.ui.print(content=True)
                self.temperature_change_last = self.temperature
                self.temperature_changed = temp_diff
            else:
                self.temperature_changed = False
        else:
            self.temperature_changed = False

    def temperature_update(self):
        self.temperature_read_error = None
        try:
            temperature_read = self.max31855.temperature
            temperature_reference_read = self.max31855.reference_temperature
        except RuntimeError as e:
            self.temperature_changed = False
            self.temperature_read_error = e
            self.ui.print_warning("sensor: ", e)
            e_message = e.args[0]
            if "short circuit to ground" in e_message:
                pass
            elif "short circuit to power" in e_message:
                pass
            elif "faulty reading" in e_message:
                pass
            elif "thermocouple not connected" in e_message:
                pass
            else:
                raise e
        else:
            self.temperature_reference_raw = temperature_reference_read
            self.temperature_reference = helper.round_nearest(
                self.temperature_reference_raw, 0.25
            )
            # temperature_filtered = self.temperature_filter_update(temperature_read)
            # self.temperature_update_on_change(temperature_filtered)
            self.temperature_update_on_change(temperature_read)

    def main_loop(self):
        gc.collect()
        self.temperature_update()
        self.pid.update()
        # self.temperature_update_fake()
        self.state_current.update()
        self.ui.update()
        # self.check_buttons()
        # if supervisor.runtime.serial_bytes_available:
        #     self.check_input()

    def run(self):
        self.print(42 * "*")
        self.print("run")
        # if supervisor.runtime.serial_connected:
        self.ui.userinput_print_help()
        running = True
        while running:
            try:
                self.main_loop()
            except KeyboardInterrupt as e:
                self.print("KeyboardInterrupt - Stop Program.", e)
                running = False


##########################################
