#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Live Telemetry App for Assetto Corsa
v 1.7.0
https://github.com/albertowd/Wheellive-telemetry
@author: albertowd
"""


import a_ctypes_aux # pylint: disable=unused-import

import ac

from lib.lt_acd import ACD
from lib.lt_components import BoxComponent
from lib.lt_config import Config
from lib.lt_engine_info import EngineInfo
from lib.lt_options_info import OptionsInfo
from lib.lt_wheel_info import WheelInfo
from lib.lt_util import clear_logs, export_saved_log, log

# APP VERSION
LT_VERSION = "1.7.0"

# Loaded car files
LT_ACD_OBJ = None

# Global configurations
LT_CONFIGS = None

# Each window
LT_ENGINE_INFO = None
LT_OPTIONS_INFO = None
LT_WHEEL_INFOS = {}


def acMain(ac_version: str) -> None:
    """ Initiates the program. """
    global LT_ACD_OBJ
    global LT_CONFIGS
    global LT_ENGINE_INFO
    global LT_OPTIONS_INFO

    log("Starting Live Telemetry {} on AC Python API version {}...".format(
        LT_VERSION, ac_version))

    log("Loading configs...")
    LT_CONFIGS = Config(LT_VERSION)

    log("Loading {} info...".format(ac.getCarName(0)))
    LT_ACD_OBJ = ACD("content/cars/{}".format(ac.getCarName(0)))
    log("Loaded correctly")

    log("Loading options window...")
    LT_OPTIONS_INFO = OptionsInfo(LT_CONFIGS)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("BoostBar"), on_click_boost)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Camber"), on_click_camber)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Dirt"), on_click_dirt)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Height"), on_click_height)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Load"), on_click_load)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Lock"), on_click_lock)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Logging"), on_click_logging)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Pressure"), on_click_pressure)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("RPMPower"), on_click_rpm)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Size"), on_click_size)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Suspension"), on_click_suspension)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Temps"), on_click_temps)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Tire"), on_click_tire)
    ac.addOnClickedListener(LT_OPTIONS_INFO.get_button_id("Wear"), on_click_wear)

    log("Loading engine window...")
    LT_ENGINE_INFO = EngineInfo(LT_ACD_OBJ, LT_CONFIGS)
    window_id = LT_ENGINE_INFO.get_window_id()
    ac.addOnAppActivatedListener(window_id, on_activation)
    ac.addOnAppDismissedListener(window_id, on_dismiss)
    ac.addRenderCallback(LT_ENGINE_INFO.get_window_id(), on_render_engine)

    log("Loading wheel windows...")
    for index in range(4):
        info = WheelInfo(LT_ACD_OBJ, LT_CONFIGS, index)
        window_id = info.get_window_id()
        ac.addOnAppActivatedListener(window_id, on_activation)
        ac.addOnAppDismissedListener(window_id, on_dismiss)
        LT_WHEEL_INFOS[info.get_id()] = info

    ac.addRenderCallback(LT_WHEEL_INFOS["FL"].get_window_id(), on_render_fl)
    ac.addRenderCallback(LT_WHEEL_INFOS["FR"].get_window_id(), on_render_fr)
    ac.addRenderCallback(LT_WHEEL_INFOS["RL"].get_window_id(), on_render_rl)
    ac.addRenderCallback(LT_WHEEL_INFOS["RR"].get_window_id(), on_render_rr)

    log("Live Telemetry started.")

    return "Live Telemetry"


def acShutdown() -> None:
    """ Called when the session ends (or restarts). """
    log("Shutting down Live Telemetry...")

    global LT_ACD_OBJ
    global LT_CONFIGS
    global LT_ENGINE_INFO
    global LT_OPTIONS_INFO
    global LT_WHEEL_INFOS

    log("Saving options configurations...")
    LT_CONFIGS.set_option("Camber", LT_OPTIONS_INFO.get_option("Camber"))
    LT_CONFIGS.set_option("Dirt", LT_OPTIONS_INFO.get_option("Dirt"))
    LT_CONFIGS.set_option("Height", LT_OPTIONS_INFO.get_option("Height"))
    LT_CONFIGS.set_option("Load", LT_OPTIONS_INFO.get_option("Load"))
    LT_CONFIGS.set_option("Lock", LT_OPTIONS_INFO.get_option("Lock"))
    LT_CONFIGS.set_option("Logging", LT_OPTIONS_INFO.get_option("Logging"))
    LT_CONFIGS.set_option("Pressure", LT_OPTIONS_INFO.get_option("Pressure"))
    LT_CONFIGS.set_option("RPMPower", LT_OPTIONS_INFO.get_option("RPMPower"))
    LT_CONFIGS.set_option("Size", LT_OPTIONS_INFO.get_option("Size"))
    LT_CONFIGS.set_option("Suspension", LT_OPTIONS_INFO.get_option("Suspension"))
    LT_CONFIGS.set_option("Temps", LT_OPTIONS_INFO.get_option("Temps"))
    LT_CONFIGS.set_option("Tire", LT_OPTIONS_INFO.get_option("Tire"))
    LT_CONFIGS.set_option("Wear", LT_OPTIONS_INFO.get_option("Wear"))

    log("Saving windows configurations...")
    LT_CONFIGS.set_window_active("EN", LT_ENGINE_INFO.is_active())
    LT_CONFIGS.set_window_position("EN", LT_ENGINE_INFO.get_position())
    LT_ENGINE_INFO.set_active(False)
    LT_CONFIGS.set_window_position("OP", LT_OPTIONS_INFO.get_position())
    for wheel_id in LT_WHEEL_INFOS:
        info = LT_WHEEL_INFOS[wheel_id]
        LT_CONFIGS.set_window_active(wheel_id, info.is_active())
        LT_CONFIGS.set_window_position(wheel_id, info.get_position())
        info.set_active(False)

    LT_CONFIGS.save_config()

    if (
        LT_ENGINE_INFO.has_data_logged()
        or LT_WHEEL_INFOS["FL"].has_data_logged() or LT_WHEEL_INFOS["FL"].has_data_logged()
        or LT_WHEEL_INFOS["RL"].has_data_logged() or LT_WHEEL_INFOS["RR"].has_data_logged()
    ):
        log("Saving csv data...")
        for wheel_id in LT_WHEEL_INFOS:
            info = LT_WHEEL_INFOS[wheel_id]
            export_saved_log(info.get_data_log(), wheel_id)
        export_saved_log(LT_ENGINE_INFO.get_data_log(), "EN")
    else:
        log("Deleting old csv data...")
        clear_logs()

    LT_ACD_OBJ = None
    LT_CONFIGS = None
    LT_ENGINE_INFO = None
    LT_OPTIONS_INFO = None
    LT_WHEEL_INFOS = {}
    log("Live Telemetry ended.")


def acUpdate(delta_t: float) -> None:
    """ Called every physics update. """
    if LT_ENGINE_INFO.is_active():
        LT_ENGINE_INFO.update(delta_t)

    for wheel_id in LT_WHEEL_INFOS:
        info = LT_WHEEL_INFOS[wheel_id]
        if info.is_active():
            info.update(delta_t)


def on_activation(window_id: int) -> None:
    """ Activates a window. """
    if LT_ENGINE_INFO.get_window_id() is window_id:
        LT_ENGINE_INFO.set_active(True)

    for wheel_id in LT_WHEEL_INFOS:
        info = LT_WHEEL_INFOS[wheel_id]
        if info.get_window_id() is window_id:
            info.set_active(True)


def on_click_boost(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options boost bar button. """
    toggle_option("BoostBar")


