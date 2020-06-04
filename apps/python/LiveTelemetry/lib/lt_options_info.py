#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to view and change app options.

@author: albertowd
"""

from math import floor

import ac

from lib.lt_components import BoxComponent
from lib.lt_colors import Colors
from lib.lt_config import Config


class OptionsInfo(object):
    """ Options info to change app options while in game. """

    def __init__(self, configs: Config):
        """ Default constructor. """
        self.__buttons = {}
        self.__options = {
            "Camber": configs.get_bool_option("Camber"),
            "Dirt": configs.get_bool_option("Dirt"),
            "Height": configs.get_bool_option("Height"),
            "Load": configs.get_bool_option("Load"),
            "Lock": configs.get_bool_option("Lock"),
            "Logging": configs.get_bool_option("Logging"),
            "Pressure": configs.get_bool_option("Pressure"),
            "RPMPower": configs.get_bool_option("RPMPower"),
            "Size": configs.get_option("Size"),
            "Suspension": configs.get_bool_option("Suspension"),
            "Temps": configs.get_bool_option("Temps"),
            "Tire": configs.get_bool_option("Tire"),
            "Wear": configs.get_bool_option("Wear")
        }

        self.__window_id = ac.newApp("Live Telemetry")
        ac.setIconPosition(self.__window_id, 0, -10000)
        title = "Live Telemetry {}".format(configs.get_version())
        ac.setTitle(self.__window_id, title)

        position = configs.get_window_position("OP")
        ac.setPosition(self.__window_id, *position)

        ac.setSize(self.__window_id, 395, 195)

        for index, name in enumerate(sorted(self.__options.keys())):
            text = str(name) if name != "Size" else self.__options[name]
            self.__buttons[name] = ac.addButton(self.__window_id, text)
            x = 30 + (floor(index / 4) * 85)
            y = 30 + (floor(index % 4) * 35)
            ac.setPosition(self.__buttons[name], x, y)
            ac.setSize(self.__buttons[name], 80, 30)
            ac.setFontAlignment(self.__buttons[name], "center")
            self.set_option(name, self.__options[name])

    def get_button_id(self, name):
        """ Returns a button id. """
        return self.__buttons[name]

    def get_option(self, name):
        """ Returns an option value. """
        return self.__options[name]

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def resize(self, size):
        """ Resizes the window. """
        ac.setText(self.__buttons["Size"], size)

    def set_option(self, name, value):
        """ Updates an option value. """
        self.__options[name] = value
        if name != "Size":
            color = Colors.red if value else Colors.white
            ac.setFontColor(self.__buttons[name], *color)
