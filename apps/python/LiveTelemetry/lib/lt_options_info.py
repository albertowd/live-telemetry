#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to view and change app options.
"""

import ac

from lib.lt_components import BoxComponent
from lib.lt_colors import Colors
from lib.lt_config import Config


class OptionsInfo(object):
    """ Options info to change app options while in game. """

    def __init__(self, configs, lt_version):
        """ Default constructor. """
        self.__window_id = ac.newApp("Live Telemetry")
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "Live Telemetry {}".format(lt_version))

        pos_x = configs.get_options_x()
        pos_y = configs.get_options_y()
        ac.setPosition(self.__window_id, pos_x, pos_y)

        resolution = configs.get_resolution()
        ac.setSize(self.__window_id, 200, 110)

        self.__logging = configs.get_logging()
        self.__bt_logging = ac.addButton(self.__window_id, "Logging")
        ac.setFontColor(self.__bt_logging, *
                        (Colors.red if self.__logging else Colors.white))
        ac.setPosition(self.__bt_logging, 60, 30)
        ac.setSize(self.__bt_logging, 80, 30)
        ac.setFontAlignment(self.__bt_logging, "center")

        self.__bt_resolution = ac.addButton(self.__window_id, resolution)
        ac.setPosition(self.__bt_resolution, 60, 70)
        ac.setSize(self.__bt_resolution, 80, 30)
        ac.setFontAlignment(self.__bt_resolution, "center")

    def get_logging(self):
        """ Returns if the logging is enabled. """
        return self.__logging

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

    def resize(self, resolution):
        """ Resizes the window. """
        ac.setText(self.__bt_resolution, resolution)

    def set_logging(self, logging):
        """ Updates if the logging is enabled. """
        self.__logging = logging
        ac.setFontColor(self.__bt_logging, *
                        (Colors.red if self.__logging else Colors.white))
