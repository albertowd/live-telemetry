
"""
Module to update one wheel infos from car and draw on screen.
"""
import math
from wconfig import Config
from wcomponents import BoxComponent, Camber, Dirt, Height, Load, PressureAndTemps, Suspension, Tyre, Wear
import ac
import acsys

from sim_info import info


class Info(object):
    """ Wheel info to draw and update each tyre. """

    indexes = {0: "FL", 1: "FR", 2: "RL", 3: "RR"}
    names = {"FL": 0, "FR": 1, "RL": 2, "RR": 3}

    def __init__(self, wheel_index):
        """ Default constructor receive the index of the wheel it will draw info. """
        configs = Config()

        self.__id = Info.indexes[wheel_index]
        self.__active = configs.is_active(self.__id)
        self.__index = wheel_index
        self.__is_left = wheel_index is 0 or wheel_index is 2
        self.__info = {"camber": 0.0, "dirt": 0.0, "height": 0.0,
                       "load": 0.0, "pressure": 0.0, "suspension": 0.0, "wear": 0.0}
        self.__window_id = ac.newApp("Wheel Telemetry {}".format(self.__id))
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundOpacity(self.__window_id, 0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        pos_x = configs.get_x(self.__id)
        pos_y = configs.get_y(self.__id)
        ac.setPosition(self.__window_id, pos_x, pos_y)

        resolution = configs.get_resolution()
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 256 * mult)

        self.__bt_resolution = ac.addButton(self.__window_id, resolution)
        ac.setSize(self.__bt_resolution, 50, 30)
        ac.setFontAlignment(self.__bt_resolution, "center")

        self.__components = []
        self.__components.append(
            PressureAndTemps(resolution, self.__window_id))
        self.__components.append(Dirt(resolution))
        self.__components.append(Tyre(resolution))

        self.__components.append(Camber(resolution, self.__id))
        self.__components.append(Suspension(resolution, self.__id))
        self.__components.append(
            Height(resolution, self.__id, self.__window_id))
        self.__components.append(Wear(resolution, self.__id))
        self.__components.append(Load(resolution))

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
        for component in self.__components:
            component.draw(self.__info)

    def resize(self, resolution):
        """ Resizes the window. """
        ac.setText(self.__bt_resolution, resolution)
        for component in self.__components:
            component.resize(resolution)

    def set_active(self, active):
        """ Toggles the window status. """
        self.__active = active

    def update(self):
        """ Updates the wheel info. """
        self.__info["camber"] = info.physics.camberRAD[self.__index]
        self.__info["dirt"] = info.physics.tyreDirtyLevel[self.__index] * 4.0
        # um to mm
        self.__info["height"] = info.physics.rideHeight[0 if self.__index <
                                                        2 else 1] * 1000.0
        # N to (2*kgf)
        self.__info["load"] = info.physics.wheelLoad[self.__index] / \
            (2.0 * 9.80665)
        self.__info["pressure"] = info.physics.wheelsPressure[self.__index]
        max_travel = info.static.suspensionMaxTravel[self.__index]
        max_travel = max_travel if max_travel > 0.0 else 1.0
        self.__info["suspension"] = info.physics.suspensionTravel[self.__index] / max_travel
        self.__info["wear"] = info.physics.tyreWear[self.__index]
