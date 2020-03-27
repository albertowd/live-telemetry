#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one engine infos from car and draw on screen.
"""
import copy

import ac

from lib.lt_colors import Colors
from lib.lt_components import BoxComponent, RPMPower
from lib.sim_info import info


class Data(object):

    def __init__(self):
        self.max_power = 0.0
        self.max_rpm = 0.0
        self.max_torque = 0.0
        self.rpm = 0.0
        self.timestamp = 0

    def update(self, info):
        self.max_power = info.static.maxPower
        self.max_rpm = info.static.maxRpm
        self.max_torque = info.static.maxTorque
        self.rpm = info.physics.rpms
        self.timestamp = info.graphics.iCurrentTime


class EngineInfo(object):
    """ Engine info to draw and update. """

    def __init__(self, configs):
        """ Default constructor. """
        self.__active = False
        self.__data = Data()
        self.__data_log = []
        self.__logging = False
        self.__info = info
        self.__window_id = ac.newApp("Live Telemetry Engine")
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        pos_x = configs.get_engine_x()
        pos_y = configs.get_engine_y()
        ac.setPosition(self.__window_id, pos_x, pos_y)

        resolution = configs.get_resolution()
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 85 * mult)

        self.__components = []
        self.__components.append(RPMPower(resolution, self.__window_id))

        self.set_active(configs.is_engine_active())

    def get_data_log(self):
        """ Returns the saved data from the session. """
        return self.__data_log

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def is_active(self):
        """ Returns window status. """
        return self.__active

    def draw(self):
        """ Draws all info on screen. """
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        for component in self.__components:
            ac.glColor4f(*Colors.white)
            component.draw(self.__data)
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

    def set_logging_active(self, active):
        """ Updates if the logging is active. """
        self.__logging = active

    def update(self):
        """ Updates the engine information. """
        self.__data.update(self.__info)
        if self.__logging is True:
            self.__data_log.append(copy.copy(self.__data))
        for component in self.__components:
            ac.glColor4f(*Colors.white)
            component.update(self.__data)
