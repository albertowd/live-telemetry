#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Live Telemetry App for Assetto Corsa
v 1.8.0
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
LT_VERSION = "1.8.0"


class _State:  # pylint: disable=too-few-public-methods
    """ Holds plugin runtime state so AC entry-points can mutate attributes
    instead of reassigning module globals. """

    def __init__(self):
        self.acd_obj = None
        self.configs = None
        self.engine_info = None
        self.options_info = None
        self.wheel_infos = {}


LT = _State()


def acMain(ac_version: str) -> None:
    """ Initiates the program. """
    log("Starting Live Telemetry {} on AC Python API version {}...".format(
        LT_VERSION, ac_version))

    # Preload Arial Bold so tire-temp readouts can use setCustomFont.
    ac.initFont(0, "Arial", 0, 1)

    log("Loading configs...")
    LT.configs = Config(LT_VERSION)

    log("Loading {} info...".format(ac.getCarName(0)))
    LT.acd_obj = ACD("content/cars/{}".format(ac.getCarName(0)))
    log("Loaded correctly")

    log("Loading options window...")
    LT.options_info = OptionsInfo(LT.configs)
    boost_button_id = LT.options_info.get_button_id("BoostBar")
    if boost_button_id is not None:
        ac.addOnClickedListener(boost_button_id, on_click_boost)
    ac.addOnClickedListener(LT.options_info.get_button_id("Camber"), on_click_camber)
    ac.addOnClickedListener(LT.options_info.get_button_id("Dirt"), on_click_dirt)
    ac.addOnClickedListener(LT.options_info.get_button_id("Height"), on_click_height)
    ac.addOnClickedListener(LT.options_info.get_button_id("Load"), on_click_load)
    ac.addOnClickedListener(LT.options_info.get_button_id("Lock"), on_click_lock)
    ac.addOnClickedListener(LT.options_info.get_button_id("Logging"), on_click_logging)
    ac.addOnClickedListener(LT.options_info.get_button_id("Pressure"), on_click_pressure)
    ac.addOnClickedListener(LT.options_info.get_button_id("RPMPower"), on_click_rpm)
    ac.addOnClickedListener(LT.options_info.get_button_id("Size"), on_click_size)
    ac.addOnClickedListener(LT.options_info.get_button_id("Suspension"), on_click_suspension)
    ac.addOnClickedListener(LT.options_info.get_button_id("Temps"), on_click_temps)
    ac.addOnClickedListener(LT.options_info.get_button_id("Tire"), on_click_tire)
    ac.addOnClickedListener(LT.options_info.get_button_id("Wear"), on_click_wear)

    log("Loading engine window...")
    LT.engine_info = EngineInfo(LT.acd_obj, LT.configs)
    window_id = LT.engine_info.get_window_id()
    ac.addOnAppActivatedListener(window_id, on_activation)
    ac.addOnAppDismissedListener(window_id, on_dismiss)
    ac.addRenderCallback(LT.engine_info.get_window_id(), on_render_engine)

    log("Loading wheel windows...")
    for index in range(4):
        info = WheelInfo(LT.acd_obj, LT.configs, index)
        window_id = info.get_window_id()
        ac.addOnAppActivatedListener(window_id, on_activation)
        ac.addOnAppDismissedListener(window_id, on_dismiss)
        LT.wheel_infos[info.get_id()] = info

    ac.addRenderCallback(LT.wheel_infos["FL"].get_window_id(), on_render_fl)
    ac.addRenderCallback(LT.wheel_infos["FR"].get_window_id(), on_render_fr)
    ac.addRenderCallback(LT.wheel_infos["RL"].get_window_id(), on_render_rl)
    ac.addRenderCallback(LT.wheel_infos["RR"].get_window_id(), on_render_rr)

    log("Live Telemetry started.")

    return "Live Telemetry"


