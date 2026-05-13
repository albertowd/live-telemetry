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

from lib.lt_acd import ACD
from lib.lt_colors import Colors
from lib.lt_interpolation import Power, TirePsi, TireTemp


WARNING_TIME_S = 0.5
LOCK_BLINK_PERIOD_S = 0.1  # 5 Hz blink rate for the lock indicator.

# Contact-patch heuristic constants (ported from live-telemetry-ac-evo).
# AC1 doesn't publish tyre dimensions, so this is qualitative.
_CAMBER_FULL_BIAS_RAD = math.radians(4.0)
_PRESSURE_FULL_BIAS = 0.50
_PRESSURE_AMP = 0.3
_LOAD_FULL_N = 6000.0
_LOAD_FLOOR = 0.30

# Polygonal approximation for the suspension widget's mount-point rings.
_SUSP_RING_SEGMENTS = 16


class Background:  # pylint: disable=too-few-public-methods
    """ Class to draw a background in a box component. """

    def __init__(self, color=Colors.transparent, border=Colors.transparent, size=1.0):
        self.color = color
        self.border = border
        self.size = size

    def draw(self, rect, texture_id=None) -> None:
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


class Box:
    """ Class to handle a box component with background. """

    def __init__(self, p_x=0.0, p_y=0.0, width=100.0, height=100.0):
        self.center = [0.0, 0.0]
        self.rect = [p_x, p_y, width, height]
        self.recalc_center()

    def recalc_center(self) -> None:
        """ Recalculate the box middle point. """
        self.center[0] = self.rect[0] + (self.rect[2] / 2.0)
        self.center[1] = self.rect[1] + (self.rect[3] / 2.0)

    def set_position(self, pos_x, pos_y) -> None:
        """ Updates the box position. """
        self.rect[0] = pos_x
        self.rect[1] = pos_y

    def set_size(self, width, height) -> None:
        """ Updates the box size. """
        self.rect[2] = width
        self.rect[3] = height


class BoxComponent:
    """ Class to handle position and resize of a component. """

    resolutions = ["240p", "360p", "480p", "576p","HD", "FHD", "1440p", "UHD", "4K", "8K"]
    resolution_map = {"240p": 0.16, "360p": 0.25, "480p": 0.33, "576p": 0.4, "HD": 0.5, "FHD": 0.75, "1440p": 1.0, "UHD": 1.5, "4K": 1.6, "8K": 3.0}

    # Tire-centre rotation pivot in unrotated logical coords; shared
    # by Tire / Temps / Dirt so they tilt together under camber.
    _TIRE_PIVOT_LOGICAL = (256.0, 128.0)

    def __init__(self, p_x=0.0, p_y=0.0, width=100.0, height=100.0, *, font=24.0):  # pylint: disable=too-many-arguments
        self.__ini_font = font
        self.__ini_box = Box(p_x, p_y, width, height)
        self._back = Background()
        self._box = Box(p_x, p_y, width, height)
        self._font = font
        self._mult = 1.0

    def clear(self) -> None:
        """Clear labels to not draw anything on screen."""

    def _draw(self, texture_id=None) -> None:
        """ Draws the component on the screen. """
        self._back.draw(self._box.rect, texture_id)

    def draw(self, data, delta_t: float) -> None:
        """ Draw the component contents after the base. """

    def resize(self, resolution="HD") -> None:
        """ Resizes the component. """
        mult = BoxComponent.resolution_map[resolution]
        self._mult = mult
        self._box.set_position(
            self.__ini_box.rect[0] * mult, self.__ini_box.rect[1] * mult)
        self._box.set_size(
            self.__ini_box.rect[2] * mult, self.__ini_box.rect[3] * mult)
        self._box.recalc_center()
        self._font = self.__ini_font * mult
        self.resize_fonts(resolution)

    def resize_fonts(self, resolution: str) -> None:
        """ Resize all the ac components with text. Must be overrided. """

    @staticmethod
    def _rotate(offset: tuple, centre: tuple, trig: tuple) -> tuple:
        """ Rotates ``offset = (dx, dy)`` around ``centre = (cx, cy)``
        using pre-computed ``trig = (cos, sin)``. """
        dx, dy = offset
        cx, cy = centre
        cos_a, sin_a = trig
        return (cx + cos_a * dx - sin_a * dy,
                cy + sin_a * dx + cos_a * dy)

    def _camber_rotation(self, camber: float) -> tuple:
        """ Returns ``(pivot, trig)`` for the shared tire-pivot rotation. """
        pivot = (BoxComponent._TIRE_PIVOT_LOGICAL[0] * self._mult,
                 BoxComponent._TIRE_PIVOT_LOGICAL[1] * self._mult)
        angle = -camber * _TIRE_CAMBER_AMPLIFY
        return pivot, (math.cos(angle), math.sin(angle))

    def _emit_rotated_quad(self, offsets: tuple, pivot: tuple, trig: tuple) -> None:
        """ One rotated quad: 4 local offsets from ``pivot``, single
        ``glBegin(Quads)`` (AC1 honours only one quad per begin). """
        ac.glBegin(acsys.GL.Quads)
        for offset in offsets:
            ax, ay = self._rotate(offset, pivot, trig)
            ac.glVertex2f(ax, ay)
        ac.glEnd()

    def _emit_rotated_rect(self, rect: tuple, pivot: tuple, trig: tuple) -> None:
        """ ``_emit_rotated_quad`` for an axis-aligned ``(x, y, w, h)`` rect. """
        x, y, w, h = rect
        px, py = pivot
        self._emit_rotated_quad(
            ((x - px, y - py), (x + w - px, y - py),
             (x + w - px, y + h - py), (x - px, y + h - py)),
            pivot, trig)


