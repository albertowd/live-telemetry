#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to load and save app options.

@author: albertowd
"""

from configparser import ConfigParser, Error as ConfigError
from math import floor
from os import path
from sys import exc_info

from lib.lt_util import get_docs_path, log


# Options window dimensions — a fixed AC dialog that does not scale,
# used only to position the default OP anchor along the screen edge.
_OPTIONS_WH = (395, 195)

# Local copy of BoxComponent.resolution_map so config layout math
# doesn't have to import lt_components (which pulls in `ac`/`acsys`).
_SIZE_MULT = {"HD": 0.5, "FHD": 0.75, "1440p": 1.0, "UHD": 1.5,
              "4K": 1.6, "8K": 3.0}

# Persisted window positions are stored in anchor-space: the (x, y)
# pair represents the listed corner of the widget on screen so that a
# resolution change scales the widget without dragging it off-screen.
# AC's ac.setPosition still expects top-left coords, so callers convert
# via ``anchor_to_top_left`` / ``top_left_to_anchor`` below.
_ANCHOR_BY_WINDOW = {
    "EN": "BC", "FL": "TL", "FR": "TR", "OP": "TL",
    "RL": "BL", "RR": "BR",
}


def anchor_for(name: str) -> str:
    """ Returns the persisted anchor convention for a window name. """
    return _ANCHOR_BY_WINDOW.get(name, "TL")


def anchor_to_top_left(anchor: str, anchor_x: int, anchor_y: int,
                       width: int, height: int) -> [int]:
    """ Converts an anchor-space (x, y) to AC's top-left coords. """
    if anchor == "TR":
        return [int(anchor_x - width), int(anchor_y)]
    if anchor == "BL":
        return [int(anchor_x), int(anchor_y - height)]
    if anchor == "BR":
        return [int(anchor_x - width), int(anchor_y - height)]
    if anchor == "BC":
        return [int(anchor_x - width / 2), int(anchor_y - height)]
    return [int(anchor_x), int(anchor_y)]


def top_left_to_anchor(anchor: str, tl_x: int, tl_y: int,
                       width: int, height: int) -> [int]:
    """ Inverse of ``anchor_to_top_left``; converts AC's reported TL
    back into the persisted anchor-space coords. """
    if anchor == "TR":
        return [int(tl_x + width), int(tl_y)]
    if anchor == "BL":
        return [int(tl_x), int(tl_y + height)]
    if anchor == "BR":
        return [int(tl_x + width), int(tl_y + height)]
    if anchor == "BC":
        return [int(tl_x + width / 2), int(tl_y + height)]
    return [int(tl_x), int(tl_y)]