def acShutdown() -> None:
    """ Called when the session ends (or restarts). """
    log("Shutting down Live Telemetry...")

    log("Saving options configurations...")
    boost_option = LT.options_info.get_option("BoostBar")
    if boost_option is not None:
        LT.configs.set_option("BoostBar", boost_option)
    LT.configs.set_option("Camber", LT.options_info.get_option("Camber"))
    LT.configs.set_option("Dirt", LT.options_info.get_option("Dirt"))
    LT.configs.set_option("Height", LT.options_info.get_option("Height"))
    LT.configs.set_option("Load", LT.options_info.get_option("Load"))
    LT.configs.set_option("Lock", LT.options_info.get_option("Lock"))
    LT.configs.set_option("Logging", LT.options_info.get_option("Logging"))
    LT.configs.set_option("Pressure", LT.options_info.get_option("Pressure"))
    LT.configs.set_option("RPMPower", LT.options_info.get_option("RPMPower"))
    LT.configs.set_option("Size", LT.options_info.get_option("Size"))
    LT.configs.set_option("Suspension", LT.options_info.get_option("Suspension"))
    LT.configs.set_option("Temps", LT.options_info.get_option("Temps"))
    LT.configs.set_option("Tire", LT.options_info.get_option("Tire"))
    LT.configs.set_option("Wear", LT.options_info.get_option("Wear"))

    log("Saving windows configurations...")
    LT.configs.set_window_active("EN", LT.engine_info.is_active())
    LT.configs.set_window_position("EN", LT.engine_info.get_position())
    LT.engine_info.set_active(False)
    LT.configs.set_window_position("OP", LT.options_info.get_position())
    for wheel_id, info in LT.wheel_infos.items():
        LT.configs.set_window_active(wheel_id, info.is_active())
        LT.configs.set_window_position(wheel_id, info.get_position())
        info.set_active(False)

    LT.configs.save_config()

    if (
        LT.engine_info.has_data_logged()
        or LT.wheel_infos["FL"].has_data_logged() or LT.wheel_infos["FR"].has_data_logged()
        or LT.wheel_infos["RL"].has_data_logged() or LT.wheel_infos["RR"].has_data_logged()
    ):
        log("Saving csv data...")
        for wheel_id, info in LT.wheel_infos.items():
            export_saved_log(info.get_data_log(), wheel_id)
        export_saved_log(LT.engine_info.get_data_log(), "EN")
    else:
        log("Deleting old csv data...")
        clear_logs()

    LT.acd_obj = None
    LT.configs = None
    LT.engine_info = None
    LT.options_info = None
    LT.wheel_infos = {}
    log("Live Telemetry ended.")


def acUpdate(delta_t: float) -> None:
    """ Called every physics update. """
    if LT.engine_info.is_active():
        LT.engine_info.update(delta_t)

    for info in LT.wheel_infos.values():
        if info.is_active():
            info.update(delta_t)


def on_activation(window_id: int) -> None:
    """ Activates a window. """
    if LT.engine_info.get_window_id() is window_id:
        LT.engine_info.set_active(True)

    for info in LT.wheel_infos.values():
        if info.get_window_id() is window_id:
            info.set_active(True)


def on_click_boost(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options boost bar button. """
    toggle_option("BoostBar")


def on_click_camber(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options camber button. """
    toggle_option("Camber")


def on_click_dirt(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options dirt button. """
    toggle_option("Dirt")


def on_click_height(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options height button. """
    toggle_option("Height")


def on_click_load(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options load button. """
    toggle_option("Load")


def on_click_lock(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options lock button. """
    toggle_option("Lock")


def on_click_logging(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options logging button. """
    toggle_option("Logging")


def on_click_pressure(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options pressure button. """
    toggle_option("Pressure")


def on_click_rpm(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options rpm button. """
    toggle_option("RPMPower")


def on_click_size(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options size button. """
    old_resolution = LT.options_info.get_option("Size")
    new_resolution = BoxComponent.resolutions[0]
    for index, resolution in enumerate(BoxComponent.resolutions):
        if resolution == old_resolution and index + 1 < len(BoxComponent.resolutions):
            new_resolution = BoxComponent.resolutions[index + 1]

    LT.engine_info.resize(new_resolution)
    LT.options_info.resize(new_resolution)
    for info in LT.wheel_infos.values():
        info.resize(new_resolution)

    LT.options_info.set_option("Size", new_resolution)


def on_click_suspension(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options suspension button. """
    toggle_option("Suspension")


def on_click_temps(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options temps button. """
    toggle_option("Temps")


def on_click_tire(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options tire button. """
    toggle_option("Tire")


def on_click_wear(_pos_x: int, _pos_y: int) -> None:
    """ Handles the click in one of the options wear button. """
    toggle_option("Wear")


def on_dismiss(window_id: int) -> None:
    """ Deactivates a window. """
    if LT.engine_info.get_window_id() is window_id:
        LT.engine_info.set_active(False)

    for info in LT.wheel_infos.values():
        if info.get_window_id() is window_id:
            info.set_active(False)


def on_render_engine(delta_t: float) -> None:
    """ Called every frame. """
    if LT.engine_info.is_active():
        LT.engine_info.draw(delta_t)


def on_render_fl(delta_t: float) -> None:
    """ Called every frame. """
    info = LT.wheel_infos["FL"]
    if info.is_active():
        info.draw(delta_t)


def on_render_fr(delta_t: float) -> None:
    """ Called every frame. """
    info = LT.wheel_infos["FR"]
    if info.is_active():
        info.draw(delta_t)


def on_render_rl(delta_t: float) -> None:
    """ Called every frame. """
    info = LT.wheel_infos["RL"]
    if info.is_active():
        info.draw(delta_t)


def on_render_rr(delta_t: float) -> None:
    """ Called every frame. """
    info = LT.wheel_infos["RR"]
    if info.is_active():
        info.draw(delta_t)


def toggle_option(name: str) -> None:
    """ Called to toggle the option for a settings on all widgets. """
    enabled = not LT.options_info.get_option(name)

    LT.engine_info.set_option(name, enabled)
    LT.options_info.set_option(name, enabled)
    for info in LT.wheel_infos.values():
        info.set_option(name, enabled)