class BoostBar(BoxComponent):
    """ Class to handle boost bar change. """

    def __init__(self, _acd: ACD, resolution: str, window_id: int):
        # Initial size is 512x85
        super().__init__(0.0, -24.0, 512.0, 24.0)
        self._back.color = Colors.black

        self.__lb = ac.addLabel(window_id, "- bar")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb, "")

    def draw(self, data, delta_t: float) -> None:
        self._draw()

        turbo_boost = data.turbo_boost
        ratio = max(0.0, turbo_boost / max(0.1, data.max_turbo_boost))

        p_bar = copy.copy(self._box.rect)
        p_bar[2] *= ratio

        color = Colors.white if ratio < 0.9 else Colors.green
        ac.glColor4f(*color)
        ac.glQuad(*p_bar)

        ac.setFontColor(self.__lb, color[0], color[1], color[2], color[3])
        ac.setText(self.__lb, "{:.2f} bar".format(max(0.0, turbo_boost)))

    def resize_fonts(self, resolution: str) -> None:
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(self.__lb, self._box.center[0], self._box.rect[1] - self._font - 8)


class Camber(BoxComponent):
    """ Contact-patch load-distribution heuristic — three bars under
    the tire showing inner / middle / outer loading from a
    camber × pressure × load heuristic (ported from
    live-telemetry-ac-evo). INNER sits on the screen-centre-facing
    side; class kept named ``Camber`` so the existing option still
    toggles it. """

    def __init__(self, acd: ACD, resolution: str, wheel):
        # Same rect as the old trapezoidal Camber strip — flush with tire bottom.
        super().__init__(188.0, 256.0, 136.0, 15.0)
        self.__wheel = wheel
        # Per-axle ideal pressure for the pressure-bias term. Falls back to
        # TirePsi's 26 psi default on any ACD parse failure (ConfigParser
        # errors, missing keys, unparseable mod data).
        ideal = None
        try:
            ideal = acd.get_ideal_pressure(ac.getCarTyreCompound(0), wheel)
        except Exception:  # pylint: disable=broad-except
            ideal = None
        self.__ideal_psi = float(ideal) if ideal and ideal > 0.0 else 26.0
        self.resize(resolution)

    def _zone_weights(self, data) -> tuple:
        """ Returns (inner, middle, outer, load_factor) — extracted
        from ``draw`` to fit pylint's locals budget. """
        # Sign-correct camber, clamp to [-1, +1] (full inner / outer).
        camber_n = data.camber * (1.0 if self.__wheel.is_left() else -1.0)
        camber_axis = max(-1.0, min(1.0, camber_n / _CAMBER_FULL_BIAS_RAD))

        # Pressure bias: +1 bowed (edges carry), -1 crowned (centre).
        tire_p_norm = data.tire_p / self.__ideal_psi if self.__ideal_psi > 0.0 else 1.0
        p_bias = max(-1.0, min(1.0, (1.0 - tire_p_norm) / _PRESSURE_FULL_BIAS))

        # Load magnitude scales the patch. data.tire_l is in N/(5g).
        load_n = max(0.0, min(1.0, (data.tire_l * 5.0 * 9.80665) / _LOAD_FULL_N))
        load_factor = _LOAD_FLOOR + (1.0 - _LOAD_FLOOR) * load_n

        # Camber factor: inner / outer fade with axis; middle is the
        # edge average so a bowed tyre doesn't push middle below outer.
        inner_c = max(0.0, 1.0 - max(0.0, camber_axis))
        outer_c = max(0.0, 1.0 + min(0.0, camber_axis))
        edge_p = 1.0 + p_bias * _PRESSURE_AMP
        return (inner_c * edge_p,
                (inner_c + outer_c) * 0.5 * (1.0 - p_bias * _PRESSURE_AMP),
                outer_c * edge_p,
                load_factor)

    def draw(self, data, delta_t: float) -> None:
        rect = self._box.rect
        seg_w = rect[2] / 3.0
        max_h = rect[3]

        inner_w, middle_w, outer_w, load_factor = self._zone_weights(data)

        # Mirror the IMO band convention: INNER on screen-centre-facing
        # side, OUTER on screen-edge-facing side.
        if self.__wheel.is_left():
            inner_x, outer_x = rect[0] + 2.0 * seg_w, rect[0]
        else:
            inner_x, outer_x = rect[0], rect[0] + 2.0 * seg_w

        ac.glColor4f(*Colors.white)
        for weight, x in ((inner_w, inner_x),
                          (middle_w, rect[0] + seg_w),
                          (outer_w, outer_x)):
            h = max(0.0, min(1.0, weight * load_factor)) * max_h
            if h < 0.5:
                continue
            ac.glQuad(x, rect[1], seg_w, h)


class Dirt(BoxComponent):
    """ Class to handle tire dirt draw. Rotates with the tire so the
    dirt level visibly follows the tire's camber tilt. """

    def __init__(self, resolution: str):
        # Initial size is 136x116
        super().__init__(188.0, 128.0, 136.0, 116.0)
        self.resize(resolution)

    def draw(self, data, delta_t: float) -> None:
        dirt = data.tire_d * self._mult
        rect = (self._box.rect[0],
                self._box.rect[1] + self._box.rect[3] - dirt,
                self._box.rect[2],
                dirt)
        pivot, trig = self._camber_rotation(data.camber)
        ac.glColor4f(*Colors.brown)
        self._emit_rotated_rect(rect, pivot, trig)


