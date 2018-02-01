
"""
Module to update one wheel infos from car and draw on screen.
"""
import math
from wcomponents import BoxComponent, Load, Wheel
import ac
import acsys
import wconfig

from sim_info import info


class Info(object):
    """ Wheel info to draw and update each tyre. """

    indexes = {0: "FL", 1: "FR", 2: "RL", 3: "RR"}
    names = {"FL": 0, "FR": 1, "RL": 2, "RR": 3}

    def __init__(self, wheel_index):
        """ Default constructor receive the index of the wheel it will draw info. """
        self.__id = Info.indexes[wheel_index]
        self.__active = wconfig.is_active(self.__id)
        self.__index = wheel_index
        self.__is_left = wheel_index is 0 or wheel_index is 2
        self.__info = {}
        self.__window_id = ac.newApp("Wheel Telemetry {}".format(self.__id))
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundOpacity(self.__window_id, 0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        pos_x = wconfig.get_x(self.__id)
        pos_y = wconfig.get_y(self.__id)
        ac.setPosition(self.__window_id, pos_x, pos_y)

        resolution = wconfig.get_resolution()
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 400 * mult, 200 * mult)

        self.__bt_resolution = ac.addButton(self.__window_id, resolution)
        ac.setSize(self.__bt_resolution, 50, 30)
        ac.setFontAlignment(self.__bt_resolution, "center")

        self.__load = Load(resolution)
        self.__wheel = Wheel(resolution, self.__window_id)

    def get_id(self):
        """ Returns the whhel id. """
        return self.__id

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_button_id(self):
        """ Returns the resolution button id. """
        return self.__bt_resolution

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def is_active(self):
        """ Returns window status. """
        return self.__active

    def draw(self):
        """ Draws all info on screen. """
        ac.setBackgroundOpacity(self.__window_id, 0)
        self.__wheel.draw(self.__info)
        self.__load.draw(self.__info)

    def resize(self, resolution):
        """ Resizes the window. """
        ac.setText(self.__bt_resolution, resolution)
        self.__load.resize(resolution)
        self.__wheel.resize(resolution)

    def set_active(self, active):
        """ Toggles the window status. """
        self.__active = active

    def update(self):
        """ Updates the wheel info. """
        camber = math.sin(info.physics.camberRAD[self.__index]) * 100.0
        self.__info["camber_l"] = camber if self.__is_left else 0.0
        self.__info["camber_r"] = 0.0 if self.__is_left else camber
        self.__info["dirt"] = info.physics.tyreDirtyLevel[self.__index] * 4.0
        self.__info["height"] = info.physics.rideHeight[0 if self.__index < 2 else 1]
        self.__info["load"] = info.physics.wheelLoad[self.__index] / 12.0
        self.__info["pressure"] = info.physics.wheelsPressure[self.__index]
        max_travel = info.static.suspensionMaxTravel[self.__index]
        if max_travel <= 0.0:
            max_travel = 1.0
        self.__info["susp_travel"] = info.physics.suspensionTravel[self.__index] / max_travel
        self.__info["wear"] = info.physics.tyreWear[self.__index]
