#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to load and save app options.

@author: albertowd
"""

import configparser
import os


class Config(object):
    """ Singleton to handle configuration methods. """

    __configs = configparser.ConfigParser()

    def __init__(self):
        self.load_config()

    def load_config(self):
        """ Loads or creates the app configuration file. """
        if os.path.isfile("apps/python/WheelTelemetry/cfg.ini"):
            Config.__configs.read("apps/python/WheelTelemetry/cfg.ini")
        else:
            Config.__configs["Windows"] = { "FL": "False", "FR": "False", "RL": "False", "RR": "False", "SIZE": "HD"}
            Config.__configs["Positions"] = {"FL_x": "100", "FL_y": "100", "FR_x": "668", "FR_y": "100", "RL_x": "100", "RL_y": "364", "RR_x": "668", "RR_y": "364"}

    def get_resolution(self):
        """ Returns the windows resolution. """
        return self.get_str("Windows", "SIZE")

    def get_str(self, section, option):
        """ Returns an option. """
        return Config.__configs.get(section, option)

    def get_x(self, wheel):
        """ Returns the x position of window. """
        return float(self.get_str("Positions", "{}_x".format(wheel.name())))

    def get_y(self, wheel):
        """ Returns the y position of window. """
        return float(self.get_str("Positions", "{}_y".format(wheel.name())))

    def is_active(self, wheel):
        """ Returns if window is active. """
        return bool(self.get_str("Windows", wheel.name()))

    def save_config(self):
        """ Writes the actual options on the configuration file. """
        cfg_file = open("apps/python/WheelTelemetry/cfg.ini", 'w')
        Config.__configs.write(cfg_file)
        cfg_file.close()

    def set_active(self, wheel, active):
        """ Updates if window is active. """
        self.set_str("Windows", wheel.name(), str(active))

    def set_position(self, wheel, pos_x, pos_y):
        """ Updates window position. """
        self.set_str("Positions", "{}_x".format(wheel.name()), str(pos_x))
        self.set_str("Positions", "{}_y".format(wheel.name()), str(pos_y))

    def set_str(self, section, option, value):
        """ Updates an option. """
        Config.__configs.set(section, option, value)
