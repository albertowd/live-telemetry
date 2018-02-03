"""
Module to split and resize components on the screen.
"""
import copy
import math
import ac
import acsys
from wcolors import Colors
from wutil import log, psi_color, temp_color


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


class Brake(BoxComponent):
    """ Class to handle brake draw. """

    texture_id = 0

    def __init__(self, resolution, wheel_id, window_id):
        is_left = wheel_id[1] == 'L'

        # Initial size is 96x96
        super(Brake, self).__init__(
            46.0 if is_left else 370.0, 0.0, 96.0, 96.0)
        self._back.background = Colors.white

        if Brake.texture_id == 0:
            Brake.texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/brake.png")

        self.__lb = ac.addLabel(window_id, "- ºC")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def draw(self, data):
        self._draw(Brake.texture_id)
        ac.setText(self.__lb, "{:3.0f} ºC".format(data.brake_t))

    def resize_fonts(self, resolution):
        ac.setFontSize(self.__lb, self._font)
        rect = self._box.rect
        ac.setPosition(
            self.__lb, self._box.center[0], rect[1] + rect[3])


class Camber(BoxComponent):
    """ Class to handle tyre camber draw. """

    def __init__(self, resolution, wheel_id):
        self.__is_left = wheel_id[1] == 'L'

        # Initial size is 160x10
        super(Camber, self).__init__(170.0, 256.0, 172.0, 15.0)
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, data):
        rect = self._box.rect
        camber = data.camber
        tan = math.tan(camber) * rect[2]
        tan_left = - (tan if camber < 0.0 else 0.0)
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
    """ Class to handle tyre dirt draw. """

    def __init__(self, resolution):
        # Initial size is 136x116
        super(Dirt, self).__init__(188.0, 128.0, 136.0, 116.0)
        self.__mult = BoxComponent.resolution_map[resolution]

        self.resize(resolution)

    def draw(self, data):
        dirt = data.tyre_d * self.__mult

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
            20.0 if is_left else 428.0, 208.0, 64.0, 48.0)
        self._back.background = Colors.white

        if Height.texture_id == 0:
            Height.texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/height.png")

        self.__lb = ac.addLabel(window_id, "- mm")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def draw(self, data):
        self._draw(Height.texture_id)
        ac.setText(self.__lb, "{:03.1f} mm".format(data.height))

    def resize_fonts(self, resolution):
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(
            self.__lb, self._box.center[0], self._box.center[1] - (self._font / 1.25))


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

    def draw(self, data):
        load = data.tyre_l * self.__mult
        load_2 = load / 2.0
        self._box.set_position(
            self._box.center[0] - load_2, self._box.center[1] - load_2)
        self._box.set_size(load, load)
        self._draw(Load.texture_id)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


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

    def draw(self, data):
        travel = data.susp_t
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


class Temps(BoxComponent):
    """ Class to handle tyre temperatures draw. """

    def __init__(self, resolution, wheel_id, window_id):
        self.__is_left = wheel_id[1] == 'L'

        # Initial size is 160x256
        super(Temps, self).__init__(176.0, 0.0, 160.0, 256.0, 16)

        self.__lb_bg_i = ac.addLabel(window_id, "-\nºC")
        ac.setBackgroundColor(self.__lb_bg_i, 0.0, 0.0, 0.0)
        ac.setBackgroundOpacity(self.__lb_bg_i, 1.0)

        self.__lb_bg_m = ac.addLabel(window_id, "-\nºC")
        ac.setBackgroundColor(self.__lb_bg_m, 0.0, 0.0, 0.0)
        ac.setBackgroundOpacity(self.__lb_bg_m, 1.0)

        self.__lb_bg_o = ac.addLabel(window_id, "-\nºC")
        ac.setBackgroundColor(self.__lb_bg_o, 0.0, 0.0, 0.0)
        ac.setBackgroundOpacity(self.__lb_bg_o, 1.0)

        self.resize(resolution)

    def draw(self, data):
        temp = data.tyre_t_i
        #color = temp_color("Street", temp)
        # log(color)
        # ac.glColor4f(*Colors.white)
        #ac.setBackgroundOpacity(self.__lb_bg_i, color[3])
        #ac.setBackgroundColor(self.__lb_bg_i, color[0], color[1], color[2])
        ac.setText(self.__lb_bg_i, "{:3.0f}\nºC".format(temp))

        temp = data.tyre_t_m
        #color = temp_color("Street", temp)
        # ac.glColor4f(*Colors.white)
        #ac.setBackgroundOpacity(self.__lb_bg_m, color[3])
        #ac.setBackgroundColor(self.__lb_bg_m, color[0], color[1], color[2])
        ac.setText(self.__lb_bg_m, "{:3.0f}\nºC".format(temp))

        temp = data.tyre_t_o
        #color = temp_color("Street", temp)
        # ac.glColor4f(*Colors.white)
        #ac.setBackgroundOpacity(self.__lb_bg_o, color[3])
        #ac.setBackgroundColor(self.__lb_bg_o, color[0], color[1], color[2])
        ac.setText(self.__lb_bg_o, "{:3.0f}\nºC".format(temp))

    def resize_fonts(self, resolution):
        # Initial padding is 12x12
        pad = 12 * BoxComponent.resolution_map[resolution]
        height = self._box.rect[3] - (2.0 * pad)
        part = (self._box.rect[2] - (2.0 * pad)) / 3.0

        inner = part * (2.0 if self.__is_left else 0.0)
        outer = part * (0.0 if self.__is_left else 2.0)

        ac.setFontSize(self.__lb_bg_i, self._font)
        ac.setPosition(
            self.__lb_bg_i, self._box.rect[0] + pad + inner, self._box.rect[1] + pad)
        ac.setSize(self.__lb_bg_i, part, height)

        ac.setFontSize(self.__lb_bg_m, self._font)
        ac.setPosition(
            self.__lb_bg_m, self._box.rect[0] + pad + part, self._box.rect[1] + pad)
        ac.setSize(self.__lb_bg_m, part, height)

        ac.setFontSize(self.__lb_bg_o, self._font)
        ac.setPosition(
            self.__lb_bg_o, self._box.rect[0] + pad + outer, self._box.rect[1] + pad)
        ac.setSize(self.__lb_bg_o, part, height)


class TyreAndPsi(BoxComponent):
    """ Class to handle tyre and pressure draw. """

    texture_id = 0

    def __init__(self, resolution, window_id):
        # Initial size is 160x256
        super(TyreAndPsi, self).__init__(176.0, 0.0, 160.0, 256.0)
        self._back.background = Colors.white

        if TyreAndPsi.texture_id == 0:
            TyreAndPsi.texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/tyre.png")

        self.__lb = ac.addLabel(window_id, "- psi")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def draw(self, data):
        """ Draws the tyre. """
        #log("psi {}".format(data.tyre_p))
        #color = psi_color("Street", data.tyre_p)
        #self._back.background = color
        self._draw(TyreAndPsi.texture_id)
        ac.setText(self.__lb, "{:03.1f} psi".format(data.tyre_p))

    def resize_fonts(self, resolution):
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(
            self.__lb, self._box.center[0], self._box.center[1] - (self._font / 2.0))


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

    def draw(self, data):
        """ Draws the wear. """
        self._draw()
        wear = data.tyre_w
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