def on_click_camber(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options camber button. """
    toggle_option("Camber")


def on_click_dirt(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options dirt button. """
    toggle_option("Dirt")


def on_click_height(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options height button. """
    toggle_option("Height")


def on_click_load(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options load button. """
    toggle_option("Load")


def on_click_lock(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options load button. """
    toggle_option("Lock")


def on_click_logging(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options logging button. """
    toggle_option("Logging")


def on_click_pressure(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options pressure button. """
    toggle_option("Pressure")


def on_click_rpm(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options rpm button. """
    toggle_option("RPMPower")


def on_click_size(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options size button. """
    old_resolution = LT_OPTIONS_INFO.get_option("Size")
    new_resolution = BoxComponent.resolutions[0]
    for index, resolution in enumerate(BoxComponent.resolutions):
        if resolution == old_resolution and index + 1 < len(BoxComponent.resolutions):
            new_resolution = BoxComponent.resolutions[index + 1]

    LT_ENGINE_INFO.resize(new_resolution)
    LT_OPTIONS_INFO.resize(new_resolution)
    for wheel_id in LT_WHEEL_INFOS:
        info = LT_WHEEL_INFOS[wheel_id]
        info.resize(new_resolution)

    LT_OPTIONS_INFO.set_option("Size", new_resolution)


def on_click_suspension(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options suspension button. """
    toggle_option("Suspension")


def on_click_temps(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options temps button. """
    toggle_option("Temps")


def on_click_tire(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options tire button. """
    toggle_option("Tire")


def on_click_wear(pos_x: int, pos_y: int) -> None:
    """ Handles the click in one of the options wear button. """
    toggle_option("Wear")


def on_dismiss(window_id: int) -> None:
    """ Deactivates a window. """
    if LT_ENGINE_INFO.get_window_id() is window_id:
        LT_ENGINE_INFO.set_active(False)

    for wheel_id in LT_WHEEL_INFOS:
        info = LT_WHEEL_INFOS[wheel_id]
        if info.get_window_id() is window_id:
            info.set_active(False)


def on_render_engine(delta_t: float) -> None:
    """ Called every frame. """
    if LT_ENGINE_INFO.is_active():
        LT_ENGINE_INFO.draw(delta_t)


def on_render_fl(delta_t: float) -> None:
    """ Called every frame. """
    info = LT_WHEEL_INFOS["FL"]
    if info.is_active():
        info.draw(delta_t)


def on_render_fr(delta_t: float) -> None:
    """ Called every frame. """
    info = LT_WHEEL_INFOS["FR"]
    if info.is_active():
        info.draw(delta_t)


def on_render_rl(delta_t: float) -> None:
    """ Called every frame. """
    info = LT_WHEEL_INFOS["RL"]
    if info.is_active():
        info.draw(delta_t)


def on_render_rr(delta_t: float) -> None:
    """ Called every frame. """
    info = LT_WHEEL_INFOS["RR"]
    if info.is_active():
        info.draw(delta_t)


def toggle_option(name: str) -> None:
    """ Called to toggle the option for a settings on all widgets. """
    enabled = not LT_OPTIONS_INFO.get_option(name)

    LT_ENGINE_INFO.set_option(name, enabled)
    LT_OPTIONS_INFO.set_option(name, enabled)
    for wheel_id in LT_WHEEL_INFOS:
        info = LT_WHEEL_INFOS[wheel_id]
        info.set_option(name, enabled)
