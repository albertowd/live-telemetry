#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to keep some utility functions.

@author: albertowd
"""
from datetime import datetime
import ctypes.wintypes

import ac

ACD_FILE = None


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


def get_acd():
    """ Returns the global ACD file. """
    global ACD_FILE
    return ACD_FILE


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
        keys = data_log[0].__dict__.keys()
        csv.append(";".join(keys))
        
        # Create the each data row.
        for data in data_log:
            row = []
            data_dict = vars(data)
            for key in keys:
                row.append(str(data_dict[key]))
            csv.append(";".join(row))
    
    # Load the My Documents folder.
    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value            
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    
    with open("{}/Assetto Corsa/logs/LiveTelemetry_{}.log".format(buf.value, csv_name), "w") as w:
        w.write("\n".join(csv))


def update_acd(path):
    """ Updates the ACD car information. """
    log("Loading {} info...".format(ac.getCarName(0)))
    from lib.lt_acd import ACD
    global ACD_FILE
    ACD_FILE = ACD(path)
    log("Loaded correctly")
