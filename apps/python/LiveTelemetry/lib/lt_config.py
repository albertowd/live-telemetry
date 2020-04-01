#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to load and save app options.

@author: albertowd
"""

import configparser
import os

from lib.lt_util import get_docs_path, log


class Config(object):
    """ Singleton to handle configuration methods. """

    __configs = configparser.ConfigParser()

    def __init__(self, lt_version):
        """ Loads or creates the app configuration file. """
        if os.path.isfile("apps/python/LiveTelemetry/cfg.ini"):
            Config.__configs.read("apps/python/LiveTelemetry/cfg.ini")

        # If the config does not have it's version or is invalid, create a new one.
        try:
            config_version = self.get_version()
            if config_version != lt_version:
                log("Old config file. Could make things crash!")
                raise Exception("Old config file.")
        except:
            log("Creating new config file.")

            Config.__configs = configparser.ConfigParser()
            Config.__configs["About"] = {"Version": lt_version}

            self.set_option_active("Camber", True)
            self.set_option_active("Dirt", True)
            self.set_option_active("Height", True)
            self.set_option_active("Load", True)
            self.set_option_active("Logging", True)
            self.set_option_active("Pressure", True)
            self.set_option_active("Temps", True)
            self.set_option_active("Size", "FHD")
            self.set_option_active("Suspension", True)
            self.set_option_active("Tire", True)
            self.set_option_active("Wear", True)

            self.set_window_active("EN", False)
            self.set_window_active("FL", False)
            self.set_window_active("FR", False)
            self.set_window_active("RL", False)
            self.set_window_active("RR", False)

            h = 720
            w = 1280
            try:
                video = configparser.ConfigParser()
                video.read(
                    "{}/Assetto Corsa/cfg/video.ini".format(get_docs_path()))
                h = int(video.get("VIDEO", "HEIGHT"))
                w = int(video.get("VIDEO", "WIDTH"))
            except:
                log("Could not get 'cfg/video.ini' video options, using default 1280x720 resolution.")

            self.set_window_position("EN", [(w - 360) / 2, h - 51 - 160])
            self.set_window_position("FL", [10, 80])
            self.set_window_position("FR", [w - 360 - 10, 80])
            self.set_window_position("OP", [w - 200 - 50, (h - 110) / 2])
            self.set_window_position("RL", [10, h - 163 - 80])
            self.set_window_position("RR", [w - 360 - 10, h - 163 - 80])
            self.save_config()

    def __get_str(self, section, option):
        """ Returns an option. """
        return Config.__configs.get(section, option)

    def __set_str(self, section, option, value):
        """ Updates an option. """
        Config.__configs.set(section, option, value)

    def get_version(self):
        """ Returns the config file version. """
        return self.__get_str("About", "version")

    def get_window_position(self, name):
        """ Returns the position [x,y] of a window. """
        return [
            float(self.__get_str("Windows Positions", "{}_x".format(name))),
            float(self.__get_str("Windows Positions", "{}_y".format(name)))
        ]

    def is_option_active(self, name):
        """ Returns if a option is active. """
        return self.__get_str("Options", name) == "True"

    def is_window_active(self, name):
        """ Returns if a window is active. """
        return self.__get_str("Windows", name) == "True"

    def save_config(self):
        """ Writes the actual options on the configuration file. """
        cfg_file = open("apps/python/LiveTelemetry/cfg.ini", 'w')
        Config.__configs.write(cfg_file)
        cfg_file.close()

    def set_option_active(self, name, active):
        """ Updates if a option is active. """
        self.__set_str("Options", name, str(active))

    def set_window_active(self, name, active):
        """ Updates if a window is active. """
        self.__set_str("Windows", name, str(active))

    def set_window_position(self, name, position):
        """ Updates a window position. """
        self.__set_str("Windows Positions",
                       "{}_x".format(name), str(position[0]))
        self.__set_str("Windows Positions",
                       "{}_y".format(name), str(position[1]))