class Height(BoxComponent):
    """ Ride-height widget rebuilt as pure GL primitives — matches
    ``height.svg`` (2048×1536 path, scaled 1:32 into the 64×48
    widget). Geometry:

    * 2 horizontal quads form the reference-surface bars (top and
      bottom rails).
    * 2 triangles point inward at each bar (up-arrow at the top,
      down-arrow at the bottom).

    Bars and arrows are slimmer than the SVG (4 / 5 px instead of
    5 / 6 px) so the gap between rails opens from 26 to 30 logical
    px — the height readout sits in that gap and now has breathing
    room above and below. Text is properly vertically centred (text
    height ≈ 1.2 × font, so anchor = centre − font·0.6).

    Colour flips to red for ``WARNING_TIME_S`` after the ride height
    drops below 0.02 mm (kerb-strike / bottom-out indicator). Bars,
    arrows, and the readout all share the warning colour so the
    alert is unmistakable.
    """

    def __init__(self, resolution: str, wheel, window_id: int):
        # 64×48. Flush with the widget edge so the suspension widget
        # can be pushed outward (46 px from the tire) without
        # overlapping this row in the y=208-256 band.
        super().__init__(
            448.0 if wheel.is_left() else 0.0, 208.0, 64.0, 48.0)
        self._back.color = Colors.white
        self.__warn_time = 0.0

        self.__lb = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb, "")

    def draw(self, data, delta_t: float) -> None:
        if data.height < 0.02:
            self.__warn_time = WARNING_TIME_S
        if self.__warn_time - delta_t > 0.0:
            color = Colors.red
            self.__warn_time -= delta_t
        else:
            color = Colors.white
        self._back.color = color
        ac.glColor4f(*color)

        m = self._mult
        rx, ry = self._box.rect[0], self._box.rect[1]
        w = self._box.rect[2]
        h = self._box.rect[3]
        bar_h = 4.0 * m
        arrow_h = 5.0 * m
        arrow_half_w = 6.0 * m
        cx = rx + w * 0.5

        # 2 reference-surface bars (top + bottom).
        ac.glQuad(rx, ry, w, bar_h)
        ac.glQuad(rx, ry + h - bar_h, w, bar_h)

        # 2 arrow triangles — top points up at the top bar, bottom
        # points down at the bottom bar.
        top_apex_y = ry + bar_h
        top_base_y = top_apex_y + arrow_h
        ac.glBegin(acsys.GL.Triangles)
        ac.glVertex2f(cx, top_apex_y)
        ac.glVertex2f(cx - arrow_half_w, top_base_y)
        ac.glVertex2f(cx + arrow_half_w, top_base_y)
        ac.glEnd()

        bot_apex_y = ry + h - bar_h
        bot_base_y = bot_apex_y - arrow_h
        ac.glBegin(acsys.GL.Triangles)
        ac.glVertex2f(cx, bot_apex_y)
        ac.glVertex2f(cx - arrow_half_w, bot_base_y)
        ac.glVertex2f(cx + arrow_half_w, bot_base_y)
        ac.glEnd()

        ac.setText(self.__lb, "{:03.1f} mm".format(data.height))
        ac.setFontColor(self.__lb, *color)

    def resize_fonts(self, resolution: str) -> None:
        ac.setFontSize(self.__lb, self._font)
        # Vertically centred between the two arrow bases. AC1 anchors
        # the label by its top edge and its baseline sits low inside
        # the rendered glyph box, so the visible centre of the text
        # ends up *below* the geometric centre at the offset implied
        # by half the font height. Bumping the offset to `font · 0.8`
        # nudges the text up enough that the x-height of the readout
        # lines up with the centre of the gap between the bars.
        ac.setPosition(
            self.__lb, self._box.center[0],
            self._box.center[1] - self._font * 0.8)


class Load(BoxComponent):
    """ Tire-load circle (from live-telemetry-ac-evo). Diameter scales
    linearly with N via ``_LOAD_PX_PER_N``, clamped to the tire width;
    hidden when sub-pixel so a light wheel shrinks to nothing. """

    texture_id = 0

    def __init__(self, resolution: str, _wheel):
        super().__init__(128.0, 0.0, 256.0, 256.0)
        self._back.color = Colors.white

        if Load.texture_id == 0:
            Load.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/load.png")

        self.resize(resolution)

    def draw(self, data, delta_t: float) -> None:
        # ``data.tire_l`` is wheelLoad in ``N / (5 g)`` units; convert
        # back to Newtons for the evo px-per-Newton calibration.
        load_n = data.tire_l * (5.0 * 9.80665)
        diameter = max(0.0, min(_LOAD_DIAMETER_MAX_LOGICAL,
                                load_n * _LOAD_PX_PER_N))
        if diameter < _LOAD_HIDE_BELOW:
            return
        diameter *= self._mult
        half = diameter * 0.5
        self._box.set_position(self._box.center[0] - half,
                               self._box.center[1] - half)
        self._box.set_size(diameter, diameter)
        self._draw(Load.texture_id)


class Lock(BoxComponent):
    """ Class to handle tire lock draw. """

    texture_id = 0

    def __init__(self, acd: ACD, resolution: str, wheel):
        abs_hz = acd.get_abs_hz()
        self.__abs_cycle = (1.0 / abs_hz) if abs_hz > 0.0 else 3600.0
        self.__abs_timeout_s = 0.0 if abs_hz > 0.0 else 3600.0

        # Initial size is 85x85
        super().__init__(
            70.0 if wheel.is_left() else 382.0, 0.0, 60.0, 60.0)
        self._back.color = Colors.white
        self.__lock_time = 0.0
        self.__lock_blink_t = 0.0

        if Lock.texture_id == 0:
            Lock.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/brake.png")

        self.resize(resolution)

    def draw(self, data, delta_t: float) -> None:
        self.__abs_timeout_s -= delta_t
        self.__lock_time -= delta_t

        abs_active = False
        lock = data.lock

        if lock is True:
            self.__lock_time = WARNING_TIME_S

        if data.abs_active:
            # Only release the brake if the elapsed time matches the ABS timeout.
            if self.__abs_timeout_s <= 0.0:
                abs_active = True
                self.__abs_timeout_s = self.__abs_cycle

        if abs_active:
            self.__lock_blink_t = 0.0
            self._back.color = Colors.blue
        elif self.__lock_time > 0.0:
            # Blink yellow/white at LOCK_BLINK_PERIOD_S to make the lock more visible.
            self.__lock_blink_t += delta_t
            blink_on = int(self.__lock_blink_t / LOCK_BLINK_PERIOD_S) % 2 == 0
            self._back.color = Colors.yellow if blink_on else Colors.white
        else:
            self.__lock_blink_t = 0.0
            self._back.color = Colors.white

        self._draw(Lock.texture_id)


class Pressure(BoxComponent):
    """ Class to handle tire pressure draw. """

    texture_id = 0

    def __init__(self, acd: ACD, resolution: str, wheel, window_id: int):
        self.__calc = TirePsi(acd.get_ideal_pressure(
            ac.getCarTyreCompound(0), wheel))

        # Initial size is 85x85
        super().__init__(
            70.0 if wheel.is_left() else 382.0, 171.0, 60.0, 60.0)
        self._back.color = Colors.white

        if Pressure.texture_id == 0:
            Pressure.texture_id = ac.newTexture(
                "apps/python/LiveTelemetry/img/pressure.png")

        self.__lb = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb, "")

    def draw(self, data, delta_t: float) -> None:
        psi = data.tire_p
        ac.setText(self.__lb, "{:3.1f} psi".format(psi))

        color = self.__calc.interpolate_color(psi)
        ac.setFontColor(self.__lb, color[0], color[1], color[2], color[3])
        self._back.color = color
        self._draw(Pressure.texture_id)

    def resize_fonts(self, resolution: str) -> None:
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(
            self.__lb, self._box.center[0], self._box.rect[1] + self._box.rect[3])


