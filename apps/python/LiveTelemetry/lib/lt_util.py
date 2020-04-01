#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to keep some utility functions.

@author: albertowd
"""
from datetime import datetime
import ctypes.wintypes
import os
import platform
import sys

import ac


class WheelPos(object):
    """ Keep useful information about the wheel position. """

    def __init__(self, index):
        """ Construct the properties with the wheel index (0-3). """
        self.__index = index
        self.__is_front = (index // 2) == 0
        self.__is_left = (index % 2) == 0
        self.__name = "{}{}".format(
            "F" if self.__is_front else "R", "L" if self.__is_left else "R")

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


def clear_logs():
    """ Clears saved CSV data files. """
    my_docs = get_docs_path()
    if os.path.isfile("{}/Assetto Corsa/logs/LiveTelemetry_EN.csv".format(my_docs)):
        os.unlink("{}/Assetto Corsa/logs/LiveTelemetry_EN.csv".format(my_docs))
    if os.path.isfile("{}/Assetto Corsa/logs/LiveTelemetry_FL.csv".format(my_docs)):
        os.unlink("{}/Assetto Corsa/logs/LiveTelemetry_FL.csv".format(my_docs))
    if os.path.isfile("{}/Assetto Corsa/logs/LiveTelemetry_FR.csv".format(my_docs)):
        os.unlink("{}/Assetto Corsa/logs/LiveTelemetry_FR.csv".format(my_docs))
    if os.path.isfile("{}/Assetto Corsa/logs/LiveTelemetry_RL.csv".format(my_docs)):
        os.unlink("{}/Assetto Corsa/logs/LiveTelemetry_RL.csv".format(my_docs))
    if os.path.isfile("{}/Assetto Corsa/logs/LiveTelemetry_RR.csv".format(my_docs)):
        os.unlink("{}/Assetto Corsa/logs/LiveTelemetry_RR.csv".format(my_docs))


def color_interpolate(c_1, c_2, perc):
    """ Interpolate between two colors. """
    c_r = c_1[0] + (c_2[0] - c_1[0]) * perc
    c_g = c_1[1] + (c_2[1] - c_1[1]) * perc
    c_b = c_1[2] + (c_2[2] - c_1[2]) * perc
    c_a = c_1[3] + (c_2[3] - c_1[3]) * perc
    return [c_r, c_g, c_b, c_a]


def get_docs_path():
    """Load the My Documents folder path."""
    try:
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return buf.value
    except:
        log("Could not load My Documents folder")
        for index in range(len(sys.exc_info())):
            log(sys.exc_info()[index])
        return ""


def log(message, console=True, app_log=True):
    """ Logs a message on the log and console. """
    time_str = datetime.utcnow().strftime("%H:%M:%S.%f")
    formated = "[LT][{}] {}".format(time_str, message)

    if console:
        ac.console(formated)

    if app_log:
        ac.log(formated)


def export_saved_log(data_log, csv_name):
    """ Export saved data to a CSV file. """
    csv = []

    # Verifies the log length.
    if(len(data_log) > 0):
        # Create the header row
        keys = sorted(data_log[0].__dict__.keys())
        csv.append(";".join(keys))

        # Create the each data row.
        for data in data_log:
            row = []
            data_dict = vars(data)
            for key in keys:
                row.append(str(data_dict[key]))
            csv.append(";".join(row))

    # Load the My Documents folder.
    docs_path = get_docs_path()

    if len(docs_path) > 0:
        with open("{}/Assetto Corsa/logs/LiveTelemetry_{}.csv".format(docs_path, csv_name), "w") as w:
            w.write("\n".join(csv))
    else:
        with open("LiveTelemetry_{}.csv".format(csv_name), "w") as w:
            w.write("\n".join(csv))
