#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to view and change app options.

@author: albertowd
"""

from math import floor

import ac

from lib.lt_colors import Colors
from lib.lt_config import Config
from lib.sim_info import info


class OptionsInfo:
    """ Options info to change app options while in game. """

    def __init__(self, configs: Config):
        """ Default constructor. """
        self.__buttons = {}
        bool_keys = ("Camber", "Dirt", "Height", "Load", "Lock", "Logging",
                     "Pressure", "RPMPower", "Suspension", "Temps", "Tire", "Wear")
        self.__options = {key: configs.get_bool_option(key) for key in bool_keys}
        self.__options["Size"] = configs.get_option("Size")

        # Only expose BoostBar toggle for turbocharged cars.
        if info.static.maxTurboBoost > 0.0:
            self.__options["BoostBar"] = configs.get_bool_option("BoostBar")

        self.__window_id = ac.newApp("Live Telemetry")
        ac.setIconPosition(self.__window_id, 0, -10000)
        title = "Live Telemetry {}".format(configs.get_version())
        ac.setTitle(self.__window_id, title)

        position = configs.get_window_position("OP")
        ac.setPosition(self.__window_id, *position)

        ac.setSize(self.__window_id, 395, 195)

        # Action buttons live outside the toggle-options dict: they
        # don't carry a persisted bool and so must skip the colouring
        # / set_option path used by the regular toggles.
        action_buttons = ("Reset",)
        button_names = sorted(self.__options.keys()) + list(action_buttons)

        for index, name in enumerate(button_names):
            text = str(name) if name != "Size" else self.__options[name]
            self.__buttons[name] = ac.addButton(self.__window_id, text)
            x = 30 + (floor(index / 4) * 85)
            y = 30 + (floor(index % 4) * 35)
            ac.setPosition(self.__buttons[name], x, y)
            ac.setSize(self.__buttons[name], 80, 30)
            ac.setFontAlignment(self.__buttons[name], "center")
            if name in self.__options:
                self.set_option(name, self.__options[name])

    def get_button_id(self, name):
        """ Returns a button id, or None if the option button was not created. """
        return self.__buttons.get(name)

    def get_option(self, name):
        """ Returns an option value, or None if the option is not exposed. """
        return self.__options.get(name)

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def reset_position(self, configs) -> None:
        """ Repositions the options window to the persisted default.
        OP uses a TL anchor so the saved coords are already the AC
        setPosition value. """
        pos = configs.get_window_position("OP")
        ac.setPosition(self.__window_id, *pos)

    def resize(self, size):
        """ Resizes the window. """
        ac.setText(self.__buttons["Size"], size)

    def set_option(self, name, value):
        """ Updates an option value. """
        self.__options[name] = value
        if name != "Size":
            color = Colors.red if value else Colors.white
            ac.setFontColor(self.__buttons[name], *color)