class RPMPower(BoxComponent):
    """ Class to handle best power change. """

    def __init__(self, acd: ACD, resolution: str, window_id: int):
        self.__calc = Power(acd.get_power_curve())

        # Initial size is 512x85
        super().__init__(0.0, 0.0, 512.0, 50.0)
        self._back.color = Colors.black

        self.__lb_hp = ac.addLabel(window_id, "- HP")
        ac.setFontAlignment(self.__lb_hp, "left")

        self.__lb_rpm = ac.addLabel(window_id, "- RPM")
        ac.setFontAlignment(self.__lb_rpm, "right")

        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb_hp, "")
        ac.setText(self.__lb_rpm, "")

    def draw(self, data, delta_t: float) -> None:
        self._draw()

        rpm = data.rpm
        ratio = min(rpm / data.max_rpm, 1.0)
        torque = self.__calc.interpolate(rpm)
        hp = int(torque * ( 1.0 + data.turbo_boost))

        p_bar = copy.copy(self._box.rect)
        p_bar[2] *= ratio

        color = self.__calc.interpolate_color(rpm)
        ac.glColor4f(*color)
        ac.glQuad(*p_bar)

        ac.setFontColor(self.__lb_hp, color[0], color[1], color[2], color[3])
        ac.setText(self.__lb_hp, "{} HP".format(hp))
        ac.setFontColor(self.__lb_rpm, color[0], color[1], color[2], color[3])
        ac.setText(self.__lb_rpm, "{} RPM".format(rpm))

    def resize_fonts(self, resolution: str) -> None:
        ac.setFontSize(self.__lb_hp, self._font)
        ac.setPosition(
            self.__lb_hp, self._box.rect[0], self._box.rect[1] + self._box.rect[3])
        ac.setFontSize(self.__lb_rpm, self._font)
        ac.setPosition(
            self.__lb_rpm, self._box.rect[0] + self._box.rect[2], self._box.rect[1] + self._box.rect[3])


class Suspension(BoxComponent):
    """ Strut silhouette rebuilt as pure GL quads — matches
    ``suspension.svg`` (512×2048 path, scaled 1:8 into the 64×256
    widget). Geometry:

    * 4 quads form the hollow rectangular body frame (left / right /
      top / bottom walls, each 10 logical px thick) — same outline as
      the SVG's evenodd outer-minus-inner path.
    * 2 mount-point rings (top + bottom) are approximated as
      16-segment annular fans — donut shape from the SVG packers path
      (outer r=22, inner r=10 in logical px).

    A coloured inner-fill quad still sits inside the hollow and
    shrinks as the suspension compresses (parity with the legacy
    texture widget: solid at full extension, empty at full
    compression). The whole shape is recoloured per frame based on
    travel: red at the limits, yellow nearing them, blue when running
    on a dynamic ``susp_v`` max, white otherwise.
    """

    def __init__(self, resolution: str, wheel):
        # 64×256 logical. Inboard edge sits ~26 px from the tire — more
        # than the ~13 px needed for ±6° camber-rotated corners to
        # clear this widget, while leaving a healthy gap (~22 px) to
        # the ride-height widget sitting flush against the widget edge.
        super().__init__(
            362.0 if wheel.is_left() else 86.0, 0.0, 64.0, 256.0)
        self._back.color = Colors.white
        self.__mult = BoxComponent.resolution_map[resolution]
        self.resize(resolution)

    def draw(self, data, delta_t: float) -> None:
        travel = (data.susp_t / data.susp_m_t) if data.susp_m_t > 0.0 else 0.5
        if travel > 0.95 or travel < 0.05:
            self._back.color = Colors.red
        elif travel > 0.90 or travel < 0.1:
            self._back.color = Colors.yellow
        else:
            self._back.color = Colors.blue if data.susp_v else Colors.white
        ac.glColor4f(*self._back.color)

        m = self.__mult
        rx, ry = self._box.rect[0], self._box.rect[1]
        wall = 10.0 * m
        body_top = ry + 34.0 * m
        body_bot = ry + 222.0 * m
        body_h = body_bot - body_top
        inner_left = rx + 10.0 * m
        inner_right = rx + 54.0 * m
        inner_top = ry + 44.0 * m
        inner_bot = ry + 212.0 * m
        inner_w = inner_right - inner_left

        # 4 body-frame quads (left / right / top / bottom walls).
        ac.glQuad(rx, body_top, wall, body_h)
        ac.glQuad(inner_right, body_top, wall, body_h)
        ac.glQuad(inner_left, body_top, inner_w, wall)
        ac.glQuad(inner_left, inner_bot, inner_w, wall)

        # Mount-point rings — centres at (32, 22) and (32, 234) in
        # logical coords (matches the SVG packers path).
        self._emit_ring(rx + 32.0 * m, ry + 22.0 * m)
        self._emit_ring(rx + 32.0 * m, ry + 234.0 * m)

        # Inner travel fill — same colour as the frame; height shrinks
        # toward zero as the strut compresses.
        fill_h = min(inner_bot - inner_top,
                     max(0.0, (inner_bot - inner_top) * (1.0 - travel)))
        if fill_h > 0.0:
            ac.glQuad(inner_left, inner_top, inner_w, fill_h)

    def _emit_ring(self, cx: float, cy: float) -> None:
        """ ``_SUSP_RING_SEGMENTS`` trapezoidal quads spanning the
        annulus between the inner and outer radii. """
        m = self.__mult
        r_o = 22.0 * m
        r_i = 10.0 * m
        step = (2.0 * math.pi) / _SUSP_RING_SEGMENTS
        for i in range(_SUSP_RING_SEGMENTS):
            t1 = step * i
            t2 = step * (i + 1)
            c1, s1 = math.cos(t1), math.sin(t1)
            c2, s2 = math.cos(t2), math.sin(t2)
            ac.glBegin(acsys.GL.Quads)
            ac.glVertex2f(cx + r_i * c1, cy + r_i * s1)
            ac.glVertex2f(cx + r_o * c1, cy + r_o * s1)
            ac.glVertex2f(cx + r_o * c2, cy + r_o * s2)
            ac.glVertex2f(cx + r_i * c2, cy + r_i * s2)
            ac.glEnd()

    def resize_fonts(self, resolution: str) -> None:
        self.__mult = BoxComponent.resolution_map[resolution]


