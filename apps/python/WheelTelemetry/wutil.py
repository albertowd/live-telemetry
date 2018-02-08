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

def psi_color(compound, psi):
    """ Calc pressure color. """
    color = Colors.red
    if compound is "Street":
        if psi < 21.0:
            color = Colors.blue
        elif psi < 23.0:
            color = color_interpolate(Colors.blue, Colors.green, (psi - 21.0) / 2.0)
        elif psi < 25.0:
            color = Colors.green
        elif psi < 27.0:
            color = color_interpolate(Colors.green, Colors.red, (psi - 25.0) / 2.0)
    return color

def temp_color(compound, temp):
    """ Calc tyre temperature color. """
    color = Colors.red
    if compound is "Street":
        if temp < 65.0:
            color = Colors.blue
        elif temp < 75.0:
            color = color_interpolate(Colors.blue, Colors.green, (temp - 65.0) / 10.0)
        elif temp < 85.0:
            color = Colors.green
        elif temp < 95.0:
            color = color_interpolate(Colors.green, Colors.red, (temp - 85.0) / 10.0)
    elif compound is "Semi Slick":
        pass
    elif compound is "Slick Soft":
        pass
    elif compound is "Slick Medium":
        pass
    elif compound is "Slick Hard":
        pass

    return color

def log(message, console=True, app_log=True):
    """ Logs a message on the log and console. """
    formated = "[WT] {}".format(message)
    if console:
        ac.console(formated)
    if app_log:
        ac.log(formated)
