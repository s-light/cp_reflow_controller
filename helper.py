#!/usr/bin/env python3
# coding=utf-8

"""
collection of some small helper functions
"""


def limit(value, value_min, value_max):
    return max(min(value_max, value), value_min)