class Temps(BoxComponent):  # pylint: disable=too-many-instance-attributes
    """ IMO temperature grid (inner / middle / outer bumps + core fill)
    with per-zone text readouts. INNER always sits on the screen-centre-
    facing side. Grid quads rotate with the tire via the shared pivot;
    label positions follow the rotation each frame so the numbers stay
    visually attached to their bump under camber (AC1 can't rotate the
    glyphs themselves, but it does honour per-frame ``setPosition``). """

    def __init__(self, acd: ACD, resolution: str, wheel, window_id: int):
        self.__calc = TireTemp(acd.get_temp_curve(
            ac.getCarTyreCompound(0), wheel))
        self.__wheel = wheel

        # Initial size is 160x256
        super().__init__(176.0, 0.0, 160.0, 256.0, font=12.0)
        self.__mult = 1.0
        # Geometry cached in resize_fonts and consumed both by draw()
        # (for the rotated quads) and by the per-frame label
        # repositioning below.
        self.__band_left = 0.0
        self.__inner_x = 0.0
        self.__middle_x = 0.0
        self.__outer_x = 0.0
        self.__top_y = 0.0
        self.__part = 0.0
        self.__quarter = 0.0
        self.__zone_font = 8.0
        self.__core_font = 16.0

        # Per-zone labels. clear() blanks the text — AC has no removeLabel.
        self.__lb_i = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb_i, "center")
        self.__lb_m = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb_m, "center")
        self.__lb_o = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb_o, "center")
        self.__lb_c = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb_c, "center")

        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb_i, "")
        ac.setText(self.__lb_m, "")
        ac.setText(self.__lb_o, "")
        ac.setText(self.__lb_c, "")

    def _zone_xs(self, pad: float, part: float) -> tuple:
        """ Returns (band_left, inner_x, middle_x, outer_x). INNER sits
        on the screen-centre-facing side of the widget; right-side
        widgets are already mirrored at the wheel-info layer, so INNER
        keeps the widget-LEFT column for them. """
        band_left = self._box.rect[0] + pad
        middle_x = band_left + part
        if self.__wheel.is_left():
            return band_left, band_left + 2.0 * part, middle_x, band_left
        return band_left, band_left, middle_x, band_left + 2.0 * part

    def _draw_zone(self, temp: float, x: float, label, rot: tuple) -> None:
        """ One zone column: colored text readout in the TOP bump slot
        (the bump quad is dropped so AC1 doesn't paint over the label),
        solid colored quad in the BOTTOM bump as the visual indicator.
        ``rot = (pivot, trig)``. """
        color = self.__calc.interpolate_color(
            temp, self.__calc.interpolate(temp))
        pivot, trig = rot

        # Bottom bump only — solid coloured bar at the band bottom.
        ac.glColor4f(*color)
        self._emit_rotated_rect(
            (x, self.__top_y + self.__quarter * 7.0,
             self.__part, self.__quarter), pivot, trig)

        # Top bump replaced by the value text itself, coloured in the
        # zone temp colour. AC1's render callback fires *after* UI paint
        # (per `addRenderCallback` docs), so any solid quad we emit lands
        # on top of the labels — dropping the top-bump quad lets the
        # zone readout actually show up.
        ac.setText(label, "{}".format(int(temp)))
        ac.setFontColor(label, *color)

        # Rotate the top-bump centre around the tire pivot. AC1's
        # setPosition anchors the text by its top edge (horizontally
        # centred when align=center), so subtract half the font height
        # to drop the glyph centre onto the rotated bump centre.
        px, py = pivot
        cx = x + self.__part * 0.5
        cy = self.__top_y + self.__quarter * 0.5
        rx, ry = self._rotate((cx - px, cy - py), pivot, trig)
        ac.setPosition(label, rx, ry - self.__zone_font * 0.5)

    def draw(self, data, delta_t: float) -> None:
        rot = self._camber_rotation(data.camber)
        pivot, trig = rot

        # Core block — drawn as four quads that frame the centre column
        # where the core readout sits. AC1 paints labels first and GL
        # quads on top, so a single core quad would hide the centred
        # number; the carve-out is the middle column only (inner +
        # outer columns still carry the core colour across the gap row
        # so the band doesn't read as half-empty).
        core_color = self.__calc.interpolate_color(
            data.tire_t_c, self.__calc.interpolate(data.tire_t_c))
        ac.glColor4f(*core_color)
        band_top = self.__top_y + self.__quarter
        band_w = self.__part * 3.0
        gap_h = self.__core_font * 1.4
        gap_top = self._box.center[1] - gap_h * 0.5
        gap_bot = gap_top + gap_h
        top_h = max(0.0, gap_top - band_top)
        bot_h = max(0.0, (band_top + self.__quarter * 6.0) - gap_bot)
        if top_h > 0.0:
            self._emit_rotated_rect(
                (self.__band_left, band_top, band_w, top_h), pivot, trig)
        if bot_h > 0.0:
            self._emit_rotated_rect(
                (self.__band_left, gap_bot, band_w, bot_h), pivot, trig)
        # Left + right side quads filling the gap row's outer columns.
        gap_row_h = gap_bot - gap_top
        if gap_row_h > 0.0:
            self._emit_rotated_rect(
                (self.__band_left, gap_top, self.__part, gap_row_h),
                pivot, trig)
            self._emit_rotated_rect(
                (self.__band_left + 2.0 * self.__part, gap_top,
                 self.__part, gap_row_h), pivot, trig)

        # Per-zone bumps + text readouts (positions rotated inside _draw_zone).
        self._draw_zone(data.tire_t_i, self.__inner_x, self.__lb_i, rot)
        self._draw_zone(data.tire_t_m, self.__middle_x, self.__lb_m, rot)
        self._draw_zone(data.tire_t_o, self.__outer_x, self.__lb_o, rot)

        # Core readout fits inside the carved gap, coloured in the core
        # temp colour so the magnitude still reads at a glance.
        ac.setText(self.__lb_c, "{} C".format(int(data.tire_t_c)))
        ac.setFontColor(self.__lb_c, *core_color)
        ac.setPosition(self.__lb_c, self._box.center[0],
                       self._box.center[1] - (self.__core_font * 0.5))

    def resize_fonts(self, resolution: str) -> None:
        self.__mult = BoxComponent.resolution_map[resolution]
        self.__zone_font = max(8.0, self._font * 0.85)
        self.__core_font = self._font * 1.4
        for lb in (self.__lb_i, self.__lb_m, self.__lb_o):
            ac.setFontSize(lb, self.__zone_font)
        ac.setFontSize(self.__lb_c, self.__core_font)

        # Re-derive band geometry from the resized box so draw() and the
        # per-frame label positions agree. Padding mirrors the original
        # 12 px inset at mult=1.0.
        pad = 12 * self.__mult
        self.__quarter = (self._box.rect[3] - 2.0 * pad) * 0.125
        self.__part = (self._box.rect[2] - 2.0 * pad) / 3.0
        self.__top_y = self._box.rect[1] + pad
        (self.__band_left, self.__inner_x,
         self.__middle_x, self.__outer_x) = self._zone_xs(pad, self.__part)

        # Seed an initial label position so the first paint (before
        # draw() runs) has something sensible — draw() then refreshes
        # positions per-frame from the camber-rotated bump centres.
        label_y = self.__top_y + (self.__quarter - self.__zone_font) * 0.5
        half_part = self.__part * 0.5
        ac.setPosition(self.__lb_i, self.__inner_x + half_part, label_y)
        ac.setPosition(self.__lb_m, self.__middle_x + half_part, label_y)
        ac.setPosition(self.__lb_o, self.__outer_x + half_part, label_y)
        ac.setPosition(self.__lb_c, self._box.center[0],
                       self._box.center[1] - (self.__core_font * 0.5))


