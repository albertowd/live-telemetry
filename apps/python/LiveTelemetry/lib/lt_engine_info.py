#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one engine infos from car and draw on screen.

@author: albertowd
"""
import copy

import ac

from lib.lt_components import (BoostBar, BoxComponent, EngineChips,
                               EngineReadouts, RPMPower)
from lib.lt_info_window import InfoWindow
from lib.sim_info import info


# Logical engine widget height in pixels at 1440p / mult=1.0.
# Bumped 85 → 120 in 1.8.0 to fit the driver-aid chip strip + analog
# readouts row below the existing RPM bar.
_ENGINE_LOGICAL_H = 120


class Data:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """ Data object to keep values between updates. """

    def __init__(self):
        self.abs_level = 0.0
        self.brake_bias = 0.0
        self.drs_available = False
        self.drs_enabled = False
        self.ers_charging = False
        self.fuel = 0.0
        self.max_power = 0.0
        self.max_rpm = 0.0
        self.max_turbo_boost = 0.0
        self.pit_limiter = False
        self.rpm = 0.0
        self.tc_level = 0.0
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

        # Driver-aid + analog readouts surfaced on the engine widget in
        # 1.8.0 (Phase 1/2 from live-telemetry-ac-evo). AC1 publishes a
        # subset of evo's fields — anything not in physics is just
        # missing here, the components hide the corresponding cell.
        self.abs_level = float(info_arg.physics.abs)
        self.brake_bias = float(info_arg.physics.brakeBias)
        # AC1's drs slot is a 0..1 deploy value; treat anything >0.5 as
        # actually deployed. drsAvailable is the zone flag.
        self.drs_available = bool(info_arg.physics.drsAvailable)
        self.drs_enabled = bool(info_arg.physics.drsEnabled) or float(info_arg.physics.drs) > 0.5
        self.ers_charging = bool(info_arg.physics.ersIsCharging)
        self.fuel = float(info_arg.physics.fuel)
        self.pit_limiter = bool(info_arg.physics.pitLimiterOn)
        self.tc_level = float(info_arg.physics.tc)


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
        ac.setSize(self._window_id, 512 * mult, _ENGINE_LOGICAL_H * mult)

        if info.static.maxTurboBoost > 0.0:
            self._components.append(BoostBar(acd, size, self._window_id))
        self._components.append(RPMPower(acd, size, self._window_id))
        # Always-on driver-aid chips + analog readouts (see lt_info_window
        # for the missing-key default-True dispatch). Cheap text-only
        # additions; hiding them would just be extra UI noise.
        self._components.append(EngineChips(size, self._window_id))
        self._components.append(EngineReadouts(size, self._window_id))

        # Only starts to draw after the setup.
        self.set_active(configs.is_window_active("EN"))

    def resize(self, resolution):
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self._window_id, 512 * mult, _ENGINE_LOGICAL_H * mult)
        for component in self._components:
            component.resize(resolution)

    def update(self, _delta_t: float):
        """ Updates the engine information. """
        self._data.update(self._info)
        if self._options["Logging"] is True:
            self._data_log.append(copy.copy(self._data))
