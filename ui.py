#!/usr/bin/env python3
# coding=utf-8

# SPDX-FileCopyrightText: 2021 Stefan Krüger
#
# SPDX-License-Identifier: MIT
#############################

"""
all things UI:
serial terminal & display terminal & drawing & button handling
"""


# import os
# import sys

import time
import board
import supervisor
from adafruit_pybadger import pybadger
import displayio
from adafruit_displayio_layout.widgets.cartesian import Cartesian

from configdict import extend_deep
import ASCII_escape_code as terminal
from state import State

from buttons import PyBadgeButtons

##########################################
# functions


##########################################
# main classe


class ReflowControllerUI(object):
    """ReflowControllerDisplay."""

    config_defaults = {
        "hw": {
            "auto_dim_display": 1,
            "display_brightness": 0.1,
        },
        "display": {
            "cartesian": {
                "x": 30,
                "y": 2,
                "width": 128,
                "height": 105,
            },
            "colors": {
                "black": 0x000000,
                "white": 0xFFFFFF,
                "gray": 0xA0A0A0,
                "blue": 0x0000FF,
                "blue_light": 0x1020FF,
                "blue_dark": 0x000010,
                # "blue_dark": 0x000010,
            },
            "serial": {
                "lines_spacing_above": 15,
            },
        },
        "colors": {
            "off": (0, 0, 0),
            "on": (2, 0, 1),
            # "done": (50, 255, 0),
            # "warn": (255, 255, 0),
            # "error": (255, 0, 0),
            "info": (0, 1, 1),
            "done": (0, 1, 0),
            "warn": (2, 1, 0),
            "error": (3, 0, 0),
        },
    }

    def __init__(self, reflowcontroller):
        super(ReflowControllerUI, self).__init__()
        # print("ReflowControllerDisplay")
        self.reflowcontroller = reflowcontroller
        self.setup()
        self.setup_states()
        self.setup_colors()

    def setup(self):
        self.config = self.reflowcontroller.config
        extend_deep(self.config, self.config_defaults.copy())

        self.display = board.DISPLAY
        # setup some attributes for fast access
        self.profile_selected = self.reflowcontroller.profile_selected
        self.profiles_names = self.reflowcontroller.profiles_names
        self.profiles = self.reflowcontroller.profiles

        # https://circuitpython.readthedocs.io/projects/pybadger/en/latest/api.html
        pybadger.auto_dim_display(delay=self.config["hw"]["auto_dim_display"])
        pybadger.brightness = self.config["hw"]["display_brightness"]

        self.show_terminal = pybadger.show_terminal
        self.pixels = pybadger.pixels
        # self.reflowcontroller.pixels = pybadger.pixels
        self.pixels = pybadger.pixels
        self.buttons = PyBadgeButtons()

        # setup cartesian
        # pybadge display:  160x128
        # Create a Cartesian widget
        # https://circuitpython.readthedocs.io/projects/displayio-layout/en/latest/api.html#module-adafruit_displayio_layout.widgets.cartesian
        self.my_plane = Cartesian(
            x=30,  # x position for the plane
            y=2,  # y plane position
            width=128,  # display width
            height=105,  # display height
            xrange=(0, self.round_int_up(self.profile_selected.duration)),
            yrange=(0, self.round_int_up(self.profile_selected.max_temperatur)),
        )

        self.main_group = displayio.Group()
        self.main_group.append(self.my_plane)

    def pixels_all(self, color):
        for index, pixel in enumerate(self.pixels):
            self.pixels[index] = color

    def setup_colors(self):
        self.colors = self.config["colors"]

    ##########################################
    # helper functions
    @staticmethod
    def round_int_up(value, round_to=10):
        """round integer up to next `round_to` value.
        based on: https://stackoverflow.com/a/14092788/574981
        """
        return value + (-value) % round_to

    def pixels_set_proportional(
        self, value, count, pixel_count=None, color_on=None, color_off=None
    ):
        if value and count:
            if not pixel_count:
                pixel_count = len(self.pixels)
            if not color_on:
                color_on = self.colors["info"]
            if not color_off:
                color_off = self.colors["off"]
            # set pixel proportional
            # pixel_count = 100% = count
            # pixel_max = x = value
            pixel_max = pixel_count * value / count
            for index in range(pixel_count):
                if index < pixel_max:
                    self.pixels[index] = color_on
                else:
                    self.pixels[index] = color_off

    def prepare_display_update(self):
        # prepare display update timing
        self.my_plane.xrange = (
            self.my_plane.xrange[0],
            self.round_int_up(self.profile_selected.duration),
        )
        self.my_plane.yrange = (
            self.my_plane.yrange[0],
            self.round_int_up(self.profile_selected.max_temperatur),
        )
        # if self.my_plane.xrange[1] < self.my_plane._width:
        #     pass
        self.display_update_intervall = self.my_plane.xrange[1] / self.my_plane._width
        if self.display_update_intervall >= 1.0:
            self.display_update_intervall = round(self.display_update_intervall)
        self.last_display_update = 0
        print("self.my_plane.xrange", self.my_plane.xrange)
        print("self.my_plane.yrange", self.my_plane.yrange)
        print("self.display_update_intervall", self.display_update_intervall)

    def show_heater_state(self, value):
        if value:
            self.pixels[4] = self.config["colors"]["on"]
        else:
            self.pixels[4] = self.config["colors"]["off"]

    def print_temperature(self):
        if (
            self.reflowcontroller.temperature
            and self.reflowcontroller.temperature_reference
        ):
            print(
                "temp: {:.02f}°C"
                # " (ref: {:.02f}°C)"
                "".format(
                    self.reflowcontroller.temperature,
                    # self.reflowcontroller.temperature_reference,
                ),
                # end="",
            )
        else:
            print("temp: not available")

    def print_warning(self, message, error):
        print(
            "{message}"
            "{color}{error}{reset}"
            "".format(
                message=message,
                error=error,
                color=terminal.colors.fg.orange,
                reset=terminal.colors.reset,
            )
        )

    ##########################################
    # state handling

    def switch_to_state(self, state):
        """switch to new state."""
        state_name_old = None
        if self.state_current:
            self.state_current.active = False
            state_name_old = self.state_current.name
        # success = None
        # try:
        #     self.state_current = self.states[state]
        #     self.state_current.active = True
        #     state_name_new = self.state_current.name
        #     print(
        #         "changed UI state: '{}' -> '{}'".format(state_name_old, state_name_new)
        #     )
        #     self.state_current.update()
        # except KeyError as e:
        #     print(e)
        #     success = False
        # else:
        #     success = True
        # return success
        self.state_current = self.states[state]
        self.state_current.active = True
        state_name_new = self.state_current.name
        print("UI state: '{}' -> '{}'".format(state_name_old, state_name_new))
        self.state_current.update()

    def setup_states(self):
        # print("UI setup_states")
        self.state_current = {}
        self.states = {
            # "standby": State(name="standby", enter=(lambda: pass),),
            "standby": State(
                name="standby",
                enter=self.states_standby_enter,
                update=self.states_standby_update,
                leave=self.states_standby_leave,
            ),
            # calibration cycle
            "calibration_prepare": State(
                name="calibration_prepare",
                enter=self.states_calibration_prepare_enter,
                update=self.states_calibration_prepare_update,
                # leave=self.states_calibration_prepare_leave,
            ),
            "calibration_running": State(
                name="calibration_running",
                enter=self.states_calibration_running_enter,
                update=self.states_calibration_running_update,
                # leave=self.states_calibration_running_leave,
            ),
            "calibration_done": State(
                name="calibration_done",
                enter=self.states_calibration_done_enter,
                update=self.states_calibration_done_update,
                leave=self.states_calibration_done_leave,
            ),
            # reflow cylce
            "reflow_prepare": State(
                name="reflow_prepare",
                enter=self.states_reflow_prepare_enter,
                update=self.states_reflow_prepare_update,
                # leave=self.states_reflow_prepare_leave,
            ),
            "reflow_running": State(
                name="reflow_running",
                enter=self.states_reflow_running_enter,
                update=self.states_reflow_running_update,
                # update=self.states_reflow_running_leave,
            ),
            "reflow_done": State(
                name="reflow_done",
                enter=self.states_reflow_done_enter,
                update=self.states_reflow_done_update,
                leave=self.states_reflow_done_leave,
            ),
        }
        self.switch_to_state("standby")

    ##########################################
    # standby

    def states_standby_enter(self):
        self.show_terminal()

    def states_standby_update(self):
        # update display
        if self.reflowcontroller.temperature_changed:
            self.reflowcontroller.temperature_changed = False
            # print("Temperature: {:.02f}°C ".format(self.reflowcontroller.temperature))
            self.print_temperature()
        if self.buttons.a.rose:
            self.buttons.a.update()
            self.switch_to_state("calibration_prepare")
            # print("Button A")
        if self.buttons.b.rose:
            self.buttons.b.update()
            print("Button B")
        if self.buttons.up.rose:
            self.buttons.up.update()
            print("Button up")
        if self.buttons.down.rose:
            self.buttons.down.update()
            print("Button down")
        if self.buttons.left.rose:
            self.buttons.left.update()
            print("Button left")
        if self.buttons.right.rose:
            self.buttons.right.update()
            print("Button right")

            # test_control()
        if self.buttons.start.rose:
            self.buttons.start.update()
            # print("Button start")
            self.switch_to_state("reflow_prepare")
        if self.buttons.select.rose:
            self.buttons.select.update()
            # print("Button select")
            self.reflowcontroller.profile_select_next()
            self.print_help()

    def states_standby_leave(self):
        pass

    ##########################################
    # calibrate

    ####################
    # calibrate prepare

    def states_calibration_prepare_enter(self):
        print("Do you really want to start the calibration cycle?")
        self.reflowcontroller.profile_select_calibration()
        # for the small screen
        print("selected profil:")
        print(self.profile_selected.title)
        print("run: 'START'")
        print("cancle: any other button")
        self.pixels_all(self.colors["info"])

    def states_calibration_prepare_update(self):
        if self.buttons.start.rose:
            # self.switch_to_state("reflow_running")
            self.switch_to_state("calibration_running")
        elif (
            self.buttons.select.rose
            or self.buttons.a.rose
            or self.buttons.b.rose
            or self.buttons.up.rose
            or self.buttons.down.rose
            or self.buttons.right.rose
            or self.buttons.left.rose
        ):
            self.switch_to_state("standby")

    # def states_calibration_prepare_leave(self):
    #     pass

    ####################
    # calibrate running

    def states_calibration_running_enter(self):
        self.prepare_display_update()
        # set special temperature range:
        self.my_plane.yrange = (
            self.my_plane.yrange[0],
            self.round_int_up(self.profile_selected.max_temperatur) + 30,
        )
        print("\n" * self.config["display"]["serial"]["lines_spacing_above"])
        self.reflowcontroller.switch_to_state("calibrate")

    def states_calibration_running_update(self):
        # print("states_calibration_running_update")
        self.states_reflow_running_update()
        # if self.buttons.select.rose:
        #     self.buttons.select.update()
        #     self.switch_to_state("standby")
        # # update display content
        # # only add new point every second..
        # duration = self.profile_selected.runtime - self.last_display_update
        # if duration > self.display_update_intervall:
        #     self.last_display_update = self.profile_selected.runtime
        #     print("display update")
        #     # self.reflow_update_ui_display()
        #     self.reflow_update_ui_serial()
        #     # self.reflow_update_ui_serial(replace=False)
        #     self.pixels_set_proportional(
        #         self.profile_selected.step_current_index,
        #         len(self.profile_selected.steps),
        #     )

    # def states_calibration_running_leave(self):
    #     self.switch_to_state("standby")

    ####################
    # calibrate done

    def states_calibration_done_enter(self):
        self.pixels_all(self.colors["done"])
        print("")
        print("calibration cycle done. ")
        print("please confirm: 'START'")
        print("")

    def states_calibration_done_update(self):
        if self.buttons.start.rose:
            self.buttons.start.update()
            self.switch_to_state("standby")

    def states_calibration_done_leave(self):
        print("calibration results:")
        print("--> TODO!!!!")
        self.pixels_all(self.colors["off"])

    ##########################################
    # reflow

    ####################
    # reflow_prepare
    def states_reflow_prepare_enter(self):
        print("Do you really want to start the reflow cycle?")
        print("selected profil:")
        self.profile_selected.print_profile()

        # for the small screen
        print("selected profil:")
        print(self.profile_selected.title)
        print("run: 'START'")
        print("cancle: any other button")
        self.pixels_all(self.colors["info"])

    def states_reflow_prepare_update(self):
        if self.buttons.start.rose:
            # self.switch_to_state("reflow_running")
            self.switch_to_state("reflow_running")
        elif (
            self.buttons.select.rose
            or self.buttons.a.rose
            or self.buttons.b.rose
            or self.buttons.up.rose
            or self.buttons.down.rose
            or self.buttons.right.rose
            or self.buttons.left.rose
        ):
            self.switch_to_state("standby")

    ####################
    # reflow running
    def menu_reflowcycle_stop(self):
        self.switch_to_state("standby")

    def states_reflow_running_enter(self):
        self.prepare_display_update()
        print("\n" * self.config["display"]["serial"]["lines_spacing_above"])
        self.my_plane.clear_lines()
        self.display.show(self.main_group)
        # TODO: s-light: show profile as background graph
        # graph_data = []
        # for step in self.profile_selected.setps:
        #     point = (step.["duration"], step.["temp_target"])
        #     graph_data.append(point)
        self.reflowcontroller.switch_to_state("reflow")

    def reflow_update_ui_display(self):
        # print("display update.", self.profile_selected.runtime)
        runtime = round(self.profile_selected.runtime)
        if self.display_update_intervall < 1.0:
            runtime = min(self.my_plane.xrange[1], self.profile_selected.runtime)
        # hard limit so we trigger no out of range execption
        temperature = min(self.my_plane.yrange[1], self.reflowcontroller.temperature)
        self.my_plane.add_line(runtime, temperature)

    def update_ui_serial_multiline(self, replace=True):
        # update serial output
        # temp_target = self.profile_selected.temp_current_proportional_target
        temp_target = self.reflowcontroller.temp_current_proportional_target
        if temp_target:
            lines_spacing_above = self.config["display"]["serial"][
                "lines_spacing_above"
            ]
            text = ""
            lines = [
                "stage:     '{stage}'\n",
                "runtime:{runtime: >7.2f}s\n",
                "target:  {orange}{target: >6.2f}{reset}°C\n",
                "current: {current: >6.2f}°C\n",
                "diff:    {diff: >6.2f}°C\n",
            ]
            if replace:
                for line in lines:
                    text += "{erase_line}" + line
            else:
                text = lines.join("")
            text = ("\n" * lines_spacing_above) + text
            if replace:
                text = "{move_to_previous_lines}" + text
            print(
                text.format(
                    stage=self.profile_selected.step_current["stage"],
                    runtime=self.profile_selected.runtime,
                    target=temp_target,
                    current=self.reflowcontroller.temperature,
                    diff=self.reflowcontroller.temperature_difference,
                    orange=terminal.colors.fg.orange,
                    reset=terminal.colors.reset,
                    move_to_previous_lines=terminal.control.cursor.previous_line(
                        len(lines) + lines_spacing_above
                    ),
                    erase_line=terminal.control.erase_line(0),
                ),
                end="",
            )

    def update_ui_serial_singleline(self, replace=False):
        # update serial output
        # temp_target = self.profile_selected.temp_current_proportional_target
        temp_target = self.reflowcontroller.temp_current_proportional_target
        if temp_target:
            lines_spacing_above = self.config["display"]["serial"][
                "lines_spacing_above"
            ]
            text = (
                "{stage: <10} "
                "{runtime: >7.2f}s "
                "t: {orange}{target: >6.2f}{reset}°C "
                "c: {current: >6.2f}°C "
                "d: {diff: >6.2f}°C "
            )
            # if replace:
            #     text += "{erase_line}" + text
            # text = ("\n" * lines_spacing_above) + text
            # if replace:
            #     text = "{move_to_previous_lines}" + text
            print(
                text.format(
                    stage=self.profile_selected.step_current["stage"],
                    runtime=self.profile_selected.runtime,
                    target=temp_target,
                    current=self.reflowcontroller.temperature,
                    diff=self.reflowcontroller.temperature_difference,
                    orange=terminal.colors.fg.orange,
                    reset=terminal.colors.reset,
                    move_to_previous_lines=terminal.control.cursor.previous_line(
                        1 + lines_spacing_above
                    ),
                    erase_line=terminal.control.erase_line(0),
                ),
                end="",
            )

    def reflow_update_ui_serial(self, replace=True):
        # self.update_ui_serial_multiline(replace)
        self.update_ui_serial_singleline()

    def states_reflow_running_update(self):
        if self.buttons.select.rose:
            self.buttons.select.update()
            self.switch_to_state("standby")
        # update display content
        # only add new point every second..
        duration = self.profile_selected.runtime - self.last_display_update
        if duration > self.display_update_intervall:
            self.last_display_update = self.profile_selected.runtime
            self.reflow_update_ui_display()
            self.reflow_update_ui_serial()
            # self.reflow_update_ui_serial(replace=False)
            self.pixels_set_proportional(
                self.profile_selected.step_current_index,
                len(self.profile_selected.steps) - 1,
                pixel_count=4,
            )

    ####################
    # reflow_done
    def states_reflow_done_enter(self):
        self.pixels_all(self.colors["done"])
        print("")
        print("reflow cycle done. ")
        print("please confirm: 'START'")
        print("")

    def states_reflow_done_update(self):
        if self.buttons.start.rose:
            self.buttons.start.update()
            self.switch_to_state("standby")

    def states_reflow_done_leave(self):
        print("")
        self.pixels_all(self.colors["off"])

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
        self.print_temperature()

    def check_input(self):
        """Check Input."""
        input_string = input()
        if "calibrate" in input_string:
            # self.calibrate()
            self.switch_to_state("calibration_prepare")
        if "start" in input_string:
            self.switch_to_state("reflow_prepare")
        if "stop" in input_string:
            self.menu_reflowcycle_stop()
        if "p" in input_string:
            self.reflowcontroller.profile_select_next()
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
    def update(self):
        self.buttons.update()
        self.state_current.update()
        # self.display_update()
        if supervisor.runtime.serial_bytes_available:
            self.check_input()


##########################################
