#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to view and change app options.

@author: albertowd
"""

import ac

from lib.lt_components import BoxComponent
from lib.lt_colors import Colors
from lib.lt_config import Config


class OptionsInfo(object):
    """ Options info to change app options while in game. """

    def __init__(self, configs):
        """ Default constructor. """
        self.__load = False
        self.__logging = False

        self.__window_id = ac.newApp("Live Telemetry")
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "Live Telemetry {}".format(
            configs.get_version()))

        pos_x = configs.get_options_x()
        pos_y = configs.get_options_y()
        ac.setPosition(self.__window_id, pos_x, pos_y)

        resolution = configs.get_resolution()
        ac.setSize(self.__window_id, 200, 150)

        self.__bt_load = ac.addButton(self.__window_id, "Load (N)")
        ac.setPosition(self.__bt_load, 60, 30)
        ac.setSize(self.__bt_load, 80, 30)
        ac.setFontAlignment(self.__bt_load, "center")

        self.__bt_logging = ac.addButton(self.__window_id, "Logging")
        ac.setPosition(self.__bt_logging, 60, 70)
        ac.setSize(self.__bt_logging, 80, 30)
        ac.setFontAlignment(self.__bt_logging, "center")

        self.__bt_resolution = ac.addButton(self.__window_id, resolution)
        ac.setPosition(self.__bt_resolution, 60, 110)
        ac.setSize(self.__bt_resolution, 80, 30)
        ac.setFontAlignment(self.__bt_resolution, "center")

        self.set_load_active(configs.is_load_active())
        self.set_logging_active(configs.is_logging_active())
        self.resize(configs.get_resolution())

    def get_load_button_id(self):
        """ Returns the load button id. """
        return self.__bt_load

    def get_logging_button_id(self):
        """ Returns the logging button id. """
        return self.__bt_logging

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_resolution(self):
        """ Returns the resolution of the window. """
        return ac.getText(self.__bt_resolution)

    def get_resolution_button_id(self):
        """ Returns the resolution button id. """
        return self.__bt_resolution

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def is_load_active(self):
        """ Returns if the load feature is active. """
        return self.__load

    def is_logging_active(self):
        """ Returns if the logging is active. """
        return self.__logging

    def resize(self, resolution):
        """ Resizes the window. """
        ac.setText(self.__bt_resolution, resolution)

    def set_load_active(self, active):
        """ Updates if the load feature is active. """
        self.__load = active
        ac.setFontColor(self.__bt_load, *
                        (Colors.red if self.__load else Colors.white))

    def set_logging_active(self, active):
        """ Updates if the logging is active. """
        self.__logging = active
        ac.setFontColor(self.__bt_logging, *
                        (Colors.red if self.__logging else Colors.white))
