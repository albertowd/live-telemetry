#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one wheel infos from car and draw on screen.

@author: albertowd
"""
import copy

import ac
import acsys

from lib.lt_acd import ACD
from lib.lt_components import (BoxComponent, Camber, Dirt, Height,
                               Load, Lock, Pressure, Temps, Suspension, Tire,
                               Wear, WheelTitle)
from lib.lt_config import Config
from lib.lt_info_window import InfoWindow
from lib.lt_util import WheelPos
from lib.sim_info import info


class Data:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """ Data object to keep values between updates. """

    def __init__(self):
        self.abs_active = False
        self.camber = 0.0
        self.height = 0.0
        self.lock = False
        self.susp_m_t = 0.0
        self.susp_t = 0.0
        self.susp_v = False
        self.timestamp = 0
        self.tire_d = 0.0
        self.tire_l = 0.0
        self.tire_p = 0.0
        self.tire_t_c = 0.0
        self.tire_t_i = 0.0
        self.tire_t_m = 0.0
        self.tire_t_o = 0.0
        self.tire_w = 0.0

    def update(self, wheel, info_arg, abs_slip_limit):
        """ Update the default values from the car engine. """
        index = wheel.index()

        # ABS / lock detection.
        # `info.physics.abs` is the player's ABS assist setting (0..1, 0 = off);
        # it is NOT a per-frame "ABS pulsing now" flag. The real signal is wheel
        # slip vs. the car's slip-ratio threshold from electronics.ini, gated by
        # the player having ABS enabled at all.
        braking = info_arg.physics.brake > 0.0
        slip = info_arg.physics.wheelSlip[index]
        ang_speed = info_arg.physics.wheelAngularSpeed[index]
        abs_enabled = info_arg.physics.abs > 0.0

        # A locked wheel either stops rotating or shows an extreme slip ratio.
        # Using both signals catches AC physics cases where a locked wheel keeps
        # a small residual angular velocity instead of going to exact zero.
        # The `slip > 0` gate prevents false positives on stationary cars.
        self.lock = braking and slip > 0.0 and (abs(ang_speed) < 1.0 or slip > 0.5)
        self.abs_active = abs_enabled and braking and slip > abs_slip_limit and not self.lock

        self.camber = info_arg.physics.camberRAD[index]

        # Shared memory's physics.suspensionTravel is unreliable on some mods, so fall back to the Python API.
        python_travel = ac.getCarState(0, acsys.CS.SuspensionTravel)
        self.susp_t = python_travel[index]

        # If there's no max travel, keep it updating for max values.
        max_travel = info_arg.static.suspensionMaxTravel[index]
        self.susp_m_t = max_travel if max_travel > 0.0 else max(
            self.susp_t, self.susp_m_t)
        self.susp_v = max_travel == 0.0

        # um to mm
        self.height = info_arg.physics.rideHeight[int(index / 2)] * 1000.0

        # Body-roll correction across the axle. Use python_travel for
        # BOTH wheels — shared memory is the unreliable-on-mods source
        # the block above already swapped out, so mixing the two
        # sources here means the diff is wrong on exactly the mods the
        # Python-API fallback was added to defend against. F1-style
        # cars with tiny absolute travel are the most sensitive
        # (correction magnitude ~ rest-state height).
        opposite_index = index + (1 if wheel.is_left() else -1)
        susp_diff = self.susp_t - python_travel[opposite_index]
        self.height -= ((susp_diff / 2.0) * 1000.0)
        # Clamp negative readings to 0 — the per-axle ride height plus
        # the body-roll correction can dip below the surface on big
        # compressions / kerb strikes; the chassis can't physically go
        # under the ground, so floor it at 0 mm. The Height widget's
        # bottom-out flash already triggers below 0.02 mm so the alert
        # is preserved.
        self.height = max(self.height, 0.0)

        self.timestamp = info_arg.graphics.iCurrentTime
        self.tire_d = info_arg.physics.tyreDirtyLevel[index] * 4.0

        # N to (5*kgf)
        self.tire_l = info_arg.physics.wheelLoad[index] / (5.0 * 9.80665)
        self.tire_p = info_arg.physics.wheelsPressure[index]
        self.tire_t_c = info_arg.physics.tyreCoreTemperature[index]
        self.tire_t_i = info_arg.physics.tyreTempI[index]
        self.tire_t_m = info_arg.physics.tyreTempM[index]
        self.tire_t_o = info_arg.physics.tyreTempO[index]

        # Normalised to [~0.99, ~1.0]; Wear.draw self-calibrates against
        # the peak observed value because AC's tyreWear is a grip/health
        # signal that climbs during warm-up before degrading.
        self.tire_w = info_arg.physics.tyreWear[index] / 100.0


# Bool-typed options shared across the wheel widget components.
WHEEL_BOOL_OPTIONS = ("Camber", "Dirt", "Height", "Load", "Lock", "Logging",
                      "Pressure", "Suspension", "Temps", "Tire", "Wear")


class WheelInfo(InfoWindow):
    """ Wheel info to draw and update each wheel. """

    def __init__(self, acd: ACD, configs: Config, wheel_index: int) -> None:
        """ Default constructor receive the index of the wheel it will draw info. """
        self.__wheel = WheelPos(wheel_index)
        super().__init__("Live Telemetry {}".format(self.__wheel.name()))
        self.__abs_slip_limit = acd.get_abs_slip_limit()
        self._data = Data()
        self._info = info
        self._options = {key: configs.get_bool_option(key) for key in WHEEL_BOOL_OPTIONS}

        # Per-wheel anchor pins the widget to its on-screen corner so a
        # Size cycle keeps it inside the screen (FL top-left, FR top-right,
        # RL bottom-left, RR bottom-right).
        self._anchor = {"FL": "TL", "FR": "TR",
                        "RL": "BL", "RR": "BR"}[self.__wheel.name()]

        size = configs.get_option("Size")
        mult = BoxComponent.resolution_map[size]
        self._apply_initial_geometry(
            configs, self.__wheel.name(),
            int(512 * mult), int(271 * mult))

        # Tire silhouette draws first so every other overlay (Temps,
        # Dirt, Lock, contact patches, ...) lands on top of it. The
        # new geometry is solid-filled — drawing it later would cover
        # the IMO temperature grid and dirt bar.
        self._components.append(Tire(acd, size, self.__wheel))
        self._components.append(
            Temps(acd, size, self.__wheel, self._window_id))
        self._components.append(Dirt(size))
        self._components.append(Lock(acd, size, self.__wheel))

        # Camber option now toggles the contact-patch load-distribution
        # heuristic — the trapezoidal camber strip was replaced in 1.8.0.
        # The component class kept its "Camber" name so the existing
        # option toggle and saved configs continue to work without a
        # migration step.
        self._components.append(Camber(acd, size, self.__wheel))
        self._components.append(Suspension(size, self.__wheel))
        self._components.append(Height(size, self.__wheel, self._window_id))
        self._components.append(
            Pressure(acd, size, self.__wheel, self._window_id))
        self._components.append(Wear(size, self.__wheel, self._window_id))
        # Wheel ID + compound abbreviation stacked above the height
        # widget. Always rendered (text-only, cheap); gating it behind
        # an option would just be UI noise.
        self._components.append(
            WheelTitle(size, self.__wheel, self._window_id))
        # Needs to be the last to render above all components
        self._components.append(Load(size, self.__wheel))

        # Only draw after the setup
        self.set_active(configs.is_window_active(self.__wheel.name()))

    def get_id(self) -> str:
        """ Returns the wheel id. """
        return self.__wheel.name()

    def resize(self, size: str) -> None:
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[size]
        self._resize_window(int(512 * mult), int(271 * mult))
        for component in self._components:
            component.resize(size)

    def update(self, _delta_t: float) -> None:
        """ Updates the wheel information. """
        self._data.update(self.__wheel, self._info, self.__abs_slip_limit)
        if self._options["Logging"] is True:
            self._data_log.append(copy.copy(self._data))
