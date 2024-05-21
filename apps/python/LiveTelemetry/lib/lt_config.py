#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to load and save app options.

@author: albertowd
"""

from configparser import ConfigParser
from math import floor
from os import path
from sys import exc_info

from lib.lt_util import get_docs_path, log


class Config:
    """ Singleton to handle configuration methods. """

    def __init__(self, lt_version: str) -> None:
        """ Loads or creates the app configuration file. """

        docs_path = get_docs_path()
        self.__configs = ConfigParser()
        if path.isfile("{}/Assetto Corsa/cfg/apps/LiveTelemetry.ini".format(docs_path)):
            self.__configs.read("{}/Assetto Corsa/cfg/apps/LiveTelemetry.ini".format(docs_path))

        # If the config does not have it's version or is invalid, create a new one.
        try:
            config_version = self.get_version()
            if config_version != lt_version:
                log("Old config file. Could make things crash!")
                raise Exception("Old config file.")
        except:
            log("Creating new config file.")
            self.__configs["About"] = {"Version": lt_version}
            self.__configs["Options"] = {}
            self.__configs["Windows"] = {}
            self.__configs["Windows Positions"] = {}

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

            self.set_window_active("EN", False)
            self.set_window_active("FL", False)
            self.set_window_active("FR", False)
            self.set_window_active("RL", False)
            self.set_window_active("RR", False)

            h = 720
            w = 1280

            if len(docs_path) > 0:
                try:
                    video = ConfigParser()
                    video.read(
                        "{}/Assetto Corsa/cfg/video.ini".format(docs_path))
                    h = int(video.get("VIDEO", "HEIGHT")) if video.has_option(
                        "VIDEO", "HEIGHT") else 720
                    w = int(video.get("VIDEO", "WIDTH")) if video.has_option(
                        "VIDEO", "WIDTH") else 1280
                except:
                    log("Could not get 'cfg/video.ini' video options, using default 1280x720 resolution:")
                    for info in exc_info():
                        log(info)

            self.set_window_position(
                "EN", [floor((w - 360) / 2), h - 51 - 160])
            self.set_window_position("FL", [10, 80])
            self.set_window_position("FR", [w - 360 - 10, 80])
            self.set_window_position(
                "OP", [w - 395 - 50, floor((h - 195) / 2)])
            self.set_window_position("RL", [10, h - 163 - 80])
            self.set_window_position("RR", [w - 360 - 10, h - 163 - 80])
            self.save_config()

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
        docs_path = get_docs_path()
        with open("{}/Assetto Corsa/cfg/apps/LiveTelemetry.ini".format(docs_path), "w", encoding="utf-8") as cfg_file:
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
