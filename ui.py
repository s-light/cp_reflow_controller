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
        },
        "colors": {
            "off": (0, 0, 0),
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
        print("changed UI state: '{}' -> '{}'".format(state_name_old, state_name_new))
        self.state_current.update()

    # standby
    def states_standby_enter(self):
        self.show_terminal()

    def states_standby_update(self):
        if self.buttons.a.rose:
            self.buttons.a.update()
            # print(colors.fg.blue, end="")
            print("Button A")
        if self.buttons.b.rose:
            self.buttons.b.update()
            # print(colors.fg.green, end="")
            print("Button B")
        if self.buttons.up.rose:
            self.buttons.up.update()
            print("Button up")
            # print(control.cursor.previous_line("2"), end="")
            # print("\033[1F", end="")
        if self.buttons.down.rose:
            self.buttons.down.update()
            print("Button down")
        if self.buttons.left.rose:
            self.buttons.left.update()
            print("Button left")
            # print(control.erase_line("0"), end="")
            # print("\033[K", end="")
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
            print("Button select")
            # print(colors.reset, end="")
            # print(terminal.control.erase_display(), end="")

    def states_standby_leave(self):
        pass

    # calibrate
    # def states_calibrate_enter(self):
    #     pass

    def states_calibrate_update(self):
        print(
            "{previous_line2}"
            "{erase_line}stage:   '{stage}'\n"
            "{erase_line}runtime:  {orange}{runtime: >6.2f}{reset}s\n"
            "".format(
                stage="test",
                runtime=time.monotonic(),
                orange=terminal.colors.fg.orange,
                reset=terminal.colors.reset,
                previous_line2=terminal.control.cursor.previous_line(2),
                erase_line=terminal.control.erase_line(0),
            ),
            end="",
        )
        time.sleep(0.5)

    # def states_calibrate_leave(self):
    #     self.switch_to_state("standby")

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

    # reflow
    def menu_reflowcycle_stop(self):
        self.switch_to_state("standby")

    def states_reflow_running_enter(self):
        # prepare display update timing
        self.my_plane.xrange = (
            self.my_plane.xrange[0],
            self.round_int_up(self.profile_selected.duration),
        )
        self.my_plane.yrange = (
            self.my_plane.yrange[0],
            self.round_int_up(self.profile_selected.max_temperatur),
        )
        self.display_update_intervall = int(
            self.my_plane.xrange[1] / self.my_plane._width
        )
        self.last_display_update = 0

        self.display.show(self.main_group)
        # TODO: s-light: show profile as background graph
        # graph_data = []
        # for step in self.profile_selected.setps:
        #     point = (step.["duration"], step.["temp_target"])
        #     graph_data.append(point)
        self.reflowcontroller.switch_to_state("reflow")

    def states_reflow_running_update(self):
        if self.buttons.select.rose:
            self.buttons.select.update()
            self.switch_to_state("standby")
        # update display content
        # only add new point every second..
        duration = self.profile_selected.runtime - self.last_display_update
        if duration > self.display_update_intervall:
            self.last_display_update = self.profile_selected.runtime
            self.my_plane.update_line(
                round(self.profile_selected.runtime),
                self.reflowcontroller.temperature,
            )

    # reflow_done
    def states_reflow_done_enter(self):
        print("")
        print("reflow cycle done. ")
        print("please confirm: 'START'")
        print("")

    def states_reflow_done_update(self):
        if self.buttons.start.rose:
            self.switch_to_state("standby")

    def states_reflow_done_leave(self):
        print("")
        self.pixels_all(self.colors["off"])

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
            "calibrate": State(
                name="calibrate",
                # enter=self.states_calibrate_enter,
                update=self.states_calibrate_update,
                # leave=self.states_calibrate_leave,
            ),
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
                # leave=self.reflowcycle_finished,
            ),
            "reflow_done": State(
                name="reflow_done",
                enter=self.states_reflow_done_enter,
                update=self.states_reflow_done_update,
                leave=self.states_reflow_done_leave,
                # leave=lambda: self.switch_to_state("standby"),
            ),
        }
        self.switch_to_state("standby")

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
            # self.calibrate()
            self.switch_to_state("calibrate")
        if "start" in input_string:
            self.switch_to_state("reflow_prepare")
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
    def update(self):
        self.buttons.update()
        self.state_current.update()
        # self.display_update()
        if supervisor.runtime.serial_bytes_available:
            self.check_input()


##########################################