# Tire-shape geometry + tire-load circle constants (match evo).
_TIRE_CHAMFER = 0.08
_TIRE_CORNER_SEGMENTS = 5
_TIRE_CAMBER_AMPLIFY = 2.0
# Tread-cut slots — 4 transparent rectangles in tire.png (2 top,
# 2 bottom) that read as tire marks. Values measured off the PNG.
_TIRE_CUT_X_INNER = 0.400   # cut inner edge, fraction of half_w from centre
_TIRE_CUT_X_OUTER = 0.426   # cut outer edge, fraction of half_w
_TIRE_CUT_DEPTH = 0.0625    # cut depth, fraction of half_h
_LOAD_PX_PER_N = 0.027
_LOAD_DIAMETER_MAX_LOGICAL = 160.0
_LOAD_HIDE_BELOW = 1.0


class Tire(BoxComponent):
    """ Hollow tire silhouette matching tire.svg — rounded-rect frame
    around the IMO band with tread cuts on top/bottom. Rotates with
    camber around the shared tire pivot. """

    def __init__(self, acd: ACD, resolution: str, wheel):
        self.__calc = TireTemp(acd.get_temp_curve(
            ac.getCarTyreCompound(0), wheel))
        # 160x256 — Temps/Dirt/Load coords depend on this footprint.
        super().__init__(176.0, 0.0, 160.0, 256.0)
        self._back.color = Colors.white
        self.resize(resolution)

    def draw(self, data, delta_t: float) -> None:
        """ Draws the tire. """
        temp = data.tire_t_c * 0.75 + \
            ((data.tire_t_i + data.tire_t_m + data.tire_t_o) / 3.0) * 0.25
        color = self.__calc.interpolate_color(
            temp, self.__calc.interpolate(temp))
        ac.glColor4f(*color)
        pivot, trig = self._camber_rotation(data.camber)
        self._draw_body(pivot, trig)

    def _draw_body(self, pivot: tuple, trig: tuple) -> None:
        """ Side + tread-cut top/bottom strips + corner fans. """
        rect = self._box.rect
        half_w = rect[2] * 0.5
        half_h = rect[3] * 0.5
        chamfer = rect[2] * _TIRE_CHAMFER
        inner_w = half_w - chamfer
        inner_h = half_h - chamfer
        geom = (half_w, half_h, inner_w, inner_h)

        for strip in self._side_strips(geom):
            self._emit_rotated_quad(strip, pivot, trig)
        for strip in self._top_bottom_strips(geom):
            self._emit_rotated_quad(strip, pivot, trig)
        self._draw_corner_fans(inner_w, inner_h, chamfer, pivot, trig)

    @staticmethod
    def _side_strips(geom: tuple) -> tuple:
        """ Left + right edge strips (no cuts). """
        half_w, _half_h, inner_w, inner_h = geom
        return (
            ((-half_w, -inner_h), (-inner_w, -inner_h),   # LEFT
             (-inner_w, inner_h), (-half_w, inner_h)),
            ((inner_w, -inner_h), (half_w, -inner_h),     # RIGHT
             (half_w, inner_h),   (inner_w, inner_h)),
        )

    @staticmethod
    def _top_bottom_strips(geom: tuple) -> tuple:
        """ Top + bottom strips, each split by two tread cuts into
        one inner full-width band plus three outer segments. """
        half_w, half_h, inner_w, inner_h = geom
        cut_d = half_h * _TIRE_CUT_DEPTH
        cut_in = half_w * _TIRE_CUT_X_INNER
        cut_out = half_w * _TIRE_CUT_X_OUTER
        top_cut = -half_h + cut_d
        bot_cut = half_h - cut_d
        return (
            # TOP inner band (touches IMO band, no cuts).
            ((-inner_w, top_cut), (inner_w, top_cut),
             (inner_w, -inner_h), (-inner_w, -inner_h)),
            # TOP outer segments — left, middle (between cuts), right.
            ((-inner_w, -half_h), (-cut_out, -half_h),
             (-cut_out, top_cut), (-inner_w, top_cut)),
            ((-cut_in, -half_h),  (cut_in, -half_h),
             (cut_in, top_cut),   (-cut_in, top_cut)),
            ((cut_out, -half_h),  (inner_w, -half_h),
             (inner_w, top_cut),  (cut_out, top_cut)),
            # BOTTOM inner band + 3 outer segments (mirror of top).
            ((-inner_w, inner_h), (inner_w, inner_h),
             (inner_w, bot_cut),  (-inner_w, bot_cut)),
            ((-inner_w, bot_cut), (-cut_out, bot_cut),
             (-cut_out, half_h),  (-inner_w, half_h)),
            ((-cut_in, bot_cut),  (cut_in, bot_cut),
             (cut_in, half_h),    (-cut_in, half_h)),
            ((cut_out, bot_cut),  (inner_w, bot_cut),
             (inner_w, half_h),   (cut_out, half_h)),
        )

    def _draw_corner_fans(self, inner_w: float, inner_h: float,  # pylint: disable=too-many-arguments,too-many-positional-arguments
                          radius: float, pivot: tuple, trig: tuple) -> None:
        """ Four quarter-circle fans rounding the outer corners. """
        step = (math.pi * 0.5) / _TIRE_CORNER_SEGMENTS
        specs = (
            (-inner_w, -inner_h, math.pi,        radius, step),  # TL
            (inner_w,  -inner_h, math.pi * 1.5,  radius, step),  # TR
            (inner_w,   inner_h, 0.0,            radius, step),  # BR
            (-inner_w,  inner_h, math.pi * 0.5,  radius, step),  # BL
        )
        for spec in specs:
            self._emit_corner_fan(spec, pivot, trig)

    def _emit_corner_fan(self, spec: tuple, pivot: tuple, trig: tuple) -> None:
        """ ``_TIRE_CORNER_SEGMENTS`` fan triangles for one rounded
        corner. ``spec = (fx, fy, t_start, radius, step)``. Each
        triangle is a degenerate quad (last vertex repeated). """
        fx, fy, t_start, radius, step = spec
        for i in range(_TIRE_CORNER_SEGMENTS):
            t1 = t_start + step * i
            t2 = t1 + step
            offsets = (
                (fx, fy),
                (fx + radius * math.cos(t1), fy + radius * math.sin(t1)),
                (fx + radius * math.cos(t2), fy + radius * math.sin(t2)),
                (fx + radius * math.cos(t2), fy + radius * math.sin(t2)),
            )
            self._emit_rotated_quad(offsets, pivot, trig)