class Config:
    """ Singleton to handle configuration methods. """

    def __init__(self, lt_version: str) -> None:
        """ Loads or creates the app configuration file. """

        self.__base_path = path.join(path.dirname(path.realpath(__file__)), "..", "cfg")
        settings_path = path.join(self.__base_path, "conf.ini")

        self.__configs = ConfigParser(allow_no_value=True, comment_prefixes=(";","#","/","_"), empty_lines_in_values=False, inline_comment_prefixes=(";","#","/","_"), strict=False)
        if path.isfile(settings_path):
            self.__configs.read(settings_path)
        else:
            log("Settings file not found. Using default values instead!")

        # If the config does not have it's version or is invalid, create a new one.
        try:
            config_version = self.get_version()
            if config_version != lt_version:
                log("Version missmatch. Using default values instead!")
                raise ValueError("Old config file.")
        except (ConfigError, KeyError, ValueError):
            log("Creating new config file.")
            self.__create_default_config(lt_version)
            self.save_config()

        # Coerce a stale Size preset (e.g. 480p, which was dropped) to a
        # supported one so downstream resolution_map[size] lookups don't
        # KeyError on first launch after the sub-720p presets were removed.
        if self.__configs.has_option("Options", "Size"):
            current_size = self.__get_str("Options", "Size")
            if current_size not in _SIZE_MULT:
                log("Unsupported Size '{}', falling back to FHD.".format(current_size))
                self.set_option("Size", "FHD")
                self.save_config()

    def __create_default_config(self, lt_version: str) -> None:
        """ Initializes the in-memory config with default sections and values. """
        self.__configs["About"] = {"Version": lt_version}
        self.__configs["Options"] = {}
        self.__configs["Windows"] = {}
        self.__configs["Windows Positions"] = {}

        self.__load_documented_defaults()
        height, width = self.__read_screen_resolution()
        self.__set_default_window_positions(height, width)

    def __load_documented_defaults(self) -> None:
        """ Copies [Options] and [Windows] from settings_defaults.ini.

        settings_defaults.ini is the single source of truth for documented
        defaults so the runtime cannot drift from the docs. [Windows
        Positions] is computed from screen resolution instead.
        """
        defaults_path = path.join(self.__base_path, "settings_defaults.ini")
        defaults = ConfigParser(allow_no_value=True, comment_prefixes=(";","#","/","_"), empty_lines_in_values=False, inline_comment_prefixes=(";","#","/","_"), strict=False)
        defaults.read(defaults_path)
        for section in ("Options", "Windows"):
            if defaults.has_section(section):
                for name, value in defaults.items(section):
                    # ConfigParser keeps inline-comment-stripped values
                    # with trailing whitespace; strip so "True " becomes
                    # "True" and get_bool_option compares correctly.
                    self.__set_str(section, name, value.strip())

    @staticmethod
    def __read_screen_resolution() -> (int, int):
        """ Reads (height, width) from AC's video.ini, falling back to 1080x1920. """
        height = 1080
        width = 1920
        docs_path = get_docs_path()
        if len(docs_path) > 0:
            try:
                video = ConfigParser()
                video.read("{}/Assetto Corsa/cfg/video.ini".format(docs_path))
                height = int(video.get("VIDEO", "HEIGHT")) if video.has_option(
                    "VIDEO", "HEIGHT") else height
                width = int(video.get("VIDEO", "WIDTH")) if video.has_option(
                    "VIDEO", "WIDTH") else width
            except (ConfigError, OSError, ValueError):
                log("Could not get 'cfg/video.ini' video options, using default 1280x720 resolution:")
                for info in exc_info():
                    log(info)
        return height, width

    def reset_window_positions(self) -> None:
        """ Recomputes the default anchor positions for the current
        screen resolution and persists them. Fired by the options
        window's Reset button to send widgets back to their default
        screen edge without forcing a config wipe. """
        height, width = self.__read_screen_resolution()
        self.__set_default_window_positions(height, width)
        self.save_config()

    def __set_default_window_positions(self, height: int, width: int) -> None:
        """ Writes the default window positions for the given screen size.

        Positions are stored in anchor-space (see ``_ANCHOR_BY_WINDOW``):
        each widget pins to its assigned screen corner / edge so that
        cycling Size keeps it on-screen without recomputing offsets.
        """
        op_w, op_h = _OPTIONS_WH

        edge = 10
        pad = 80

        self.set_window_position("EN", [floor(width / 2), height - pad])
        self.set_window_position("FL", [edge, pad])
        self.set_window_position("FR", [width - edge, pad])
        self.set_window_position("OP", [width - op_w - 50, floor((height - op_h) / 2)])
        self.set_window_position("RL", [edge, height - pad])
        self.set_window_position("RR", [width - edge, height - pad])

    def __get_str(self, section: str, option: str) -> str:
        """ Returns an option. """
        return self.__configs.get(section, option)

    def __set_str(self, section: str, option: str, value) -> None:
        """ Updates an option. """
        self.__configs.set(section, option, str(value))

    def get_bool_option(self, name: str) -> bool:
        """ Returns a option value as a boolean. """
        return self.__get_str("Options", name) == "True"

    def get_option(self, name: str) -> str:
        """ Returns a option value as a string. """
        return self.__get_str("Options", name)

    def get_version(self) -> str:
        """ Returns the config file version. """
        return self.__get_str("About", "version")

    def get_window_position(self, name: str) -> [int]:
        """ Returns the position [x,y] of a window. """
        return [
            int(self.__get_str("Windows Positions", "{}_x".format(name))),
            int(self.__get_str("Windows Positions", "{}_y".format(name)))
        ]

    def is_window_active(self, name: str) -> bool:
        """ Returns if a window is active. """
        return self.__get_str("Windows", name) == "True"

    def save_config(self) -> None:
        """ Writes the actual options on the configuration file. """
        with open(path.join(self.__base_path, "conf.ini"), "w", encoding="utf-8") as cfg_file:
            self.__configs.write(cfg_file)

    def set_option(self, name: str, value) -> None:
        """ Updates an option value. """
        self.__set_str("Options", name, str(value))

    def set_window_active(self, name: str, active: bool) -> None:
        """ Updates if a window is active. """
        self.__set_str("Windows", name, str(active))

    def set_window_position(self, name: str, position: [int]) -> None:
        """ Updates a window position. """
        self.__set_str("Windows Positions",
                       "{}_x".format(name), str(int(position[0])))
        self.__set_str("Windows Positions",
                       "{}_y".format(name), str(int(position[1])))
