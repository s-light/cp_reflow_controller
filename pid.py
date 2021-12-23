#!/usr/bin/env python3
# coding=utf-8

"""
simple pid control.

based on
https://github.com/B3AU/micropython/blob/master/PID.py
and
https://www.embeddedrelated.com/showarticle/943.php
and
http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-direction/
"""
import time


class PID:
    """
    Discrete PID control.

    P: proportional
    I: integral
    D: derivative
    """

    def __init__(
        self,
        input_fun,
        output_fun,
        *,  # force keyword arguments
        update_intervall=0.1,
        P_gain=0.0,
        I_gain=0.0,
        D_gain=0.0,
        output_min=0.0,
        output_max=100.0,
        debug_out_print=False,
        debug_out_fun=None,
    ):
        self.input_fun = input_fun
        self.output_fun = output_fun
        self.update_intervall = update_intervall

        self.P_gain = P_gain
        self.P_value = 0

        self.I_gain = I_gain
        self.I_value = 0
        self.I_state = 0
        self.I_max = 100.0
        self.I_min = 0

        self.D_gain = D_gain
        self.D_value = 0
        self.D_state = 0

        self.output_min = output_min
        self.output_max = output_max

        self.debug_out_print = debug_out_print
        self.debug_out_fun = debug_out_fun
        self.set_point = 0.0
        self.output = 0

        self.last_update_time = time.monotonic()

    def _update(self, current_value):
        # calculate the proportional term
        self.P_value = self.P_gain * self.error

        # calculate the integral state with appropriate limiting
        self.I_state += self.error
        # Limit the integrator state if necessary
        if self.I_state > self.I_max:
            self.I_state = self.I_max
        elif self.I_state < self.I_min:
            self.I_state = self.I_min

        # calculate the integral term
        self.I_value = self.I_gain * self.I_state

        # calculate the derivative term
        self.D_value = self.D_gain * (current_value - self.D_state)
        self.D_state = current_value

        # calculate output
        self.output = self.P_value + self.I_value - self.D_value

        # limit output
        if self.output < self.output_min:
            self.output = self.output_min
        if self.output > self.output_max:
            self.output = self.output_max

        if self.debug_out_fun or self.debug_out_print:
            debug_out = (
                # "set_point: {set_point}\n"
                "P_value: {P_value: > 7.2f}  "
                "I_value: {I_value: > 7.2f}  "
                "D_value: {D_value: > 7.2f}  "
                "output: {output: > 7.2f}  "
                "".format(
                    # set_point=self.set_point,
                    P_value=self.P_value,
                    I_value=self.I_value,
                    D_value=self.D_value,
                    output=self.output,
                )
            )
            if self.debug_out_fun:
                self.debug_out_fun(debug_out)
            if self.debug_out_print:
                print(debug_out, end="")

        return self.output / 100.0

    def update(
        self,
        *,  # force keyword arguments
        current_value=None,
        set_point=None,
        error=None,
    ):
        """Calculate PID output value."""
        output = None
        elapsed_time = time.monotonic() - self.last_update_time
        if elapsed_time > self.update_intervall:
            if not current_value:
                current_value = self.input_fun()
            if set_point:
                self.set_point = set_point
            if not error:
                self.error = self.set_point - current_value
                if self.debug_out_fun or self.debug_out_print:
                    debug_out = (
                        "current_value: {current_value: > 7.2f}  "
                        "set_point: {set_point: > 7.2f}  "
                        "error: {error: > 7.2f}  "
                        "".format(
                            current_value=current_value,
                            set_point=self.set_point,
                            error=self.error,
                        )
                    )
                    if self.debug_out_fun:
                        self.debug_out_fun(debug_out)
                    if self.debug_out_print:
                        print(debug_out, end="")
            else:
                self.error = error
            output = self._update(current_value)
            self.output_fun(output)
            self.last_update_time = time.monotonic()
            print()
        return output
