#!/usr/bin/env python
# coding=utf-8

"""
profile base class.

    generates a test profile.

    history:
        see git commits

    todo:
        ~ all fine :-)
"""

import sys
import importlib
import os
import pkgutil

##########################################
# globals

profile_list = []


##########################################
# special functions


def _load_all_modules(path, names):
    """Load all modules in path.

    usage:
        # Load all modules in the current directory.
        load_all_modules(__file__,__name__)

    based on
        http://stackoverflow.com/a/25459405/574981
        from Daniel Kauffman

    """
    module_names = []
    # For each module in the current directory...
    for importer, module_name, is_package in pkgutil.iter_modules(
        [os.path.dirname(path)]
    ):
        # print("importing:", names + '.' + module_name)
        # Import the module.
        importlib.import_module(names + "." + module_name)
        module_names.append(module_name)

    return module_names


##########################################
# package init

# Load all modules in the current directory.
# load_all_modules(__file__, __name__)


def load_all_submodules():
    """Load all submodules in this directory."""
    # Load all modules in the current directory.
    profile_list = _load_all_modules(__file__, __name__)
    return profile_list


##########################################
# functions


##########################################
# classes


class Profile(object):
    """Name of Profile - Include Manufacture"""

    title = __doc__
    alloy = "alloy name / description"
    melting_point = 0
    reference = "url to manufacture datasheet"
    # this profile steps contain the soldering profile
    steps = [
        {
            "stage": "preheat",
            "duration": 210,
            "temp_target": 150,
        },
        {
            "stage": "soak",
            "duration": 90,
            "temp_target": 200,
        },
        {
            "stage": "reflow",
            "duration": 40,
            "temp_target": 245,
        },
        {
            "stage": "cool",
            "duration": 70,
            "temp_target": 0,
        },
    ]

    def __init__(self):
        """Init profile."""


##########################################
if __name__ == "__main__":

    print(42 * "*")
    print("Python Version: " + sys.version)
    print(42 * "*")
    print(__doc__)
    print(42 * "*")
    print("This Module has no stand alone functionality.")
    print(42 * "*")

##########################################
