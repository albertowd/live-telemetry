#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handles wheel interpolations and colors.

@author: albertowd
"""
from wcolors import Colors
from wutil import color_interpolate, log


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


class TyrePsi(object):
    """ Handles tyre pressure interpolations. """

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
            return color_interpolate(Colors.blue, Colors.green, (perc - 0.95) / 0.05)
        elif perc < 1.05:
            return color_interpolate(Colors.green, Colors.red, (perc - 1.00) / 0.05)
        else:
            return Colors.red


class TyreTemp(Curve):
    """ Handles tyre temperature interpolations. """
    
    def __init__(self, content=""):
        super(TyreTemp, self).__init__(content)

    def interpolate_color(self, temp, interpolated):
        """ Interpolates the temp color. """
        if interpolated < 0.98:
            return Colors.blue if temp < self._max[0] else Colors.red
        else:
            if temp < 100.0:
                return color_interpolate(Colors.blue, Colors.green, (interpolated - 0.98) / 0.02)
            else:
                return color_interpolate(Colors.red, Colors.green, (interpolated - 0.98) / 0.02)

        
if __name__ == "__main__":
    curve = "0|99.5\n0.57|100\n2.0|100\n4|99\n7.6|97\n15.2|92\n20.9|90\n22.8|85"
    interpolation = TyreTemp(curve)
    log("Tyre Temp:\n\t{}".format(curve.replace("\n", "\n\t")))
    currents = [0.0, 0.25, 0.57, 1.0, 4.0, 6.0, 23.0]
    for current in currents:
        log("\t{} => {}".format(current, interpolation.interpolate(current)))
    
    psi = 30.0
    log("Tyre Psi: {}".format(psi))
    interpolation = TyrePsi(psi)
    psis = [24.0, 28.0, 30.0, 32.0, 36.0]
    for current in psis:
        log("\t{} => {}".format(current, interpolation.interpolate(current)))
