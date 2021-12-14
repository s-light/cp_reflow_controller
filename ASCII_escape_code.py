#!/usr/bin/env python3
# coding=utf-8

"""
ASCII escape codes.

based on
    https://www.geeksforgeeks.org/print-colors-python-terminal/
and
    https://en.wikipedia.org/wiki/ANSI_escape_code
"""


def create_seq(control, esc="\033["):
    return lambda value="": "{esc}{value}{control}".format(
        esc=esc, value=value, control=control
    )


def create_color(color):
    return create_seq("m")(color)


class ASCIIControllsBase:
    """
    Base Class for ASCII Color and Control Characters.
    """

    esc = "\033["

    # @staticmethod
    # def create_seq(control, esc=esc):
    #     return lambda value: "{esc}{value}{control}".format(
    #         esc=esc, value=value, control=control
    #     )

    @classmethod
    def get_flat_list(cls, obj_dict=None):
        """Get a flattend list of all control characters in dict."""
        result = []
        if obj_dict is None:
            obj_dict = cls.__dict__
        # print("*"*42)
        # print("obj_dict", obj_dict)
        # print("*"*42)
        for attr_name, attr_value in obj_dict.items():
            if not attr_name.startswith("__"):
                # if type(attr_value) is str:
                #     value_str = attr_value.replace("\x1b", "\\x1b")
                # else:
                #     value_str = attr_value
                # print(
                #     "'{}' '{}': {}  "
                #     "".format(
                #         attr_name,
                #         type(attr_value),
                #         value_str,
                #     ),
                #     end=""
                # )
                if type(attr_value) is str:
                    # print(" STRING ")
                    result.append(attr_value)
                elif type(attr_value) is type:
                    # print(" TYPE ")
                    result.extend(cls.get_flat_list(attr_value.__dict__))
                else:
                    # print(" UNKNOWN ")
                    pass
        # print("*"*42)
        return result


class colors(ASCIIControllsBase):
    """
    ASCII Color and Control Characters.

    reset all colors with colors.reset;
    two sub classes
        fg for foreground
        bg for background;
    use as colors.subclass.colorname:
    `colors.fg.red`
    `colors.bg.green`
    the generics
    bold, disable, underline, reverse, strike through, invisible
    work with the main class:
    `colors.bold`
    """

    # reset = ASCIIControllsBase.esc + "0m"
    reset = create_color("0")
    bold = create_color("01")
    disable = create_color("02")
    underline = create_color("04")
    reverse = create_color("07")
    strikethrough = create_color("09")
    invisible = create_color("08")

    # class fg:
    #     """Forderground Colors."""
    #
    #     black = create_color("30m")
    #     red = create_color("31m")
    #     green = create_color("32m")
    #     orange = create_color("33m")
    #     blue = create_color("34m")
    #     purple = create_color("35m")
    #     cyan = create_color("36m")
    #     lightgrey = create_color("37m")
    #     darkgrey = create_color("90m")
    #     lightred = create_color("91m")
    #     lightgreen = create_color("92m")
    #     yellow = create_color("93m")
    #     lightblue = create_color("94m")
    #     pink = create_color("95m")
    #     lightcyan = create_color("96m")
    #
    # class bg:
    #     """Background Colors."""
    #
    #     black = create_color("40m")
    #     red = create_color("41m")
    #     green = create_color("42m")
    #     orange = create_color("43m")
    #     blue = create_color("44m")
    #     purple = create_color("45m")
    #     cyan = create_color("46m")
    #     lightgrey = create_color("47m")

    class fg:
        """Forderground Colors."""

        black = ASCIIControllsBase.esc + "30m"
        red = ASCIIControllsBase.esc + "31m"
        green = ASCIIControllsBase.esc + "32m"
        orange = ASCIIControllsBase.esc + "33m"
        blue = ASCIIControllsBase.esc + "34m"
        purple = ASCIIControllsBase.esc + "35m"
        cyan = ASCIIControllsBase.esc + "36m"
        lightgrey = ASCIIControllsBase.esc + "37m"
        darkgrey = ASCIIControllsBase.esc + "90m"
        lightred = ASCIIControllsBase.esc + "91m"
        lightgreen = ASCIIControllsBase.esc + "92m"
        yellow = ASCIIControllsBase.esc + "93m"
        lightblue = ASCIIControllsBase.esc + "94m"
        pink = ASCIIControllsBase.esc + "95m"
        lightcyan = ASCIIControllsBase.esc + "96m"

    class bg:
        """Background Colors."""

        black = ASCIIControllsBase.esc + "40m"
        red = ASCIIControllsBase.esc + "41m"
        green = ASCIIControllsBase.esc + "42m"
        orange = ASCIIControllsBase.esc + "43m"
        blue = ASCIIControllsBase.esc + "44m"
        purple = ASCIIControllsBase.esc + "45m"
        cyan = ASCIIControllsBase.esc + "46m"
        lightgrey = ASCIIControllsBase.esc + "47m"


class control(ASCIIControllsBase):
    """
    ASCII Cursor movement.

    these do not work under circuitpython

    use as:
    # move cursor up 5 lines
    control.cursor.up(5)
    """

    ED = erase_display = create_seq("J")
    EL = erase_line = create_seq("K")
    SU = scroll_up = create_seq("S")
    SD = scroll_down = create_seq("T")
    DSR = device_status_report = create_seq("n")("6")

    class cursor:
        CUU = up = create_seq("A")
        CUD = down = create_seq("B")
        CUF = forward = create_seq("C")
        CUB = back = create_seq("D")
        CNL = next_line = create_seq("E")
        CPL = previous_line = create_seq("F")
        CHA = horizontal_absolute = create_seq("G")
        CUP = position = create_seq("H")


##########################################


def filter_ASCII_controlls(data):
    """Remove ASCII controll characters."""
    code_list = []
    code_list.extend(colors.get_flat_list())
    code_list.extend(control.get_flat_list())
    for el in code_list:
        data = data.replace(el, "")
    return data


def test_filtering():
    """Test for filter_ASCII_controlls."""
    test_string = (
        colors.fg.lightblue
        + "Hello "
        + colors.fg.green
        + "World "
        + colors.fg.orange
        + ":-)"
        + colors.reset
    )
    print("test_string", test_string)
    test_filtered = filter_ASCII_controlls(test_string)
    print("test_filtered", test_filtered)


def test_control():
    """Test for control sequences."""
    import time

    test_string = (
        colors.fg.lightblue
        + "Hello "
        + colors.fg.green
        + "World "
        + colors.fg.orange
        + ":-)"
        + colors.reset
    )
    print("test_string", test_string)
    print("test_string", test_string)
    print("test_string", test_string)
    time.sleep(1)
    test_string = (
        control.cursor.previous_line(2)
        + "WOOO"
        + control.cursor.next_line(1)
        + control.erase_line()
        + ":-)"
    )
    print(test_string)
