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
import usb_cdc
from adafruit_pybadger import pybadger
import displayio
from adafruit_displayio_layout.widgets.cartesian import Cartesian

import ansi_escape_code as terminal
import nonblocking_serialinput as nb_serial

import helper

from configdict import extend_deep
from state import State

from buttons import PyBadgeButtons

##########################################
# functions


##########################################
# main classe


class ReflowControllerUI(object):
    """ReflowControllerDisplay."""

    logo_slight = """
        ^ ^
       (0,0)
       ( _ )
        " "
    s-light.eu
    """

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
            # "serial": {
            #     "lines_spacing_above": 15,
            # },
        },
        "serial_data": {
            "intervall": 0.1,
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
        # self.print("ReflowControllerDisplay")
        self.reflowcontroller = reflowcontroller
        self.setup_serial()
        self.setup()
        self.setup_states()
        self.setup_colors()
        self.usb_cdc_data_setup()

    def setup_serial(self):
        self.my_input = nb_serial.NonBlockingSerialInput(
            input_handling_fn=self.userinput_event_handling,
            print_help_fn=self.userinput_print_help,
            echo=True,
            statusline=True,
            statusline_intervall=1.0,
            statusline_fn=self.statusline_fn,
        )
        self.print = self.my_input.print
        self.reflowcontroller.print = self.my_input.print

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
            xrange=(0, helper.round_up(self.profile_selected.duration)),
            yrange=(0, helper.round_up(self.profile_selected.max_temperature)),
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
            helper.round_up(self.profile_selected.duration),
        )
        self.my_plane.yrange = (
            self.my_plane.yrange[0],
            helper.round_up(self.profile_selected.max_temperature),
        )
        # if self.my_plane.xrange[1] < self.my_plane._width:
        #     pass
        self.display_update_intervall = self.my_plane.xrange[1] / self.my_plane._width
        if self.display_update_intervall >= 1.0:
            self.display_update_intervall = round(self.display_update_intervall)
        self.last_display_update = 0
        self.print("self.my_plane.xrange", self.my_plane.xrange)
        self.print("self.my_plane.yrange", self.my_plane.yrange)
        self.print("self.display_update_intervall", self.display_update_intervall)

    def show_heater_state(self, value, value_raw=None):
        if value:
            color = self.config["colors"]["on"]
            # TODO: apply dimming.
            # color =
            self.pixels[4] = color
        else:
            self.pixels[4] = self.config["colors"]["off"]
        # self.print(" " * 48 + "heater: {: >7.2f}".format(value), end="")
        # if value_raw:
        #     self.print(" = {: >6}".format(value_raw), end="")
        # else:
        #     # add missing line end
        #     self.print()
        pass

    def print_temperature(self):
        if (
            self.reflowcontroller.temperature
            and self.reflowcontroller.temperature_reference
        ):
            self.print(
                "temp: {:.02f}°C"
                # " (ref: {:.02f}°C)"
                "".format(
                    self.reflowcontroller.temperature,
                    # self.reflowcontroller.temperature_reference,
                ),
                # end="",
            )
        else:
            self.print("temp: not available")

    def print_warning(self, message, error):
        self.print(
            "{message}"
            "{color}{error}{reset}"
            "".format(
                message=message,
                error=error,
                color=terminal.ANSIColors.fg.orange,
                reset=terminal.ANSIColors.reset,
            )
        )

    ##########################################
    # usb_cdc.data

    def create_plot_data_system(self):
        # current = self.reflowcontroller.temperature
        # if not current:
        #     current = 0
        text = (
            # "{runtime: > 7.2f}, "
            "{current: > 7.2f}, "
            "{heater_target: > 7.2f}, "
            "{heater_pwm: > 7.2f}, "
        ).format(
            # runtime=time.monotonic(),
            current=self.reflowcontroller.temperature,
            heater_target=self.reflowcontroller.heater_target,
            heater_pwm=self.reflowcontroller.heater_pwm * 100,
        )
        return text

    def create_plot_data_profile(self):
        step_index = 0
        if self.profile_selected:
            step_index = self.profile_selected.step_current_index
        if not step_index:
            step_index = 0
        text = (
            # "{runtime: >7.2f}, "
            "{step_index: >2d}, "
            "{error: > 7.2f}, "
        ).format(
            # runtime=self.profile_selected.runtime,
            step_index=step_index * 10,
            error=self.reflowcontroller.pid.error,
        )
        return text

    def create_plot_data_pid(self):
        text = ""
        pid = self.reflowcontroller.pid
        if pid:
            text = (
                "{p_value: >6.2f}, " "{i_value: >6.2f}, " "{d_value: >6.2f}, "
            ).format(
                p_value=pid.P_value,
                i_value=pid.I_value,
                d_value=pid.D_value,
            )
        return text

    def usb_cdc_data_send(self):
        text = ""
        text += self.create_plot_data_system()
        text += self.create_plot_data_profile()
        # text += self.create_plot_data_pid()
        text += "\n"
        usb_cdc.data.write(text.encode("utf-8"))
        # self.print(text, end="")

    def usb_cdc_data_setup(self):
        self.usb_cdc_data_last_send = time.monotonic()
        self.usb_cdc_data_intervall = self.config["serial_data"]["intervall"]

    def usb_cdc_data_update(self):
        duration = time.monotonic() - self.usb_cdc_data_last_send
        if duration > self.usb_cdc_data_intervall:
            self.usb_cdc_data_send()
            self.usb_cdc_data_last_send = time.monotonic()

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
        #     self.print(e)
        #     success = False
        # else:
        #     success = True
        # return success
        self.state_current = self.states[state]
        self.state_current.active = True
        state_name_new = self.state_current.name
        # self.print("UI state: '{}' -> '{}'".format(state_name_old, state_name_new))
        self.state_current.update()

    def setup_states(self):
        # self.print("UI setup_states")
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
        self.reflowcontroller.switch_to_state("standby")

    def states_standby_update(self):
        # update display
        if self.buttons.a.rose:
            self.buttons.a.update()
            self.switch_to_state("calibration_prepare")
            # self.print("Button A")
        if self.buttons.b.rose:
            self.buttons.b.update()
            self.print("Button B")
        if self.buttons.up.rose:
            self.buttons.up.update()
            self.print("Button up")
        if self.buttons.down.rose:
            self.buttons.down.update()
            self.print("Button down")
        if self.buttons.left.rose:
            self.buttons.left.update()
            self.print("Button left")
        if self.buttons.right.rose:
            self.buttons.right.update()
            self.print("Button right")

            # test_control()
        if self.buttons.start.rose:
            self.buttons.start.update()
            # self.print("Button start")
            self.switch_to_state("reflow_prepare")
        if self.buttons.select.rose:
            self.buttons.select.update()
            # self.print("Button select")
            self.reflowcontroller.profile_select_next()
            self.print_help()

    def states_standby_leave(self):
        pass

    ##########################################
    # calibrate

    ####################
    # calibrate prepare

    def states_calibration_prepare_enter(self):
        self.print("Do you really want to start the calibration cycle?")
        self.reflowcontroller.profile_select_calibration()
        # for the small screen
        self.print("selected profil:")
        self.print(self.profile_selected.title)
        self.print("run: 'START'")
        self.print("cancle: any other button")
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
            helper.round_up(self.profile_selected.max_temperature) + 20,
        )
        # self.print("\n" * self.config["display"]["serial"]["lines_spacing_above"])
        self.my_plane.clear_plot_lines()
        self.display.show(self.main_group)
        self.reflowcontroller.switch_to_state("calibrate")

    def states_calibration_running_update(self):
        if self.reflowcontroller.temperature_changed:
            self.usb_cdc_data_send()
        if self.buttons.select.rose:
            self.buttons.select.update()
            self.switch_to_state("standby")
        # update display content
        # only add new point every second..
        duration = self.profile_selected.runtime - self.last_display_update
        if duration > self.display_update_intervall:
            self.last_display_update = self.profile_selected.runtime
            self.reflow_update_ui_display()
            # self.update_ui_serial_singleline(end="")
            self.pixels_set_proportional(
                self.profile_selected.step_current_index,
                len(self.profile_selected.steps) - 1,
                pixel_count=4,
            )

    # def states_calibration_running_leave(self):
    #     self.switch_to_state("standby")

    ####################
    # calibrate done

    def states_calibration_done_enter(self):
        self.pixels_all(self.colors["done"])
        self.print("")
        self.print("calibration cycle done. ")
        self.print("please confirm: 'START'")
        self.print("")

    def states_calibration_done_update(self):
        if self.buttons.start.rose:
            self.buttons.start.update()
            self.switch_to_state("standby")

    def states_calibration_done_leave(self):
        self.print("calibration results:")
        self.print("--> TODO!!!!")
        self.pixels_all(self.colors["off"])

    ##########################################
    # reflow

    ####################
    # reflow_prepare
    def states_reflow_prepare_enter(self):
        # clear full screen
        self.print(terminal.ANSIControl.erase_display(2))
        self.print("Do you really want to start the reflow cycle?")
        self.print("selected profil:")
        self.print(self.profile_selected.format_profile())

        # for the small screen
        self.print("selected profil:")
        self.print(self.profile_selected.title)
        self.print("run: 'START'")
        self.print("cancle: any other button")
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
        # self.print("\n" * self.config["display"]["serial"]["lines_spacing_above"])
        self.my_plane.clear_plot_lines()
        self.display.show(self.main_group)
        # TODO: s-light: show profile as background graph
        # graph_data = []
        # for step in self.profile_selected.setps:
        #     point = (step.["duration"], step.["temp_target"])
        #     graph_data.append(point)
        self.reflowcontroller.switch_to_state("reflow")

    def reflow_update_ui_display(self):
        # self.print("display update.", self.profile_selected.runtime)
        runtime = round(self.profile_selected.runtime)
        if self.display_update_intervall < 1.0:
            runtime = min(self.my_plane.xrange[1], self.profile_selected.runtime)
        # hard limit so we trigger no out of range execption
        temperature = min(self.my_plane.yrange[1], self.reflowcontroller.temperature)
        self.my_plane.add_plot_line(runtime, temperature)

    def old_unused_code_to_store_somewhere_for_maybe_later_use(self):
        # def update_ui_serial_multiline(self, replace=True):
        #     # update serial output
        #     lines_spacing_above = self.config["display"]["serial"]["lines_spacing_above"]
        #     text = ""
        #     lines = [
        #         "step_name:     '{step_name}'\n",
        #         "runtime:{runtime: >7.2f}s\n",
        #         "target:  {orange}{target: >6.2f}{reset}°C\n",
        #         "current: {current: >6.2f}°C\n",
        #     ]
        #     if replace:
        #         for line in lines:
        #             text += "{erase_line}" + line
        #     else:
        #         text = lines.join("")
        #     text = ("\n" * lines_spacing_above) + text
        #     if replace:
        #         text = "{move_to_previous_lines}" + text
        #     self.print(
        #         text.format(
        #             step_name=self.profile_selected.step_current["name"],
        #             runtime=self.profile_selected.runtime,
        #             target=self.reflowcontroller.heater_target,
        #             current=self.reflowcontroller.temperature,
        #             orange=terminal.AnsiColors.fg.orange,
        #             reset=terminal.AnsiColors.reset,
        #             move_to_previous_lines=terminal.control.cursor.previous_line(
        #                 len(lines) + lines_spacing_above
        #             ),
        #             erase_line=terminal.control.erase_line(0),
        #         ),
        #         end="",
        #     )
        #
        # def update_ui_serial_singleline(self, replace=False, end="\n"):
        #     # update serial output
        #     text = (
        #         "{step_name: <10} "
        #         "{runtime: >7.2f}s "
        #         "t: {orange}{target: > 7.2f}{reset}°C "
        #         "c: {current: > 7.2f}°C "
        #         "d: {error: > 7.2f}°C "
        #     )
        #     # if replace:
        #     #     text += "{erase_line}" + text
        #     # text = ("\n" * lines_spacing_above) + text
        #     # if replace:
        #     #     text = "{move_to_previous_lines}" + text
        #     self.print(
        #         text.format(
        #             step_name=self.profile_selected.step_current["name"],
        #             runtime=self.profile_selected.runtime,
        #             target=self.reflowcontroller.heater_target,
        #             current=self.reflowcontroller.temperature,
        #             error=self.reflowcontroller.pid.error,
        #             orange=terminal.AnsiColors.fg.orange,
        #             reset=terminal.AnsiColors.reset,
        #             move_to_previous_lines=terminal.control.cursor.previous_line(1),
        #             erase_line=terminal.control.erase_line(0),
        #         ),
        #         # end=end,
        #     )
        #
        # def reflow_update_ui_serial(self, replace=True):
        #     # self.update_ui_serial_multiline(replace)
        #     self.update_ui_serial_singleline()
        pass

    def states_reflow_running_update(self):
        if self.reflowcontroller.temperature_changed:
            self.usb_cdc_data_send()
        if self.buttons.select.rose:
            self.buttons.select.update()
            self.switch_to_state("standby")
        # update display content
        # only add new point every second..
        duration = self.profile_selected.runtime - self.last_display_update
        if duration > self.display_update_intervall:
            self.last_display_update = self.profile_selected.runtime
            self.reflow_update_ui_display()
            # self.reflow_update_ui_serial()
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
        self.print("")
        self.print("reflow cycle done. ")
        self.print("please confirm: 'START'")
        self.print("")

    def states_reflow_done_update(self):
        if self.buttons.start.rose:
            self.buttons.start.update()
            self.switch_to_state("standby")

    def states_reflow_done_leave(self):
        self.print("")
        self.pixels_all(self.colors["off"])

    ##########################################
    # menu

    def userinput_print_help(self):
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
        self.print(
            "you can set some options:\n"
            "- 'pid *' set pid *\n"
            "- 'pid p': proportional gain ({pid_p: >8.5f})\n"
            "- 'pid i': integral gain     ({pid_i: >8.5f})\n"
            "- 'pid d': derivative gain   ({pid_d: >8.5f})\n"
            # "- 'pid s': set_point         ({pid_s: >8.5f})\n"
            "- 'h': set heater_target ({heater_target: > 7.2f})\n"
            "- 'pn' select next profil\n"
            "{profile_list}"
            "- 'calibrate'\n"
            "- 'start' reflow cycle\n"
            "- 'stop'  reflow cycle\n"
            "".format(
                profile_list=profile_list,
                pid_p=self.reflowcontroller.pid.P_gain,
                pid_i=self.reflowcontroller.pid.I_gain,
                pid_d=self.reflowcontroller.pid.D_gain,
                # pid_s=self.reflowcontroller.pid.set_point,
                heater_target=self.reflowcontroller.heater_target,
            ),
            # end="",
        )

    def userinput_event_handling__pid(self, input_string):
        if input_string.startswith("pid p"):
            value = nb_serial.parse_value(input_string, "pid p")
            if value:
                self.reflowcontroller.pid.P_gain = value
        elif input_string.startswith("pid i"):
            value = nb_serial.parse_value(input_string, "pid i")
            if nb_serial.is_number(value):
                self.reflowcontroller.pid.I_gain = value
        elif input_string.startswith("pid d"):
            value = nb_serial.parse_value(input_string, "pid d")
            if nb_serial.is_number(value):
                self.reflowcontroller.pid.D_gain = value
        # elif input_string.startswith(f "pid s"):
        #     value = nb_serial.parse_value(input_string, "pid s")
        #     if nb_serial.is_number(value):
        #         self.reflowcontroller.pid.set_point = value

    def userinput_event_handling(self, input_string):
        """Check Input."""
        if input_string.startswith("calibrate"):
            # self.calibrate()
            self.switch_to_state("calibration_prepare")
        elif input_string.startswith("start"):
            self.switch_to_state("reflow_prepare")
        elif input_string.startswith("stop"):
            self.menu_reflowcycle_stop()
        elif input_string.startswith("pn"):
            self.reflowcontroller.profile_select_next()
        elif input_string.startswith("pid"):
            self.userinput_event_handling__pid(input_string)
        elif input_string.startswith("h"):
            value = nb_serial.parse_value(input_string, "h")
            if nb_serial.is_number(value):
                self.reflowcontroller.heater_target = value

    statusline_template = (
        "uptime:{uptime: >8.2f}    "
        # "temp: {current_color}{current: >6.02f}{reset}°C   "
        "temp: {current: >6.02f}°C   "
        "target: {target: >6.02f}°C   "
        "error: {error: >6.02f}°C   "
        "step: {step_name: <11s}   "
        "runtime: {step_runtime: >7.2f}s   "
        "ui: {ui_state: <14}   "
        "ctr: {ctr_state: <14}"
    )

    def statusline_fn(self):
        """
        Generate statusline.

        NO prints in this function!!
        (leads to infinity loops..)

        line content:

        uptime:00000.00
        temp: 000.00°C
        target: 000.00°C
        error: 000.00°C
        step: step_nameNAME_
        runtime: 0000.00s

        """

        # this does not work in that easy way...
        # current_color = terminal.ANSIColors.fg.lightblue
        # if self.reflowcontroller.temperature_changed:
        #     # self.reflowcontroller.temperature_changed = False
        #     # print("\n" * 5 + "tch" + "\n" * 5)
        #     current_color = terminal.ANSIColors.fg.orange
        temperature_current = 0
        if (
            self.reflowcontroller.temperature
            and self.reflowcontroller.temperature_reference
        ):
            temperature_current = self.reflowcontroller.temperature
        temperature_target = self.reflowcontroller.heater_target
        temperature_error = 0
        if hasattr(self.reflowcontroller.pid, "error"):
            temperature_error = self.reflowcontroller.pid.error

        step_name = "***"
        step_runtime = -1
        if self.profile_selected:
            if self.profile_selected.step_current:
                step_name = self.profile_selected.step_current["name"]
                step_runtime = self.profile_selected.runtime

        statusline = self.statusline_template.format(
            uptime=time.monotonic(),
            # current_color=current_color,
            current=temperature_current,
            target=temperature_target,
            error=temperature_error,
            step_name=step_name,
            step_runtime=step_runtime,
            ui_state=self.state_current.name,
            ctr_state=self.reflowcontroller.state_current.name,
            reset=terminal.ANSIColors.reset,
        )

        return statusline

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
        #     self.print("Exception parsing 'col': ", e)
        # try:
        #     row = int(input_string[sep_pos + 1 : sep_value])
        # except ValueError as e:
        #     self.print("Exception parsing 'row': ", e)
        # try:
        #     value = int(input_string[sep_value + 1 :])
        # except ValueError as e:
        #     self.print("Exception parsing 'value': ", e)
        # pixel_index = 0
        pass

    ##########################################
    # main handling
    def update(self):
        self.buttons.update()
        self.state_current.update()
        # self.display_update()
        self.usb_cdc_data_update()
        self.my_input.update()


##########################################
