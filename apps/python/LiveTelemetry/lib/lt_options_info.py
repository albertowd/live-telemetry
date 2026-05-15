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
        # BatteryBar is tri-state (AUTO / ON / OFF). Unlike Size, the
        # button face stays on the static "Battery" label and the
        # current mode is read from the font colour instead (yellow
        # AUTO, red ON, white OFF).
        self.__options["BatteryBar"] = configs.get_option("BatteryBar")

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

        # Size's button face shows its current value (e.g. "FHD"),
        # BatteryBar uses a friendly static label, and everything else
        # falls back to the option key as the button text.
        custom_labels = {"BatteryBar": "Battery"}
        for index, name in enumerate(button_names):
            if name == "Size":
                text = self.__options[name]
            else:
                text = custom_labels.get(name, str(name))
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
        if name == "Size":
            return
        if name == "BatteryBar":
            # Button face stays on the static "Battery" label — the
            # current mode is encoded in the font colour: yellow AUTO
            # (default, detector decides), red ON (force visible),
            # white OFF (hidden regardless).
            if value == "ON":
                color = Colors.red
            elif value == "OFF":
                color = Colors.white
            else:
                color = Colors.yellow
            ac.setFontColor(self.__buttons[name], *color)
            return
        color = Colors.red if value else Colors.white
        ac.setFontColor(self.__buttons[name], *color)
