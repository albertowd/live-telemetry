#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to load and save app options.

@author: albertowd
"""

from configparser import ConfigParser, Error as ConfigError
from math import floor
from os import path
from sys import exc_info

from lib.lt_util import get_docs_path, log


class Config:
    """ Singleton to handle configuration methods. """

    def __init__(self, lt_version: str) -> None:
        """ Loads or creates the app configuration file. """

        self.__base_path = path.join(path.dirname(path.realpath(__file__)), "..", "cfg")
        settings_path = path.join(self.__base_path, "conf.ini")

        self.__configs = ConfigParser(allow_no_value=True, comment_prefixes=(";","#","/","_"), empty_lines_in_values=False, inline_comment_prefixes=(";","#","/","_"), strict=False)
        if path.isfile(settings_path):
            self.__configs.read(settings_path)
        else:
            log("Settings file not found. Using default values instead!")

        # If the config does not have it's version or is invalid, create a new one.
        try:
            config_version = self.get_version()
            if config_version != lt_version:
                log("Version missmatch. Using default values instead!")
                raise ValueError("Old config file.")
        except (ConfigError, KeyError, ValueError):
            log("Creating new config file.")
            self.__create_default_config(lt_version)
            self.save_config()

    def __create_default_config(self, lt_version: str) -> None:
        """ Initializes the in-memory config with default sections and values. """
        self.__configs["About"] = {"Version": lt_version}
        self.__configs["Options"] = {}
        self.__configs["Windows"] = {}
        self.__configs["Windows Positions"] = {}

        self.__set_default_options()
        self.__set_default_windows_active()
        height, width = self.__read_screen_resolution()
        self.__set_default_window_positions(height, width)

    def __set_default_options(self) -> None:
        """ Writes the default option values. """
        self.set_option("BoostBar", True)
        self.set_option("Camber", True)
        self.set_option("Dirt", True)
        self.set_option("Height", True)
        self.set_option("Load", True)
        self.set_option("Lock", False)
        self.set_option("Logging", False)
        self.set_option("Pressure", True)
        self.set_option("RPMPower", True)
        self.set_option("Size", "FHD")
        self.set_option("Suspension", True)
        self.set_option("Temps", True)
        self.set_option("Tire", True)
        self.set_option("Wear", True)

    def __set_default_windows_active(self) -> None:
        """ Marks all windows active by default.

        AC restores apps from its own app-bar persistence after a version bump,
        but its activation listener does not fire for auto-restored apps — so
        a False default here would surface as invisible widgets.
        """
        self.set_window_active("EN", True)
        self.set_window_active("FL", True)
        self.set_window_active("FR", True)
        self.set_window_active("RL", True)
        self.set_window_active("RR", True)

    @staticmethod
    def __read_screen_resolution() -> (int, int):
        """ Reads (height, width) from AC's video.ini, falling back to 1080x1920. """
        height = 1080
        width = 1920
        docs_path = get_docs_path()
        if len(docs_path) > 0:
            try:
                video = ConfigParser()
                video.read("{}/Assetto Corsa/cfg/video.ini".format(docs_path))
                height = int(video.get("VIDEO", "HEIGHT")) if video.has_option(
                    "VIDEO", "HEIGHT") else height
                width = int(video.get("VIDEO", "WIDTH")) if video.has_option(
                    "VIDEO", "WIDTH") else width
            except (ConfigError, OSError, ValueError):
                log("Could not get 'cfg/video.ini' video options, using default 1280x720 resolution:")
                for info in exc_info():
                    log(info)
        return height, width

    def __set_default_window_positions(self, height: int, width: int) -> None:
        """ Writes the default window positions for the given screen size. """
        self.set_window_position("EN", [floor((width - 360) / 2), height - 51 - 160])
        self.set_window_position("FL", [10, 80])
        self.set_window_position("FR", [width - 360 - 10, 80])
        self.set_window_position("OP", [width - 395 - 50, floor((height - 195) / 2)])
        self.set_window_position("RL", [10, height - 163 - 80])
        self.set_window_position("RR", [width - 360 - 10, height - 163 - 80])

    def __get_str(self, section: str, option: str) -> str:
        """ Returns an option. """
        return self.__configs.get(section, option)

    def __set_str(self, section: str, option: str, value) -> None:
        """ Updates an option. """
        self.__configs.set(section, option, str(value))

    def get_bool_option(self, name: str) -> bool:
        """ Returns a option value as a boolean. """
        return self.__get_str("Options", name) == "True"

    def get_option(self, name: str) -> str:
        """ Returns a option value as a string. """
        return self.__get_str("Options", name)

    def get_version(self) -> str:
        """ Returns the config file version. """
        return self.__get_str("About", "version")

    def get_window_position(self, name: str) -> [int]:
        """ Returns the position [x,y] of a window. """
        return [
            int(self.__get_str("Windows Positions", "{}_x".format(name))),
            int(self.__get_str("Windows Positions", "{}_y".format(name)))
        ]

    def is_window_active(self, name: str) -> bool:
        """ Returns if a window is active. """
        return self.__get_str("Windows", name) == "True"

    def save_config(self) -> None:
        """ Writes the actual options on the configuration file. """
        with open(path.join(self.__base_path, "conf.ini"), "w", encoding="utf-8") as cfg_file:
            self.__configs.write(cfg_file)

    def set_option(self, name: str, value) -> None:
        """ Updates an option value. """
        self.__set_str("Options", name, str(value))

    def set_window_active(self, name: str, active: bool) -> None:
        """ Updates if a window is active. """
        self.__set_str("Windows", name, str(active))

    def set_window_position(self, name: str, position: [int]) -> None:
        """ Updates a window position. """
        self.__set_str("Windows Positions",
                       "{}_x".format(name), str(int(position[0])))
        self.__set_str("Windows Positions",
                       "{}_y".format(name), str(int(position[1])))
