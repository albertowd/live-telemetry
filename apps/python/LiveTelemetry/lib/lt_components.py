#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to split and resize components on the screen.

@author: albertowd
"""
import copy
import math

import ac
import acsys

from lib.lt_colors import Colors
from lib.lt_interpolation import Power, TirePsi, TireTemp


class Background(object):
    """ Class to draw a background in a box component. """

    def __init__(self, color=Colors.transparent, border=Colors.transparent, size=1.0):
        self.color = color
        self.border = border
        self.size = size

    def draw(self, rect, texture_id=None):
        """ Draws the box background. """
        if self.size > 0.0 and self.border[3] > 0.0:
            twice = self.size * 2.0
            ac.glColor4f(*self.border)
            ac.glQuad(rect[0] - self.size, rect[1] - self.size,
                      rect[2] + twice, rect[3] + twice)

        ac.glColor4f(*self.color)
        if texture_id is None:
            ac.glQuad(*rect)
        else:
            ac.glQuadTextured(rect[0], rect[1], rect[2], rect[3], texture_id)


class Box(object):
    """ Class to handle a box component with background. """

    def __init__(self, p_x=0.0, p_y=0.0, width=100.0, height=100.0):
        self.center = [0.0, 0.0]
        self.rect = [p_x, p_y, width, height]
        self.recalc_center()

    def recalc_center(self):
        """ Recalculate the box middle point. """
        self.center[0] = self.rect[0] + (self.rect[2] / 2.0)
        self.center[1] = self.rect[1] + (self.rect[3] / 2.0)

    def set_position(self, pos_x, pos_y):
        """ Updates the box position. """
        self.rect[0] = pos_x
        self.rect[1] = pos_y

    def set_size(self, width, height):
        """ Updates the box size. """
        self.rect[2] = width
        self.rect[3] = height


class BoxComponent(object):
    """ Class to handle position and resize of a component. """

    resolutions = ["240p", "360p", "480p", "HD", "FHD", "1440p", "UHD", "4K", "8K", "480p"]
    resolution_map = {"240p": 0.16, "360p": 0.25, "480p": 0.33, "HD": 0.5,
                      "FHD": 0.75, "1440p": 1.0, "UHD": 1.5, "4K": 1.6, "8K": 3.0}

    def __init__(self, p_x=0.0, p_y=0.0, width=100.0, height=100.0, font=24.0):
        self.__ini_font = font
        self.__ini_box = Box(p_x, p_y, width, height)
        self._back = Background()
        self._box = Box(p_x, p_y, width, height)
        self._font = font
    
    def clear(self):
        """Clear labels to not draw anything on screen."""
        pass

    def _draw(self, texture_id=None):
        """ Draws the component on the screen. """
        self._back.draw(self._box.rect, texture_id)

    def draw(self, data):
        """ Draw the component contents after the base. """
        pass

    def resize(self, resolution="HD"):
        """ Resizes the component. """
        mult = BoxComponent.resolution_map[resolution]
        self._box.set_position(
            self.__ini_box.rect[0] * mult, self.__ini_box.rect[1] * mult)
        self._box.set_size(
            self.__ini_box.rect[2] * mult, self.__ini_box.rect[3] * mult)
        self._box.recalc_center()
        self._font = self.__ini_font * mult
        self.resize_fonts(resolution)

    def resize_fonts(self, resolution):
        """ Resize all the ac components with text. Must be overrided. """
        pass

    def update(self, data):
        """ Update the component contents. """
        pass


class Camber(BoxComponent):
    """ Class to handle tire camber draw. """

    def __init__(self, resolution):
        # Initial size is 160x10
        super(Camber, self).__init__(170.0, 256.0, 172.0, 15.0)
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, data):
        rect = self._box.rect
        camber = data.camber
        tan = math.tan(camber) * rect[2]
        tan_left = -(tan if camber < 0.0 else 0.0)
        tan_right = tan if camber > 0.0 else 0.0

        ac.glBegin(acsys.GL.Quads)
        ac.glColor4f(*Colors.white)
        ac.glVertex2f(rect[0], rect[1] + tan_left)
        ac.glVertex2f(rect[0], rect[1] + rect[3])
        ac.glVertex2f(rect[0] + rect[2], rect[1] + rect[3])
        ac.glVertex2f(rect[0] + rect[2], rect[1] + tan_right)
        ac.glEnd()

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class Dirt(BoxComponent):
    """ Class to handle tire dirt draw. """

    def __init__(self, resolution):
        # Initial size is 136x116
        super(Dirt, self).__init__(188.0, 128.0, 136.0, 116.0)
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, data):
        dirt = data.tire_d * self.__mult

        rect = copy.copy(self._box.rect)
        rect[1] += (rect[3] - dirt)
        rect[3] = dirt

        ac.glColor4f(*Colors.brown)
        ac.glQuad(*rect)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class Height(BoxComponent):
    """ Class to handle height draw. """

    texture_id = 0

    def __init__(self, resolution, wheel, window_id):
        # Initial size is 64x48
        super(Height, self).__init__(
            430.0 if wheel.is_left() else 18.0, 208.0, 64.0, 48.0)
        self._back.color = Colors.white

        if Height.texture_id == 0:
            Height.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/height.png")

        self.__lb = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def clear(self):
        ac.setText(self.__lb, "")

    def draw(self, data):
        self._draw(Height.texture_id)
        ac.setText(self.__lb, "{:03.1f} mm".format(data.height))

    def resize_fonts(self, resolution):
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(
            self.__lb, self._box.center[0], self._box.center[1] - (self._font / 1.25))


class Load(BoxComponent):
    """ Class to handle tire load draw. """

    texture_id = 0

    def __init__(self, resolution, wheel):
        super(Load, self).__init__(128.0, 0.0, 256.0, 256.0)
        self._back.color = Colors.white
        self.__mult = BoxComponent.resolution_map[resolution]

        if Load.texture_id == 0:
            Load.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/load.png")

        self.resize(resolution)

    def draw(self, data):
        load = data.tire_l * self.__mult
        load_2 = load / 2.0
        self._box.set_position(
            self._box.center[0] - load_2, self._box.center[1] - load_2)
        self._box.set_size(load, load)
        self._draw(Load.texture_id)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class Pressure(BoxComponent):
    """ Class to handle tire pressure draw. """

    texture_id = 0

    def __init__(self, acd, resolution, wheel, window_id):
        self.__calc = TirePsi(acd.get_ideal_pressure(
            ac.getCarTyreCompound(0), wheel))

        # Initial size is 85x85
        super(Pressure, self).__init__(
            70.0 if wheel.is_left() else 382.0, 95.0, 60.0, 60.0)
        self._back.color = Colors.white

        if Pressure.texture_id == 0:
            Pressure.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/pressure.png")

        self.__lb = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)
    
    def clear(self):
        ac.setText(self.__lb, "")

    def draw(self, data):
        psi = data.tire_p
        ac.setText(self.__lb, "{:3.1f} psi".format(psi))

        color = self.__calc.interpolate_color(psi)
        ac.setFontColor(self.__lb, color[0], color[1], color[2], color[3])
        self._back.color = color
        self._draw(Pressure.texture_id)

    def resize_fonts(self, resolution):
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(
            self.__lb, self._box.center[0], self._box.rect[1] + self._box.rect[3])


class RPMPower(BoxComponent):
    """ Class to handle best power change. """

    def __init__(self, acd, resolution, window_id):
        self.__calc = Power(acd.get_power_curve())

        # Initial size is 512x85
        super(RPMPower, self).__init__(0.0, 0.0, 512.0, 50.0)
        self._back.color = Colors.black

        self.__lb = ac.addLabel(window_id, "- RPM")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def draw(self, data):
        self._draw()

        rpm = data.rpm
        ratio = data.rpm / data.max_rpm

        bar = copy.copy(self._box.rect)
        bar[2] *= ratio

        color = self.__calc.interpolate_color(rpm)
        ac.glColor4f(*color)
        ac.glQuad(*bar)

        ac.setFontColor(self.__lb, color[0], color[1], color[2], color[3])
        ac.setText(self.__lb, "{} RPM".format(rpm))

    def resize_fonts(self, resolution):
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(
            self.__lb, self._box.center[0], self._box.rect[1] + self._box.rect[3])


class Suspension(BoxComponent):
    """ Class to handle suspension draw. """

    texture_id = 0

    def __init__(self, resolution, wheel):
        # Initial size is 64x256
        super(Suspension, self).__init__(
            346.0 if wheel.is_left() else 102.0, 0.0, 64.0, 256.0)
        self._back.color = Colors.white
        self.__mult = BoxComponent.resolution_map[resolution]

        if Suspension.texture_id == 0:
            Suspension.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/suspension.png")

        self.resize(resolution)

    def draw(self, data):
        travel = data.susp_t / data.susp_m_t
        if travel > 0.95 or travel < 0.05:
            self._back.color = Colors.red
        elif travel > 0.90 or travel < 0.1:
            self._back.color = Colors.yellow
        else:
            self._back.color = Colors.white
        self._draw(Suspension.texture_id)

        # Initial padding is 10x44
        rect = copy.copy(self._box.rect)
        rect[0] += 10 * self.__mult
        rect[1] += 44 * self.__mult
        rect[2] -= 20 * self.__mult
        rect[3] -= 88 * self.__mult # 100%

        # Why there is negative and above maximum numbers, KUNOS???
        rect[3] = min(rect[3], max(0.0, rect[3] * (1.0 - travel)))

        ac.glColor4f(*self._back.color)
        ac.glQuad(*rect)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class Temps(BoxComponent):
    """ Class to handle tire temperatures draw. """

    def __init__(self, acd, resolution, wheel):
        self.__calc = TireTemp(acd.get_temp_curve(
            ac.getCarTyreCompound(0), wheel))

        # Initial size is 160x256
        super(Temps, self).__init__(176.0, 0.0, 160.0, 256.0, 16.0)
        self.resize(resolution)

    def draw(self, data):
        # Initial padding is 12x12
        pad = 12 * self.__mult
        pad2 = 2.0 * pad

        quarter = (self._box.rect[3] - pad2) * 0.125
        part = (self._box.rect[2] - pad2) / 3.0
        inner = self._box.rect[0] + pad
        outer = self._box.rect[0] + pad + 2.0 * part
        height = self._box.rect[1] + pad

        temp = data.tire_t_c
        interpolated = self.__calc.interpolate(temp)
        color = self.__calc.interpolate_color(temp, interpolated)
        ac.glColor4f(*color)
        ac.glQuad(inner, height + quarter, part * 3.0, quarter * 6.0)

        temp = data.tire_t_i
        interpolated = self.__calc.interpolate(temp)
        color = self.__calc.interpolate_color(temp, interpolated)
        ac.glColor4f(*color)
        ac.glQuad(inner, height, part, quarter)
        ac.glQuad(inner, height + quarter * 7, part, quarter)

        temp = data.tire_t_m
        interpolated = self.__calc.interpolate(temp)
        color = self.__calc.interpolate_color(temp, interpolated)
        ac.glColor4f(*color)
        ac.glQuad(self._box.rect[0] + pad + part, height, part, quarter)
        ac.glQuad(self._box.rect[0] + pad + part,
                  height + quarter * 7, part, quarter)

        temp = data.tire_t_o
        interpolated = self.__calc.interpolate(temp)
        color = self.__calc.interpolate_color(temp, interpolated)
        ac.glColor4f(*color)
        ac.glQuad(outer, height, part, quarter)
        ac.glQuad(outer, height + quarter * 7, part, quarter)

    def resize_fonts(self, resolution):
        # Initial padding is 12x12
        self.__mult = BoxComponent.resolution_map[resolution]


class Tire(BoxComponent):
    """ Class to handle tire draw. """

    texture_id = 0

    def __init__(self, acd, resolution, wheel):
        self.__calc = TireTemp(acd.get_temp_curve(
            ac.getCarTyreCompound(0), wheel))

        # Initial size is 160x256
        super(Tire, self).__init__(176.0, 0.0, 160.0, 256.0)
        self._back.color = Colors.white

        if Tire.texture_id == 0:
            Tire.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/tire.png")

        self.resize(resolution)

    def draw(self, data):
        """ Draws the tire. """
        temp = data.tire_t_c * 0.75 + \
            ((data.tire_t_i + data.tire_t_m + data.tire_t_o) / 3.0) * 0.25
        interpolated = self.__calc.interpolate(temp)
        self._back.color = self.__calc.interpolate_color(temp, interpolated)
        self._draw(Tire.texture_id)


class Wear(BoxComponent):
    """ Class to handle tire wear draw. """

    def __init__(self, resolution, wheel):
        # Initial size is 14x256 (with borders)
        super(Wear, self).__init__(
            154.0 if wheel.is_left() else 348.0, 2.0, 10.0, 252.0)
        self._back.color = Colors.black
        self._back.border = Colors.white
        self._back.size = 2.0
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, data):
        """ Draws the wear. """
        self._draw()
        wear = data.tire_w
        if wear > 0.98:
            ac.glColor4f(*Colors.green)
        elif wear > 0.96:
            ac.glColor4f(*Colors.yellow)
        else:
            ac.glColor4f(*Colors.red)

        # Initial padding is 10x44
        wear = (wear - 0.94) / 0.06
        rect = copy.copy(self._box.rect)
        rect[1] += (1.0 - wear) * rect[3]
        rect[3] *= wear
        ac.glQuad(*rect)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]
