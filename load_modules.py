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

# import sys
import os

# import pkgutil
# import importlib

##########################################
# special functions


def print_directory(path, tabs=0):
    # https://learn.adafruit.com/micropython-hardware-sd-cards/tdicola-circuitpython#list-files-2976357-28
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "    "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print("{0:<40} Size: {1:>10}".format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)


def isclass(object):
    """
    Return true if the object is a class.
    source:
    https://stackoverflow.com/questions/395735/how-to-check-whether-a-variable-is-a-class-or-not#comment83233256_10123520
    """
    return isinstance(object, type)


def ismoduleclass(object):
    """
    Return true if the object is the module class.
    """
    return "module" in repr(object)


def get_module_custom_classes(module, base_class=None):
    classes = {}
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        # print(
        #     "attribute '{attribute_name}': {attribute}\n"
        #     "  isclass: {isclass}"
        #     "".format(
        #         attribute_name=attribute_name,
        #         attribute=attribute,
        #         isclass=isclass(attribute),
        #     )
        # )
        if isclass(attribute):
            if base_class:
                # print("  issubclass(attribute)", issubclass(attribute, base_class))
                if issubclass(attribute, base_class):
                    classes[attribute_name] = attribute
            elif not ismoduleclass(attribute):
                # ^ exclude module class
                classes[attribute_name] = attribute
    return classes


def _load_all_modules(path, names):
    """Load all modules in path.

    usage:
        # Load all modules in the current directory.
        load_all_modules(__file__,__name__)

    based on
        http://stackoverflow.com/a/25459405/574981
        from Daniel Kauffman
    and circuitpython variant
        https://forum.micropython.org/viewtopic.php?p=29226&#p29226
        https://github.com/pewpew-game/game-menu/blob/master/main.py

    converted to circuitpython variant
    """

    # print("path", path)
    # print("names", names)
    # print("[os.path.dirname(path)]", [os.path.dirname(path)])
    # print("os.stat(path)", os.stat(path))
    # print_directory(names)

    module_names = []
    module_infos = {}
    for name in os.listdir(path):
        if name.endswith(".py") and name != "main.py" and name != "__init__.py":
            # print("name", name)
            module_name = name[:-3]
            try:
                filename = path + "." + module_name
                module = __import__(filename)
                # print("{} imported.".format(filename))
            except Exception as e:
                raise e
            else:
                module_names.append(module_name)
                module_infos[module_name] = {
                    "name": module_name,
                    "filename": filename,
                    "module": getattr(module, module_name),
                }

    # # For each module in the current directory...
    # for importer, module_name, is_package in pkgutil.iter_modules(
    #     [os.path.dirname(path)]
    # ):
    #     # print("importing:", names + '.' + module_name)
    #     # Import the module.
    #     importlib.import_module(names + "." + module_name)
    #    module_names.append(module_name)

    # return module_names, module_infos
    return module_infos


def instantiate_classes(module_classes, class_instances={}):
    """instantiate specific class."""
    # print("module_classes", module_classes)
    # create a Object Instance from Class
    for class_name, class_obj in module_classes.items():
        if class_name not in class_instances:
            class_instances[class_name] = class_obj()
    return class_instances


def instantiate_classes_for_modules(module_infos, class_instances={}):
    for module_name, module_info in module_infos.items():
        # print("module_info", module_info)
        # print("module_info.module", module_info["module"])
        module_classes = get_module_custom_classes(module_info["module"])
        instantiate_classes(module_classes, class_instances=class_instances)
        # print("class_instances", class_instances)
    return class_instances


##########################################
# package init

# Load all modules in the current directory.
# load_all_modules(__file__, __name__)


def load_all_submodules(filename=__file__, modulbasepath=__name__):
    """Load all submodules in this directory."""
    module_infos = _load_all_modules(modulbasepath, filename)
    return module_infos


def load_all_submodules_and_instantiate_all_classes(
    filename=__file__, modulbasepath=__name__
):
    """Load all submodules in this directory and instantiate all found classes in them."""
    module_infos = load_all_submodules(filename=filename, modulbasepath=modulbasepath)
    # print("module_infos", module_infos)
    class_instances = instantiate_classes_for_modules(module_infos)
    return module_infos, class_instances


##########################################
# classes

##########################################
