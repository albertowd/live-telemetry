"""
Module to split and resize components on the screen.
"""
import copy
import math
import ac
import acsys
from wcolors import Colors
from wlog import log


class Background(object):
    """ Class to draw a background in a box component. """

    def __init__(self, background=None, border=None, size=1.0):
        if background is None:
            self.background = Colors.transparent
        else:
            self.background = background

        if border is None:
            self.border = Colors.transparent
        else:
            self.border = border

        self.size = size

    def draw(self, rect, texture_id=None):
        """ Draws the box background. """
        if self.size > 0.0 and self.border[3] > 0.0:
            twice = self.size * 2.0
            ac.glColor4f(*self.border)
            ac.glQuad(rect[0] - self.size, rect[1] - self.size,
                      rect[2] + twice, rect[3] + twice)

        if self.background[3] > 0.0 and rect[2] is not 0.0 and rect[3] is not 0.0:
            ac.glColor4f(*self.background)
            if texture_id is None:
                ac.glQuad(*rect)
            else:
                ac.glQuadTextured(rect[0], rect[1],
                                  rect[2], rect[3], texture_id)


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

    resolutions = ["HD", "FHD", "2K", "UHD", "4K", "8K"]
    resolution_map = {"HD": 1.0, "FHD": 1.5,
                      "2K": 1.6, "UHD": 3.0, "4K": 3.2, "8K": 6.0}

    def __init__(self, p_x=0.0, p_y=0.0, width=100.0, height=100.0, font=24.0):
        self.__ini_font = font
        self.__ini_box = Box(p_x, p_y, width, height)
        self._back = Background()
        self._box = Box(p_x, p_y, width, height)
        self._font = font

    def _draw(self, texture_id=None):
        """ Draws the component on the screen. """
        self._back.draw(self._box.rect, texture_id)

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


class Camber(BoxComponent):
    """ Class to handle tyre camber draw. """

    def __init__(self, resolution, wheel_id):
        self.__is_left = wheel_id[1] == 'L'

        # Initial size is 160x10
        super(Camber, self).__init__(170.0, 256.0, 172.0, 15.0)
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, info):
        """ Draws the camber below the trye. """
        rect = self._box.rect
        camber = info["camber"]
        tan = math.tan(camber) * rect[2]

        ac.glBegin(acsys.GL.Quads)
        ac.glColor4f(*Colors.white)
        ac.glVertex2f(rect[0], rect[1] - (tan if camber < 0.0 else 0.0))
        ac.glVertex2f(rect[0], rect[1] + rect[3])
        ac.glVertex2f(rect[0] + rect[2], rect[1] + rect[3])
        ac.glVertex2f(rect[0] + rect[2], rect[1] + (tan if camber > 0.0 else 0.0))
        ac.glEnd()

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class Dirt(BoxComponent):
    """ Class to handle tyre dirt draw. """

    def __init__(self, resolution):
        # Initial size is 136x116
        super(Dirt, self).__init__(188.0, 128.0, 136.0, 116.0)
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, info):
        """ Draws the dirt on the tyre. """
        dirt = info["dirt"] * self.__mult

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

    def __init__(self, resolution, wheel_id, window_id):
        is_left = wheel_id[1] == 'L'

        # Initial size is 64x48
        super(Height, self).__init__(
            428.0 if is_left else 20.0, 208.0, 64.0, 48.0)
        self._back.background = Colors.white

        if Height.texture_id == 0:
            Height.texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/height.png")

        self.__lb_height = ac.addLabel(window_id, "- mm")
        ac.setFontAlignment(self.__lb_height, "center")

        self.resize(resolution)

    def draw(self, info):
        """ Draws the height. """
        self._draw(Height.texture_id)
        ac.setText(self.__lb_height, "{:03.1f} mm".format(info["height"]))

    def resize_fonts(self, resolution):
        ac.setFontSize(self.__lb_height, self._font)
        ac.setPosition(self.__lb_height,
                       self._box.center[0], self._box.center[1] - (self._font / 1.25))


