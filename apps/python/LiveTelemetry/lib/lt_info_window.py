#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base class for telemetry info windows (engine, wheel).
Owns the AC window handle and the shared component/draw plumbing.

@author: albertowd
"""
import ac

from lib.lt_colors import Colors
from lib.lt_config import anchor_to_top_left, top_left_to_anchor


class InfoWindow:
    """ Shared window plumbing for telemetry info displays. """

    def __init__(self, title: str):
        self._active = False
        self._anchor = "TL"
        self._components = []
        self._data = None
        self._data_log = []
        self._options = {}
        self._widget_w = 0
        self._widget_h = 0
        self._window_id = ac.newApp(title)
        ac.drawBorder(self._window_id, 0)
        ac.setBackgroundOpacity(self._window_id, 0.0)
        ac.setIconPosition(self._window_id, 0, -10000)
        ac.setTitle(self._window_id, "")

    def _apply_initial_geometry(self, configs, name: str, width: int, height: int) -> None:
        """ Sets the window size and positions it from the persisted
        anchor-space coords. Call once at construction. """
        ac.setSize(self._window_id, width, height)
        anchor_pos = configs.get_window_position(name)
        tl_x, tl_y = anchor_to_top_left(
            self._anchor, anchor_pos[0], anchor_pos[1], width, height)
        ac.setPosition(self._window_id, tl_x, tl_y)
        self._widget_w = width
        self._widget_h = height

    def _resize_window(self, new_w: int, new_h: int) -> None:
        """ Resizes the window in-place, keeping the anchor pinned so
        the widget doesn't drift off-screen on a Size cycle. """
        cur_tl = ac.getPosition(self._window_id)
        anchor_pos = top_left_to_anchor(
            self._anchor, cur_tl[0], cur_tl[1],
            self._widget_w, self._widget_h)
        ac.setSize(self._window_id, new_w, new_h)
        new_tl = anchor_to_top_left(
            self._anchor, anchor_pos[0], anchor_pos[1], new_w, new_h)
        ac.setPosition(self._window_id, new_tl[0], new_tl[1])
        self._widget_w = new_w
        self._widget_h = new_h

    def get_anchor_position(self):
        """ Returns the current window position in anchor-space coords
        so it can be persisted back to the config. """
        cur_tl = ac.getPosition(self._window_id)
        return top_left_to_anchor(
            self._anchor, cur_tl[0], cur_tl[1],
            self._widget_w, self._widget_h)

    def reset_position(self, configs, name: str) -> None:
        """ Repositions the window using the persisted anchor coords
        and the current widget size — used by the Reset action to
        send the widget back to its default screen edge. """
        anchor_pos = configs.get_window_position(name)
        tl_x, tl_y = anchor_to_top_left(
            self._anchor, anchor_pos[0], anchor_pos[1],
            self._widget_w, self._widget_h)
        ac.setPosition(self._window_id, tl_x, tl_y)

    def get_data_log(self):
        """ Returns the saved data from the session. """
        return self._data_log

    def get_option(self, name):
        """ Returns an option value. """
        return self._options[name]

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self._window_id)

    def get_window_id(self):
        """ Returns the window id. """
        return self._window_id

    def has_data_logged(self) -> bool:
        """ Returns if the info has data logged. """
        return len(self._data_log) > 0

    def is_active(self) -> bool:
        """ Returns window status. """
        return self._active

    def set_active(self, active) -> None:
        """ Toggles the window status. """
        self._active = active

    def set_option(self, name, value) -> None:
        """ Updates an option value. """
        self._options[name] = value

    def draw(self, delta_t: float) -> None:
        """ Draws all enabled components on screen. """
        ac.setBackgroundOpacity(self._window_id, 0.0)
        for component in self._components:
            # `.get(..., True)` so always-on components added in 1.8.0
            # (Compound, EngineChips, EngineReadouts) render without
            # needing a new persisted option key. Existing toggleable
            # components are still keyed on their class name and look
            # up the user-set bool the same way as before. Tri-state
            # options (BatteryBar's AUTO/ON/OFF) only need the "OFF"
            # literal handled here — both AUTO and ON should render the
            # component and let the component decide visibility itself.
            opt = self._options.get(type(component).__name__, True)
            disabled = opt is False or opt == "OFF"
            if not disabled:
                ac.glColor4f(*Colors.white)
                component.draw(self._data, delta_t)
            else:
                component.clear()
        ac.glColor4f(*Colors.white)
