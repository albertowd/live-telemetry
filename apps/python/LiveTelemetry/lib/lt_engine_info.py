#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one engine infos from car and draw on screen.

@author: albertowd
"""
import copy

import ac

from lib.lt_components import BoostBar, BoxComponent, RPMPower
from lib.lt_info_window import InfoWindow
from lib.sim_info import info


class Data:  # pylint: disable=too-few-public-methods
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
        self.rpm = info_arg.physics.rpms
        self.timestamp = info_arg.graphics.iCurrentTime
        self.turbo_boost = info_arg.physics.turboBoost
        # Rolling observed maximum — static.maxTurboBoost is unreliable on some mods.
        self.max_turbo_boost = max(self.max_turbo_boost, self.turbo_boost)


class EngineInfo(InfoWindow):
    """ Engine info to draw and update. """

    def __init__(self, acd, configs):
        """ Default constructor. """
        super().__init__("Live Telemetry Engine")
        self._data = Data()
        self._info = info
        self._options = {key: configs.get_bool_option(key)
                         for key in ("BoostBar", "Logging", "RPMPower")}

        position = configs.get_window_position("EN")
        ac.setPosition(self._window_id, *position)

        size = configs.get_option("Size")
        mult = BoxComponent.resolution_map[size]
        ac.setSize(self._window_id, 512 * mult, 85 * mult)

        if info.static.maxTurboBoost > 0.0:
            self._components.append(BoostBar(acd, size, self._window_id))
        self._components.append(RPMPower(acd, size, self._window_id))

        # Only starts to draw after the setup.
        self.set_active(configs.is_window_active("EN"))

    def resize(self, resolution):
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self._window_id, 512 * mult, 85 * mult)
        for component in self._components:
            component.resize(resolution)

    def update(self, _delta_t: float):
        """ Updates the engine information. """
        self._data.update(self._info)
        if self._options["Logging"] is True:
            self._data_log.append(copy.copy(self._data))