class Load(BoxComponent):
    """ Class to handle tyre load draw. """

    texture_id = 0

    def __init__(self, resolution):
        super(Load, self).__init__(128.0, 0.0, 256.0, 256.0)
        self._back.background = Colors.white
        self.__mult = BoxComponent.resolution_map[resolution]

        if Load.texture_id == 0:
            Load.texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/load.png")

        self.resize(resolution)

    def draw(self, info):
        """ Draws the tyre. """
        load = info["load"] * self.__mult
        load_2 = load / 2.0
        self._box.set_position(
            self._box.center[0] - load_2, self._box.center[1] - load_2)
        self._box.set_size(load, load)
        self._draw(Load.texture_id)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class PressureAndTemps(BoxComponent):
    """ Class to handle tyre pressure and temps draw. """

    def __init__(self, resolution, window_id):
        # Initial size is 160x256
        super(PressureAndTemps, self).__init__(176.0, 0.0, 160.0, 256.0)

        self.__lb_pressure_bg = ac.addLabel(window_id, "")
        ac.setBackgroundColor(self.__lb_pressure_bg, 0, 0, 0)
        ac.setBackgroundOpacity(self.__lb_pressure_bg, 1)

        self.__lb_pressure = ac.addLabel(window_id, "- psi")
        ac.setFontAlignment(self.__lb_pressure, "center")

        self.resize(resolution)

    def draw(self, info):
        """ Draws the pressure and temps. """
        ac.setText(self.__lb_pressure, "{:03.1f} psi".format(info["pressure"]))

    def resize_fonts(self, resolution):
        # Initial padding is 12x12
        pad = 12 * BoxComponent.resolution_map[resolution]
        ac.setPosition(self.__lb_pressure_bg,
                       self._box.rect[0] + pad, self._box.rect[1] + pad)
        ac.setSize(self.__lb_pressure_bg,
                   self._box.rect[2] - (1.0 * pad), self._box.rect[3] - (2.0 * pad))

        ac.setFontSize(self.__lb_pressure, self._font)
        ac.setPosition(self.__lb_pressure,
                       self._box.center[0], self._box.center[1] - (self._font / 2.0))


class Suspension(BoxComponent):
    """ Class to handle suspension draw. """

    texture_id = 0

    def __init__(self, resolution, wheel_id):
        is_left = wheel_id[1] == 'L'

        # Initial size is 64x256
        super(Suspension, self).__init__(
            346.0 if is_left else 102.0, 0.0, 64.0, 256.0)
        self._back.background = Colors.white
        self.__mult = BoxComponent.resolution_map[resolution]

        if Suspension.texture_id == 0:
            Suspension.texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/suspension.png")

        self.resize(resolution)

    def draw(self, info):
        """ Draws the suspension. """
        travel = info["suspension"]
        if travel > 0.9 or travel < 0.1:
            self._back.background = Colors.red
        if travel > 0.8 or travel < 0.2:
            self._back.background = Colors.yellow
        else:
            self._back.background = Colors.white
        self._draw(Suspension.texture_id)

        # Initial padding is 10x44
        rect = copy.copy(self._box.rect)
        rect[0] += 10 * self.__mult
        rect[1] += 44 * self.__mult
        rect[2] -= 20 * self.__mult
        rect[3] -= 88 * self.__mult

        rect[1] += (1.0 - travel) * rect[3]
        rect[3] *= travel

        ac.glColor4f(*self._back.background)
        ac.glQuad(*rect)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class Tyre(BoxComponent):
    """ Class to handle tyre draw. """

    texture_id = 0

    def __init__(self, resolution):
        # Initial size is 160x256
        super(Tyre, self).__init__(176.0, 0.0, 160.0, 256.0)
        self._back.background = Colors.white

        if Tyre.texture_id == 0:
            Tyre.texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/tyre.png")

        self.resize(resolution)

    def draw(self, info):
        """ Draws the tyre. """
        self._draw(Tyre.texture_id)


class Wear(BoxComponent):
    """ Class to handle tyre wear draw. """

    def __init__(self, resolution, wheel_id):
        is_left = wheel_id[1] == 'L'

        # Initial size is 14x256 (with borders)
        super(Wear, self).__init__(
            154.0 if is_left else 348.0, 2.0, 10.0, 252.0)
        self._back.background = Colors.black
        self._back.border = Colors.white
        self._back.size = 2.0
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, info):
        """ Draws the wear. """
        self._draw()
        wear = info["wear"] / 100.0
        if wear > 0.98:
            ac.glColor4f(*Colors.green)
        elif wear > 0.96:
            ac.glColor4f(*Colors.yellow)
        else:
            ac.glColor4f(*Colors.red)

        # Initial padding is 10x44
        rect = copy.copy(self._box.rect)
        rect[1] += (1.0 - wear) * rect[3]
        rect[3] *= wear
        ac.glQuad(*rect)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]