class Wear(BoxComponent):
    """ Horizontal tire-wear bar (ported from live-telemetry-ac-evo).

    A centred "Tire Wear" caption above a left→right fill bar (full =
    fresh) — colour bands switch green / yellow / red as the tyre
    degrades. Sits in the brake column between the lock icon (y=0-60)
    and the pressure icon (y=171), sharing their 60 px width so the
    column reads as a single vertical stack.

    AC1's ``tyreWear`` stays in the ``[0.94, 1.0]`` window for a
    typical session, so the bar stretches that window across its full
    width — the raw 0..1 value would barely move. Colour thresholds
    keep the legacy plugin's behaviour: >0.98 green, >0.96 yellow.
    """

    def __init__(self, resolution: str, wheel, window_id: int):
        # 60 wide × 32 tall: title row (12) + 8 px gap + bar (12).
        # Centred vertically between the lock icon (ends y=60) and the
        # pressure icon (starts y=171) — midpoint y=115.5, top y=100.
        super().__init__(
            70.0 if wheel.is_left() else 382.0, 100.0, 60.0, 32.0, font=12.0)
        self._back.color = Colors.black
        self._back.border = Colors.white
        self._back.size = 1.5

        self.__lb = ac.addLabel(window_id, "Tire Wear")
        ac.setFontAlignment(self.__lb, "center")

        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb, "")

    def draw(self, data, delta_t: float) -> None:
        ac.setText(self.__lb, "Tire Wear")
        ac.setFontColor(self.__lb, *Colors.white)

        # Stretch the AC1 [0.94, 1.0] useful range across the bar so
        # the fill actually moves during a session.
        wear = data.tire_w
        ratio = max(0.0, min(1.0, (wear - 0.94) / 0.06))
        if ratio > 0.5:
            color = Colors.green
        elif ratio > 0.2:
            color = Colors.yellow
        else:
            color = Colors.red

        # Bar outline + black fill below the title row.
        title_h = 12.0 * self._mult
        gap = 8.0 * self._mult
        bar_h = 12.0 * self._mult
        bar_x = self._box.rect[0]
        bar_y = self._box.rect[1] + title_h + gap
        bar_w = self._box.rect[2]
        self._back.draw([bar_x, bar_y, bar_w, bar_h])

        # Coloured fill inside the border (left→right, full = fresh).
        pad = 1.5 * self._mult
        inner_w = (bar_w - 2.0 * pad) * ratio
        if inner_w > 0.0:
            ac.glColor4f(*color)
            ac.glQuad(bar_x + pad, bar_y + pad, inner_w, bar_h - 2.0 * pad)

    def resize_fonts(self, resolution: str) -> None:
        ac.setFontSize(self.__lb, self._font)
        ac.setPosition(
            self.__lb, self._box.center[0], self._box.rect[1])


