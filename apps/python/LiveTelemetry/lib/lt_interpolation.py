#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handles wheel interpolations and colors.

@author: albertowd
"""
from lib.lt_colors import Colors
from lib.lt_util import color_interpolate


class ABSSlipList:
    """ Handles ABS slip curve/value. """

    def __init__(self, content=""):
        """ Default constructor receives an inner '.lut' ACD file content. """
        self.__list = []

        lines = content.split("\n")
        for line in lines:
            if len(line) > 0:
                values = line.split("|")
                self.__list.append((int(values[0]), float(values[0])))

    def level_ratio(self, abs_level: int) -> float:
        """ Returns the ABS level related ratio, a hundred if is invalid. """
        if 0 < abs_level <= len(self.__list):
            return self.__list[abs_level - 1]
        return 100.0


class Curve:
    """ Handles default curve interpolation. """

    def __init__(self, content="", normalize=False):
        """ Default constructor receives an inner '.lut' ACD file content. """
        self._curve = []
        self._max = (0.0, 0.0)

        lines = content.split("\n")
        for line in lines:
            if len(line) > 0:
                values = line.split("|")
                values[0] = float(values[0])
                values[1] = float(values[1])
                if normalize:
                    values[1] /= 100.0
                self._curve.append((values[0], values[1]))

                if values[1] > self._max[1]:
                    self._max = (values[0], values[1])

    def interpolate(self, current: float) -> float:
        """ Interpolates the current value in the curve. """
        for index, point in enumerate(self._curve):
            if current < point[0]:
                if index == 0:
                    return point[1]
                p_point = self._curve[index - 1]
                p_diff = point[0] - p_point[0]
                c_diff = (current - p_point[0]) / p_diff
                v_diff = point[1] - p_point[1]
                return p_point[1] + (v_diff * c_diff)
        return self._curve[-1][1] if len(self._curve) > 0 else 0.0


class Power(Curve):
    """ Handles power interpolations. """

    def __init__(self, content=""):
        """ Default constructor receives an inner '.lut' ACD file content. """
        super(Power, self).__init__(content)

        new_curve = []
        self._max = (0.0, 0.0)

        # Processes the curve to HP values
        for point in self._curve:
            rpm = point[0]
            torque = point[1]
            new_point = (rpm, (torque * rpm) / 5252)

            if new_point[1] > self._max[1]:
                self._max = new_point

            new_curve.append(new_point)

        self._curve = new_curve

    def interpolate_color(self, rpm: int) -> list:
        """ Interpolates the power color thourgh the current RPM value. """
        perc = self.interpolate(rpm) / self._max[1]
        if perc < 0.995:
            if rpm < self._max[0]:
                if perc < 0.985:
                    return Colors.white
                return Colors.blue
            return Colors.red
        return Colors.green


class TirePsi:
    """ Handles tire pressure interpolations. """

    def __init__(self, ref=26.0):
        """ Default constructor receives a reference value. """
        self.__ref = ref

    def interpolate(self, psi: float) -> float:
        """ Returns the normalized psi. """
        return psi / self.__ref

    def interpolate_color(self, psi: float) -> list:
        """ Interpolates the pressure color through the current value. """
        perc = self.interpolate(psi)
        if perc < 0.95:
            return Colors.blue
        if perc < 1.00:
            return color_interpolate(Colors.blue, Colors.green, max(0.0, perc - 0.95) / 0.05)
        if perc < 1.05:
            return color_interpolate(Colors.green, Colors.red, max(0.0, perc - 1.00) / 0.05)
        return Colors.red


class TireTemp(Curve):
    """ Handles tire temperature interpolations. """

    def __init__(self, content="") -> None:
        """ Default constructor receives an inner '.lut' ACD file content. """
        super(TireTemp, self).__init__(content)

    def interpolate_color(self, temp: float, interpolated: float) -> list:
        """ Interpolates the temperature color through the interpolated value. """
        if temp < self._max[0]:
            return color_interpolate(Colors.blue, Colors.green, max(0.0, interpolated - 0.98) / 0.02)
        return color_interpolate(Colors.red, Colors.green, max(0.0, interpolated - 0.98) / 0.02)
