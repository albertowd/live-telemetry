#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to keep some utility functions.

@author: albertowd
"""

import ac

from lt_colors import Colors


class WheelPos(object):
    """ Keep useful information about the wheel position. """

    def __init__(self, index):
        """ Construct the properties with the wheel index (0-3). """
        self.__index = index
        self.__is_front = (index // 2) == 0
        self.__is_left = (index % 2) == 0
        self.__name = "{}{}".format("F" if self.__is_front else "R", "L" if self.__is_left else "R")
    
    def index(self):
        """ Return the wheel index. """
        return self.__index
    
    def is_front(self):
        """ Returns if the wheel is on front. """
        return self.__is_front
    
    def name(self):
        """ Returns the name of wheel position. """
        return self.__name
    
    def is_left(self):
        """ Returns if the wheel is on the left side. """
        return self.__is_left


def color_interpolate(c_1, c_2, perc):
    """ Interpolate between two colors. """
    c_r = c_1[0] + (c_2[0] - c_1[0]) * perc
    c_g = c_1[1] + (c_2[1] - c_1[1]) * perc
    c_b = c_1[2] + (c_2[2] - c_1[2]) * perc
    c_a = c_1[3] + (c_2[3] - c_1[3]) * perc
    return [c_r, c_g, c_b, c_a]


def temp_color(compound, is_front, temp):
    """ Calculates tyre temperature color. """
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
    formated = "[LT] {}".format(message)
    
    if console:
        ac.console(formated)

    if app_log:
        ac.log(formated)
