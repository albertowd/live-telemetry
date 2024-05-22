#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one engine infos from car and draw on screen.

@author: albertowd
"""
import copy

import ac

from lib.lt_colors import Colors
from lib.lt_components import BoostBar, BoxComponent, RPMPower
from lib.sim_info import info


class Data:
    """ Data object to keep values between updates. """

    def __init__(self):
        self.max_power = 0.0
        self.max_rpm = 0.0
        self.max_turbo_boost = 0.0
        self.rpm = 0.0
        self.timestamp = 0
        self.turbo_boost = 0.0

    def update(self, info_arg):
        """ Update the default values from the car engine. """
        self.max_power = info_arg.static.maxPower
        self.max_rpm = info_arg.static.maxRpm
        self.max_turbo_boost = info_arg.static.maxTurboBoost
        self.rpm = info_arg.physics.rpms
        self.timestamp = info_arg.graphics.iCurrentTime
        self.turbo_boost = info_arg.physics.turboBoost


class EngineInfo:
    """ Engine info to draw and update. """

    def __init__(self, acd, configs):
        """ Default constructor. """
        self.__active = False
        self.__data = Data()
        self.__data_log = []
        self.__info = info
        self.__options = {
            "BoostBar": configs.get_bool_option("BoostBar"),
            "Logging": configs.get_bool_option("Logging"),
            "RPMPower": configs.get_bool_option("RPMPower")
        }
        self.__window_id = ac.newApp("Live Telemetry Engine")
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        position = configs.get_window_position("EN")
        ac.setPosition(self.__window_id, *position)

        size = configs.get_option("Size")
        mult = BoxComponent.resolution_map[size]
        ac.setSize(self.__window_id, 512 * mult, 85 * mult)

        self.__components = []
        self.__components.append(BoostBar(acd, size, self.__window_id))
        self.__components.append(RPMPower(acd, size, self.__window_id))

        # Only starts to draw after the setup.
        self.set_active(configs.is_window_active("EN"))

    def get_data_log(self):
        """ Returns the saved data from the session. """
        return self.__data_log

    def get_option(self, name):
        """ Returns an option value. """
        return self.__options[name]

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def has_data_logged(self):
        """Returns if the info has data logged."""
        return len(self.__data_log) > 0

    def is_active(self):
        """ Returns window status. """
        return self.__active

    def draw(self, delta_t: float):
        """ Draws all info on screen. """
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        for component in self.__components:
            if self.__options[type(component).__name__] is True:
                ac.glColor4f(*Colors.white)
                component.draw(self.__data, delta_t)
        ac.glColor4f(*Colors.white)

    def resize(self, resolution):
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 85 * mult)
        for component in self.__components:
            component.resize(resolution)

    def set_active(self, active):
        """ Toggles the window status. """
        self.__active = active

    def set_option(self, name, value):
        """ Updates an option value. """
        self.__options[name] = value

    def update(self, delta_t: float):
        """ Updates the engine information. """
        self.__data.update(self.__info)
        if self.__options["Logging"] is True:
            self.__data_log.append(copy.copy(self.__data))
