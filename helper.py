#!/usr/bin/env python3
# coding=utf-8

"""
collection of some small helper functions
"""


def is_number(s):
    """
    Return true if string is a number.

    based on
    https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float
    """
    try:
        float(s)
    except ValueError:
        # return NaN
        return False
    else:
        return True


def limit(value, value_min, value_max):
    return max(min(value_max, value), value_min)


def round_up(value, round_to=10):
    """round up to next `round_to` value.
    based on: https://stackoverflow.com/a/14092788/574981
    """
    return value + (-value) % round_to


def round_nearest(value, multiple_of):
    """round to `multiple_of` value.
    based on: https://stackoverflow.com/a/28425782/574981
    """
    return round(value / multiple_of) * multiple_of
