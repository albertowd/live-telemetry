"""
Module to split and resize components on the screen.
"""
import copy
import ac


class Background(object):
    """ Class to draw a background in a box component. """

    def __init__(self, background=None, border=None, size=1.0):
        if background is None:
            self.background = [0.0, 0.0, 0.0, 0.0]
        else:
            self.background = background

        if border is None:
            self.border = [0.0, 0.0, 0.0, 0.0]
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

        if self.background[3] > 0.0:
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

    def __init__(self, p_x=0.0, p_y=0.0, width=100.0, height=100.0, font=12.0):
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


class Load(BoxComponent):
    """ Class to handle tyre load draw. """

    load_texture_id = 0

    def __init__(self, resolution):
        super(Load, self).__init__(100.0, 0.0, 200.0, 200.0)
        self._back.background = [1.0, 1.0, 1.0, 1.0]
        self.__mult = BoxComponent.resolution_map[resolution]

        if Load.load_texture_id == 0:
            Load.load_texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/load.png")

        self.resize(resolution)

    def draw(self, info):
        """ Draws the tyre. """
        load = info["load"] * self.__mult
        load_2 = load / 2.0
        self._box.set_position(
            self._box.center[0] - load_2, self._box.center[1] - load_2)
        self._box.set_size(load, load)
        self._draw(Load.load_texture_id)

    def resize_fonts(self, resolution):
        self.__mult = BoxComponent.resolution_map[resolution]


class Wheel(BoxComponent):
    """ Class to handle wheel draw. """

    tyre_texture_id = 0

    def __init__(self, resolution, window_id):
        super(Wheel, self).__init__(166.0, 46.0, 68.0, 108.0)
        self._back.background = [1.0, 1.0, 1.0, 1.0]

        if Wheel.tyre_texture_id == 0:
            Wheel.tyre_texture_id = ac.newTexture(
                "apps/python/WheelTelemetry/img/tyre.png")

        self.__lb_pressure_bg = ac.addLabel(window_id, "")
        ac.setBackgroundColor(self.__lb_pressure_bg, 0, 0, 0)
        ac.setBackgroundOpacity(self.__lb_pressure_bg, 1)

        self.__lb_pressure = ac.addLabel(window_id, "- psi")
        ac.setFontAlignment(self.__lb_pressure, "center")

        self.resize(resolution)

    def draw(self, info):
        """ Draws the tyre. """
        self._draw(Wheel.tyre_texture_id)
        ac.setText(self.__lb_pressure, "{:03.1f} psi".format(info["pressure"]))

    def resize_fonts(self, resolution):
        mult = BoxComponent.resolution_map[resolution]
        ac.setPosition(self.__lb_pressure_bg,
                       self._box.rect[0] + (4.0 * mult), self._box.rect[1] + (4.0 * mult))
        ac.setSize(self.__lb_pressure_bg,
                   self._box.rect[2] - (8.0 * mult), self._box.rect[3] - (8.0 * mult))

        ac.setFontSize(self.__lb_pressure, self._font)
        ac.setPosition(self.__lb_pressure,
                       self._box.center[0], self._box.center[1] - (self._font / 2.0))
