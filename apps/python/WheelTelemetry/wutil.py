"""
Module to keep some util functions.
"""
import ac
from wcolors import Colors


def color_interpolate(c_1, c_2, perc):
    """ Interpolate between two colors. """
    c_r = c_1[0] + (c_2[0] - c_1[0]) * perc
    c_g = c_1[1] + (c_2[1] - c_1[1]) * perc
    c_b = c_1[2] + (c_2[2] - c_1[2]) * perc
    c_a = c_1[3] + (c_2[3] - c_1[3]) * perc
    return [c_r, c_g, c_b, c_a]


def psi_color(compound, is_front, psi):
    """ Calc pressure color. """
    color = Colors.red
    ref = 29.0
    perc = psi / ref
    if compound is "Street":
        if perc < 0.85:
            color = Colors.blue
        elif perc < 0.95:
            color = color_interpolate(Colors.blue, Colors.green, (perc - 0.85) / 0.1)
        elif perc < 1.05:
            color = Colors.green
        elif perc < 1.15:
            color = color_interpolate(Colors.green, Colors.red, (perc - 1.05) / 0.1)
    return color


def temp_color(compound, is_front, temp):
    """ Calc tyre temperature color. """
    color = Colors.red
    if compound is "Street":
        if temp < 40.0:
            color = Colors.blue
        elif temp < 75.0:
            color = color_interpolate(Colors.blue, Colors.green, (temp - 40.0) / 35.0)
        elif temp < 110.0:
            color = Colors.green
        elif temp < 140.0:
            color = color_interpolate(Colors.green, Colors.red, (temp - 110.0) / 30.0)

    return color


def log(message, console=True, app_log=True):
    """ Logs a message on the log and console. """
    formated = "[WT] {}".format(message)
    if console:
        ac.console(formated)
    if app_log:
        ac.log(formated)
