#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one engine infos from car and draw on screen.

@author: albertowd
"""
import copy

from lib.lt_components import (BatteryBar, BoostBar, BoxComponent,
                               EngineChips, EngineReadouts, RPMPower)
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
        # User-controlled visibility for the battery bar, plumbed in
        # from EngineInfo._options each frame. "AUTO" defers to the
        # component's own runtime hybrid detection; "ON" forces the bar
        # visible (useful for AC1 hybrid mods whose activity signals
        # the detector misses); "OFF" hides it regardless.
        self.battery_bar_mode = "AUTO"
        self.brake_bias = 0.0
        self.drs_available = False
        self.drs_enabled = False
        self.ers_charging = False
        self.ers_heat_charging = False
        self.ers_power_level = 0
        self.ers_recovery_level = 0
        self.fuel = 0.0
        # AC1 convention: 0 = reverse, 1 = neutral, 2..N = forward gears.
        self.gear = 1
        self.kers_charge = 0.0
        self.kers_current_kj = 0.0
        # Positive kW = deploying (battery SoC falling); 0 otherwise.
        # kers_current_kj is a monotonic throughput counter on AC1 hybrid
        # cars (it ticks while energy moves in either direction), so a
        # kj-delta alone can't tell deploy from regen. The reliable signal
        # is a kers_charge drop — true regardless of whether the driver
        # triggered it via a manual button or the MCU did so on its own.
        # We deliberately do not gate on kers_input: on at least one
        # auto-deploy test car the button acts more like a "block regen"
        # switch than a deploy actuator, so holding it during a regen
        # phase produced false positives where the bar showed deploy HP
        # while energy was actually flowing into the battery.
        self.kers_deploy_kw = 0.0
        self.kers_input = 0.0
        self.kers_max_j = 0.0
        self.max_power = 0.0
        self.max_rpm = 0.0
        self.max_turbo_boost = 0.0
        self.pit_limiter = False
        self.rpm = 0.0
        self.speed_kmh = 0.0
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
        self.ers_heat_charging = bool(info_arg.physics.ersHeatCharging)
        self.ers_power_level = int(info_arg.physics.ersPowerLevel)
        self.ers_recovery_level = int(info_arg.physics.ersRecoveryLevel)
        self.fuel = float(info_arg.physics.fuel)
        self.gear = int(info_arg.physics.gear)
        self.kers_charge = float(info_arg.physics.kersCharge)
        self.kers_current_kj = float(info_arg.physics.kersCurrentKJ)
        self.kers_input = float(info_arg.physics.kersInput)
        self.kers_max_j = float(info_arg.static.kersMaxJ)
        self.pit_limiter = bool(info_arg.physics.pitLimiterOn)
        self.speed_kmh = float(info_arg.physics.speedKmh)
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
        # BatteryBar is a tri-state string (AUTO / ON / OFF), not a
        # plain bool — InfoWindow.draw checks for the "OFF" literal in
        # addition to its existing `is True` truthy gate.
        self._options["BatteryBar"] = configs.get_option("BatteryBar")

        # Engine widget pins to bottom-centre so it stays anchored above
        # the player's HUD on every supported resolution.
        self._anchor = "BC"

        size = configs.get_option("Size")
        mult = BoxComponent.resolution_map[size]
        self._apply_initial_geometry(
            configs, "EN",
            int(512 * mult), int(_ENGINE_LOGICAL_H * mult))

        has_turbo = info.static.maxTurboBoost > 0.0
        if has_turbo:
            self._components.append(BoostBar(acd, size, self._window_id))
        # BatteryBar is always added — it self-hides on pure-ICE cars
        # via runtime activity detection (see its docstring). We can't
        # gate on kersMaxJ at init because AC1 leaves that at 0 for
        # plenty of mods that do model a working hybrid, and we can't
        # gate on kersCharge because AC1 spawns it at 1.0 on cars with
        # no battery at all. When boost is present the battery sits at
        # y=-88 (ending at y=-64) so its bar clears the boost label at
        # y≈-56 — see BatteryBar's docstring for the stack geometry.
        self._components.append(BatteryBar(
            acd, size, self._window_id,
            y_offset=-88.0 if has_turbo else -24.0))
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
        self._resize_window(int(512 * mult), int(_ENGINE_LOGICAL_H * mult))
        for component in self._components:
            component.resize(resolution)

    def update(self, delta_t: float):
        """ Updates the engine information.

        ``kers_deploy_kw`` is derived here because it isn't a raw AC
        physics field — we fire only when ``kers_charge`` drops (real
        energy leaving the battery), then read the rate off the
        throughput counter and EMA-smooth it. See the field comment on
        ``Data.kers_deploy_kw`` for why ``kers_input`` isn't a reliable
        deploy signal on its own, and why raw frame deltas need
        smoothing.
        """
        prev_kj = self._data.kers_current_kj
        prev_charge = self._data.kers_charge
        prev_kw = self._data.kers_deploy_kw
        self._data.update(self._info)
        # Re-plumb the user's BatteryBar mode every tick — the option
        # may have been toggled via the menu button mid-session.
        self._data.battery_bar_mode = self._options.get("BatteryBar", "AUTO")
        if delta_t > 0.0 and self._data.kers_charge < prev_charge:
            raw_kw = max(
                0.0, (self._data.kers_current_kj - prev_kj) / delta_t)
        else:
            raw_kw = 0.0
        # EMA with alpha=0.3 at ~100 Hz: ~30 ms half-life. Cuts the
        # ~16% frame-to-frame jitter from kers_charge quantisation
        # (charge ticks unevenly across frames so the raw rate
        # alternates between high and low samples), at the cost of a
        # short tail when deploy stops — barely visible on the HP read.
        self._data.kers_deploy_kw = 0.7 * prev_kw + 0.3 * raw_kw
        if self._options["Logging"] is True:
            self._data_log.append(copy.copy(self._data))
