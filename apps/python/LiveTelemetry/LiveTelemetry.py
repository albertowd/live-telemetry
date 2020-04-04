#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Live Telemetry App for Assetto Corsa
v 1.5.1
https://github.com/albertowd/Wheellive-telemetry
@author: albertowd
"""


import a_ctypes_aux

import ac

from lib.lt_acd import ACD
from lib.lt_components import BoxComponent
from lib.lt_config import Config
from lib.lt_engine_info import EngineInfo
from lib.lt_options_info import OptionsInfo
from lib.lt_wheel_info import WheelInfo
from lib.lt_util import clear_logs, export_saved_log, log

# APP VERSION
LT_VERSION = "1.5.1"

# Loaded car files
ACD_OBJ = None

# Global configurations
CONFIGS = None

# Each window
ENGINE_INFO = None
OPTIONS_INFO = None
WHEEL_INFOS = {}


def acMain(ac_version: str) -> None:
    """ Initiates the program. """
    global ACD_OBJ
    global CONFIGS
    global LT_VERSION

    log("Starting Live Telemetry {} on AC Python API version {}...".format(
        LT_VERSION, ac_version))

    log("Loading configs...")
    CONFIGS = Config(LT_VERSION)

    log("Loading {} info...".format(ac.getCarName(0)))
    ACD_OBJ = ACD("content/cars/{}".format(ac.getCarName(0)))
    log("Loaded correctly")

    log("Loading options window...")
    global OPTIONS_INFO
    OPTIONS_INFO = OptionsInfo(CONFIGS)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Camber"), on_click_camber)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Dirt"), on_click_dirt)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Height"), on_click_height)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Load"), on_click_load)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Logging"), on_click_logging)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Pressure"), on_click_pressure)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("RPMPower"), on_click_rpm)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Size"), on_click_size)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Suspension"), on_click_suspension)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Temps"), on_click_temps)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Tire"), on_click_tire)
    ac.addOnClickedListener(OPTIONS_INFO.get_button_id("Wear"), on_click_wear)

    log("Loading engine window...")
    global ENGINE_INFO
    ENGINE_INFO = EngineInfo(ACD_OBJ, CONFIGS)
    window_id = ENGINE_INFO.get_window_id()
    ac.addOnAppActivatedListener(window_id, on_activation)
    ac.addOnAppDismissedListener(window_id, on_dismiss)
    ac.addRenderCallback(ENGINE_INFO.get_window_id(), on_render_engine)

    log("Loading wheel windows...")
    global WHEEL_INFOS
    for index in range(4):
        info = WheelInfo(ACD_OBJ, CONFIGS, index)
        window_id = info.get_window_id()
        ac.addOnAppActivatedListener(window_id, on_activation)
        ac.addOnAppDismissedListener(window_id, on_dismiss)
        WHEEL_INFOS[info.get_id()] = info

    ac.addRenderCallback(WHEEL_INFOS["FL"].get_window_id(), on_render_fl)
    ac.addRenderCallback(WHEEL_INFOS["FR"].get_window_id(), on_render_fr)
    ac.addRenderCallback(WHEEL_INFOS["RL"].get_window_id(), on_render_rl)
    ac.addRenderCallback(WHEEL_INFOS["RR"].get_window_id(), on_render_rr)

    log("Live Telemetry started.")

    return "Live Telemetry"


def acShutdown() -> None:
    """ Called when the session ends (or restarts). """
    log("Shutting down Live Telemetry...")

    global CONFIGS
    global ENGINE_INFO
    global OPTIONS_INFO
    global WHEEL_INFOS

    log("Saving options configurations...")
    CONFIGS.set_option("Camber", OPTIONS_INFO.get_option("Camber"))
    CONFIGS.set_option("Dirt", OPTIONS_INFO.get_option("Dirt"))
    CONFIGS.set_option("Height", OPTIONS_INFO.get_option("Height"))
    CONFIGS.set_option("Load", OPTIONS_INFO.get_option("Load"))
    CONFIGS.set_option("Logging", OPTIONS_INFO.get_option("Logging"))
    CONFIGS.set_option("Pressure", OPTIONS_INFO.get_option("Pressure"))
    CONFIGS.set_option("RPMPower", OPTIONS_INFO.get_option("RPMPower"))
    CONFIGS.set_option("Size", OPTIONS_INFO.get_option("Size"))
    CONFIGS.set_option("Suspension", OPTIONS_INFO.get_option("Suspension"))
    CONFIGS.set_option("Temps", OPTIONS_INFO.get_option("Temps"))
    CONFIGS.set_option("Tire", OPTIONS_INFO.get_option("Tire"))
    CONFIGS.set_option("Wear", OPTIONS_INFO.get_option("Wear"))

    log("Saving windows configurations...")
    CONFIGS.set_window_active("EN", ENGINE_INFO.is_active())
    CONFIGS.set_window_position("EN", ENGINE_INFO.get_position())
    ENGINE_INFO.set_active(False)
    CONFIGS.set_window_position("OP", OPTIONS_INFO.get_position())
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        CONFIGS.set_window_active(wheel_id, info.is_active())
        CONFIGS.set_window_position(wheel_id, info.get_position())
        info.set_active(False)

    CONFIGS.save_config()

    if ENGINE_INFO.has_data_logged() or WHEEL_INFOS["FL"].has_data_logged() or WHEEL_INFOS["FL"].has_data_logged() or WHEEL_INFOS["RL"].has_data_logged() or WHEEL_INFOS["RR"].has_data_logged():
        log("Saving csv data...")
        for wheel_id in WHEEL_INFOS:
            info = WHEEL_INFOS[wheel_id]
            export_saved_log(info.get_data_log(), wheel_id)
        export_saved_log(ENGINE_INFO.get_data_log(), "EN")
    else:
        log("Deleting old csv data...")
        clear_logs()
    log("Live Telemetry ended.")


def acUpdate(delta_t: float) -> None:
    """ Called every physics update. """
    global ENGINE_INFO
    if ENGINE_INFO.is_active():
        ENGINE_INFO.update()

    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.is_active():
            info.update()


def on_activation(window_id: int) -> None:
    """ Activates a window. """
    global ENGINE_INFO
    if ENGINE_INFO.get_window_id() is window_id:
        ENGINE_INFO.set_active(True)

    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.get_window_id() is window_id:
            info.set_active(True)

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
    global ENGINE_INFO
    global OPTIONS_INFO
    global WHEEL_INFOS

    old_resolution = OPTIONS_INFO.get_option("Size")
    new_resolution = "480p"
    for index, resolution in enumerate(BoxComponent.resolutions):
        if resolution == old_resolution and index + 1 < len(BoxComponent.resolutions):
            new_resolution = BoxComponent.resolutions[index + 1]

    ENGINE_INFO.resize(new_resolution)
    OPTIONS_INFO.resize(new_resolution)
    for wheel_id in WHEEL_INFOS:
        WHEEL_INFOS[wheel_id].resize(new_resolution)

    OPTIONS_INFO.set_option("Size", new_resolution)

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
    global ENGINE_INFO
    if ENGINE_INFO.get_window_id() is window_id:
        ENGINE_INFO.set_active(False)

    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.get_window_id() is window_id:
            info.set_active(False)


def on_render_engine(delta_t: float) -> None:
    """ Called every frame. """
    global ENGINE_INFO
    if ENGINE_INFO.is_active():
        ENGINE_INFO.draw()


def on_render_fl(delta_t: float) -> None:
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["FL"]
    if info.is_active():
        info.draw()


def on_render_fr(delta_t: float) -> None:
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["FR"]
    if info.is_active():
        info.draw()


def on_render_rl(delta_t: float) -> None:
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["RL"]
    if info.is_active():
        info.draw()


def on_render_rr(delta_t: float) -> None:
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["RR"]
    if info.is_active():
        info.draw()

def toggle_option(name: str) -> None:
    global ENGINE_INFO
    global OPTIONS_INFO
    global WHEEL_INFOS

    enabled = not OPTIONS_INFO.get_option(name)

    ENGINE_INFO.set_option(name, enabled)
    OPTIONS_INFO.set_option(name, enabled)
    for wheel_id in WHEEL_INFOS:
        WHEEL_INFOS[wheel_id].set_option(name, enabled)