class WheelTitle(BoxComponent):
    """ Wheel ID + tyre compound abbreviation stacked at the top of
    the inboard column, lined up with the height widget's x. Replaces
    the old ``Compound`` placement above the tire silhouette, which
    AC1's GL render order pushed under the tire's top frame quad
    (the render callback paints primitives *after* UI labels, so
    anything on top of a solid quad disappears).

    Compound is published per-frame by AC's graphics block via
    ``ac.getCarTyreCompound(0)``; we cache it on the component and
    only re-read when the string changes (pit-stop tyre swaps
    re-publish).
    """

    def __init__(self, resolution: str, wheel, window_id: int):
        # Same x as the height widget so the wheel ID + compound and
        # the ride-height readout share a column. 64×40 leaves room
        # for the ID row (font 20) + compound row (font 14) with a
        # small gap, and sits well above the height widget at y=208.
        super().__init__(
            448.0 if wheel.is_left() else 0.0, 4.0, 64.0, 40.0, font=20.0)
        self.__wheel = wheel
        self.__lb_id = ac.addLabel(window_id, wheel.name())
        ac.setFontAlignment(self.__lb_id, "center")
        self.__lb_compound = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb_compound, "center")
        self.__last_compound = ""
        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb_id, "")
        ac.setText(self.__lb_compound, "")

    def draw(self, data, delta_t: float) -> None:
        ac.setText(self.__lb_id, self.__wheel.name())
        ac.setFontColor(self.__lb_id, *Colors.white)

        try:
            compound = ac.getCarTyreCompound(0) or ""
        except (TypeError, ValueError):
            compound = ""
        if compound != self.__last_compound:
            self.__last_compound = compound
            ac.setText(self.__lb_compound,
                       compound[:3].upper() if compound else "")
        ac.setFontColor(self.__lb_compound, *Colors.white)

    def resize_fonts(self, resolution: str) -> None:
        m = self._mult
        id_font = self._font            # 20 logical
        compound_font = self._font * 0.7  # ~14 logical
        ac.setFontSize(self.__lb_id, id_font)
        ac.setFontSize(self.__lb_compound, compound_font)
        ac.setPosition(
            self.__lb_id, self._box.center[0], self._box.rect[1])
        ac.setPosition(
            self.__lb_compound, self._box.center[0],
            self._box.rect[1] + id_font + 2.0 * m)


# Engine widget chip / readout positions. The engine widget grew from
# 85 to 120 logical pixels tall to fit a chip row + analog readouts
# row below the existing RPM bar + label band.
_ENGINE_CHIPS_Y = 75.0
_ENGINE_CHIPS_H = 18.0
_ENGINE_READOUTS_Y = 96.0
_ENGINE_READOUTS_H = 20.0


class EngineChips(BoxComponent):
    """ Driver-aid chips strip below the RPM bar (PIT / TC / ABS /
    DRS / ERS — AC1's subset of evo's Phase 1 set). Text-only because
    AC1's GL doesn't support tinted PNG sprites. """

    def __init__(self, resolution: str, window_id: int):
        super().__init__(0.0, _ENGINE_CHIPS_Y, 512.0, _ENGINE_CHIPS_H, font=12.0)
        self.__mult = BoxComponent.resolution_map[resolution]
        # 6 label slots; populated cells centred, the rest blanked.
        self.__labels = [ac.addLabel(window_id, "") for _ in range(6)]
        for lb in self.__labels:
            ac.setFontAlignment(lb, "center")
        self.resize(resolution)

    def clear(self) -> None:
        for lb in self.__labels:
            ac.setText(lb, "")

    def draw(self, data, delta_t: float) -> None:
        chips = []
        if data.pit_limiter:
            chips.append(("PIT", Colors.yellow))
        if data.tc_level > 0.0:
            chips.append(("TC", Colors.green))
        if data.abs_level > 0.0:
            chips.append(("ABS", Colors.blue))
        if data.drs_available:
            # Bright blue when actually deployed; dim white otherwise.
            chips.append(("DRS", Colors.blue if data.drs_enabled else Colors.white))
        if data.ers_charging:
            chips.append(("ERS", Colors.yellow))

        # Lay out only the populated chips centred across the strip; blank
        # the rest. Cell width adapts so a single chip doesn't stretch
        # the whole bar.
        rect = self._box.rect
        cell_w = min(64.0 * self.__mult, rect[2] / max(1, len(chips))) if chips else 0.0
        total_w = cell_w * len(chips)
        x_start = rect[0] + (rect[2] - total_w) * 0.5
        y_center = rect[1] + rect[3] * 0.5 - self._font * 0.5

        for idx, lb in enumerate(self.__labels):
            if idx < len(chips):
                label, color = chips[idx]
                ac.setText(lb, label)
                ac.setFontColor(lb, *color)
                ac.setPosition(lb, x_start + cell_w * (idx + 0.5), y_center)
            else:
                ac.setText(lb, "")

    def resize_fonts(self, resolution: str) -> None:
        self.__mult = BoxComponent.resolution_map[resolution]
        for lb in self.__labels:
            ac.setFontSize(lb, self._font)


class EngineReadouts(BoxComponent):
    """ Analog engine readouts strip — fuel + brake bias.

    Phase 2 evo (engine_view.py:_draw_readouts) had eight readout slots;
    AC1's shared memory only publishes two of them (fuel and brake bias),
    so we render those two centred. Water/oil temp, oil/fuel pressure,
    exhaust temp, battery voltage aren't in AC1's physics struct and
    are omitted entirely rather than rendered as fake zeros.
    """

    def __init__(self, resolution: str, window_id: int):
        super().__init__(0.0, _ENGINE_READOUTS_Y, 512.0, _ENGINE_READOUTS_H, font=12.0)
        self.__lb_fuel = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb_fuel, "center")
        self.__lb_bbias = ac.addLabel(window_id, "")
        ac.setFontAlignment(self.__lb_bbias, "center")
        self.resize(resolution)

    def clear(self) -> None:
        ac.setText(self.__lb_fuel, "")
        ac.setText(self.__lb_bbias, "")

    def draw(self, data, delta_t: float) -> None:
        rect = self._box.rect
        y_center = rect[1] + rect[3] * 0.5 - self._font * 0.5

        # Two cells centred on the strip — left = fuel, right = brake
        # bias. The "%F" suffix on brake bias mirrors the evo widget so
        # the polarity (front-biased = higher number) is unambiguous.
        cell_w = rect[2] * 0.5
        ac.setText(self.__lb_fuel, "FUEL {:.1f} L".format(max(0.0, data.fuel)))
        ac.setFontColor(self.__lb_fuel, *Colors.white)
        ac.setPosition(self.__lb_fuel, rect[0] + cell_w * 0.5, y_center)

        if data.brake_bias > 0.0:
            ac.setText(self.__lb_bbias,
                       "BBIAS {}%F".format(int(round(data.brake_bias * 100))))
            ac.setFontColor(self.__lb_bbias, *Colors.white)
            ac.setPosition(self.__lb_bbias, rect[0] + cell_w * 1.5, y_center)
        else:
            ac.setText(self.__lb_bbias, "")

    def resize_fonts(self, resolution: str) -> None:
        for lb in (self.__lb_fuel, self.__lb_bbias):
            ac.setFontSize(lb, self._font)
