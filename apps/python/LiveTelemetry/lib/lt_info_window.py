#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base class for telemetry info windows (engine, wheel).
Owns the AC window handle and the shared component/draw plumbing.

@author: albertowd
"""
import ac

from lib.lt_colors import Colors


class InfoWindow:
    """ Shared window plumbing for telemetry info displays. """

    def __init__(self, title: str):
        self._active = False
        self._components = []
        self._data = None
        self._data_log = []
        self._options = {}
        self._window_id = ac.newApp(title)
        ac.drawBorder(self._window_id, 0)
        ac.setBackgroundOpacity(self._window_id, 0.0)
        ac.setIconPosition(self._window_id, 0, -10000)
        ac.setTitle(self._window_id, "")

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
            # up the user-set bool the same way as before.
            if self._options.get(type(component).__name__, True) is True:
                ac.glColor4f(*Colors.white)
                component.draw(self._data, delta_t)
            else:
                component.clear()
        ac.glColor4f(*Colors.white)
