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
from lib.lt_colors import Colors
from lib.lt_components import BoxComponent, Camber, Dirt, Height, Load, Lock, Pressure, Temps, Suspension, Tire, Wear
from lib.lt_config import Config
from lib.lt_util import WheelPos
from lib.sim_info import info


class Data:
    """ Data object to keep values between updates. """

    def __init__(self):
        self.abs_active = False
        #self.abs_slip_ratio = 0.0
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
        #self.wheel_slip_ratio = 0.0

    def update(self, wheel, info_arg):
        """ Update the default values from the car engine. """
        index = wheel.index()

        #self.abs_slip_ratio = info.physics.abs
        self.abs_active = info.physics.brake > 0.0 and info.physics.wheelSlip[index] > info.physics.abs
        self.camber = info.physics.camberRAD[index]
        self.lock = info.physics.brake > 0.0 and info.physics.wheelSlip[index] > 0.0 and info.physics.wheelAngularSpeed[index] == 0.0

        #Some cars the suspension travel from the shared memory is broken.
        #Example:
        #Shared Memory Max travel: 0.15000000596046448mm
        #Python travel: 0.08263124525547028mm => 0.5508749464799981%
        #Shared Memory Travel: 0.15007904171943665mm => 1.0005269050388772%
        # self.susp_t = info.physics.suspensionTravel[index]
        python_travel = ac.getCarState(0, acsys.CS.SuspensionTravel)
        self.susp_t = python_travel[index]

        # If there's no max travel, keep it updating for max values.
        max_travel = info.static.suspensionMaxTravel[index]
        self.susp_m_t = max_travel if max_travel > 0.0 else max(
            self.susp_t, self.susp_m_t)
        self.susp_v = max_travel == 0.0

        # um to mm
        self.height = info.physics.rideHeight[int(index / 2)] * 1000.0

        # Get susp diff
        susp_diff = self.susp_t - \
            info.physics.suspensionTravel[index +
                                          (1 if wheel.is_left() else -1)]
        self.height -= ((susp_diff / 2.0) * 1000.0)

        self.timestamp = info.graphics.iCurrentTime
        self.tire_d = info.physics.tyreDirtyLevel[index] * 4.0

        # N to (5*kgf)
        self.tire_l = info.physics.wheelLoad[index] / (5.0 * 9.80665)
        self.tire_p = info.physics.wheelsPressure[index]
        self.tire_t_c = info.physics.tyreCoreTemperature[index]
        self.tire_t_i = info.physics.tyreTempI[index]
        self.tire_t_m = info.physics.tyreTempM[index]
        self.tire_t_o = info.physics.tyreTempO[index]

        # Normal to percent
        self.tire_w = info.physics.tyreWear[index] / 100.0

        # Wheel slip ratio to calculat ABS timing.
        #self.wheel_slip_ratio = info.physics.wheelSlip[index]


class WheelInfo:
    """ Wheel info to draw and update each wheel. """

    def __init__(self, acd: ACD, configs: Config, wheel_index: int) -> None:
        """ Default constructor receive the index of the wheel it will draw info. """
        self.__wheel = WheelPos(wheel_index)
        self.__active = False
        self.__data = Data()
        self.__data_log = []
        self.__info = info
        self.__options = {
            "Camber": configs.get_bool_option("Camber"),
            "Dirt": configs.get_bool_option("Dirt"),
            "Height": configs.get_bool_option("Height"),
            "Load": configs.get_bool_option("Load"),
            "Lock": configs.get_bool_option("Lock"),
            "Logging": configs.get_bool_option("Logging"),
            "Pressure": configs.get_bool_option("Pressure"),
            "Suspension": configs.get_bool_option("Suspension"),
            "Temps": configs.get_bool_option("Temps"),
            "Tire": configs.get_bool_option("Tire"),
            "Wear": configs.get_bool_option("Wear")
        }
        self.__window_id = ac.newApp(
            "Live Telemetry {}".format(self.__wheel.name()))
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        position = configs.get_window_position(self.__wheel.name())
        ac.setPosition(self.__window_id, *position)

        size = configs.get_option("Size")
        mult = BoxComponent.resolution_map[size]
        ac.setSize(self.__window_id, 512 * mult, 271 * mult)

        self.__components = []
        self.__components.append(Temps(acd, size, self.__wheel))
        self.__components.append(Dirt(size))
        self.__components.append(Lock(acd, size, self.__wheel))
        self.__components.append(Tire(acd, size, self.__wheel))

        self.__components.append(Camber(size))
        self.__components.append(Suspension(size, self.__wheel))
        self.__components.append(Height(size, self.__wheel, self.__window_id))
        self.__components.append(
            Pressure(acd, size, self.__wheel, self.__window_id))
        self.__components.append(Wear(size, self.__wheel))
        # Needs to be the last to render above all components
        self.__components.append(Load(size, self.__wheel))

        # Only draw after the setup
        self.set_active(configs.is_window_active(self.__wheel.name()))

    def get_data_log(self):
        """ Returns the saved data from the session. """
        return self.__data_log

    def get_id(self) -> str:
        """ Returns the wheel id. """
        return self.__wheel.name()

    def get_option(self, name: str):
        """ Returns an option value. """
        return self.__options[name]

    def get_position(self) -> [float]:
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_window_id(self) -> int:
        """ Returns the window id. """
        return self.__window_id

    def has_data_logged(self) -> bool:
        """Returns if the info has data logged."""
        return len(self.__data_log) > 0

    def is_active(self) -> bool:
        """ Returns window status. """
        return self.__active

    def draw(self, delta_t: float) -> None:
        """ Draws all info on screen. """
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        for component in self.__components:
            if self.__options[type(component).__name__] is True:
                ac.glColor4f(*Colors.white)
                component.draw(self.__data, delta_t)
            else:
                component.clear()
        ac.glColor4f(*Colors.white)

    def resize(self, size: str) -> None:
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[size]
        ac.setSize(self.__window_id, 512 * mult, 271 * mult)
        for component in self.__components:
            component.resize(size)

    def set_active(self, active: bool) -> None:
        """ Toggles the window status. """
        self.__active = active

    def set_option(self, name: str, value) -> None:
        """ Updates an option value. """
        self.__options[name] = value

    def update(self, delta_t: float) -> None:
        """ Updates the wheel information. """
        self.__data.update(self.__wheel, self.__info)
        if self.__options["Logging"] is True:
            self.__data_log.append(copy.copy(self.__data))
