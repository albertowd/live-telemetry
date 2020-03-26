#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handles wheel interpolations and colors.

@author: albertowd
"""
from lib.lt_colors import Colors
from lib.lt_util import color_interpolate


class Curve(object):
    """ Handles default curve interpolation. """

    def __init__(self, content="", normalize=False):
        """ Default constructor receives a inner '.lut' ACD file content. """
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

    def interpolate(self, current):
        """ Interpolates the current value in the curve. """
        for index in range(len(self._curve)):
            point = self._curve[index]
            if current < point[0]:
                if index == 0:
                    return point[1]
                else:
                    p_point = self._curve[index - 1]
                    p_diff = point[0] - p_point[0]
                    c_diff = (current - p_point[0]) / p_diff
                    v_diff = point[1] - p_point[1]
                    return p_point[1] + (v_diff * c_diff)
        return self._curve[-1][1] if len(self._curve) > 0 else 0.0


class Power(Curve):
    """ Handles power interpolations. """

    def __init__(self, content=""):
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

    def interpolate_color(self, rpm):
        """ Interpolates the power color. """
        perc = self.interpolate(rpm) / self._max[1]
        if perc < 0.995:
            if rpm < self._max[0]:
                if perc < 0.985:
                    return Colors.white
                elif perc < 0.995:
                    return Colors.blue
            else:
                return Colors.red
        else:
            return Colors.green


class TirePsi(object):
    """ Handles tire pressure interpolations. """

    def __init__(self, ref=26.0):
        self.__ref = ref
    
    def interpolate(self, psi):
        """ Returns the normalized psi. """
        return psi / self.__ref

    def interpolate_color(self, psi):
        """ Interpolates the wear color. """
        perc = self.interpolate(psi)
        if perc < 0.95:
            return Colors.blue
        elif perc < 1.00:
            return color_interpolate(Colors.blue, Colors.green, max(0.0, perc - 0.95) / 0.05)
        elif perc < 1.05:
            return color_interpolate(Colors.green, Colors.red, max(0.0, perc - 1.00) / 0.05)
        else:
            return Colors.red


class TireTemp(Curve):
    """ Handles tire temperature interpolations. """
    
    def __init__(self, content=""):
        super(TireTemp, self).__init__(content)

    def interpolate_color(self, temp, interpolated):
        """ Interpolates the temp color. """
        if temp < self._max[0]:
            return color_interpolate(Colors.blue, Colors.green, max(0.0, interpolated - 0.98) / 0.02)
        else:
            return color_interpolate(Colors.red, Colors.green, max(0.0, interpolated - 0.98) / 0.02)
