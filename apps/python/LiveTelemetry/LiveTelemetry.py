#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Live Telemetry App for Assetto Corsa
v 1.4.0
https://github.com/albertowd/Wheellive-telemetry
@author: albertowd
"""
from lib.lt_util import clear_logs, export_saved_log, log, update_acd
from lib.lt_wheel_info import WheelInfo
from lib.lt_options_info import OptionsInfo
from lib.lt_engine_info import EngineInfo
from lib.lt_config import Config
from lib.lt_components import BoxComponent
import os
import platform
import sys

import ac

if platform.architecture()[0] == "64bit":
    sys.path.append("apps/python/LiveTelemetry/stdlib64")
else:
    sys.path.append("apps/python/LiveTelemetry/stdlib")
os.environ["PATH"] = os.environ["PATH"] + ";."


# VERSION
LT_VERSION = '1.4.0'

# Each window
ENGINE_INFO = None
OPTIONS_INFO = None
WHEEL_INFOS = {}


def acMain(ac_version):
    """ Initiates the program. """
    configs = Config()

    global LT_VERSION
    log("Starting Live Telemetry {} on AC Python API version {}...".format(
        LT_VERSION, ac_version))

    update_acd("content/cars/{}".format(ac.getCarName(0)))

    global WHEEL_INFOS
    for index in range(4):
        info = WheelInfo(configs,index)
        window_id = info.get_window_id()
        ac.addOnAppActivatedListener(window_id, on_activation)
        ac.addOnAppDismissedListener(window_id, on_dismiss)
        WHEEL_INFOS[info.get_id()] = info

    ac.addRenderCallback(WHEEL_INFOS["FL"].get_window_id(), on_render_fl)
    ac.addRenderCallback(WHEEL_INFOS["FR"].get_window_id(), on_render_fr)
    ac.addRenderCallback(WHEEL_INFOS["RL"].get_window_id(), on_render_rl)
    ac.addRenderCallback(WHEEL_INFOS["RR"].get_window_id(), on_render_rr)

    global OPTIONS_INFO
    OPTIONS_INFO = OptionsInfo(configs, LT_VERSION)
    ac.addOnClickedListener(
        OPTIONS_INFO.get_logging_button_id(), on_click_logging)
    ac.addOnClickedListener(
        OPTIONS_INFO.get_resolution_button_id(), on_click_resolution)

    global ENGINE_INFO
    ENGINE_INFO = EngineInfo(configs)
    window_id = ENGINE_INFO.get_window_id()
    ac.addOnAppActivatedListener(window_id, on_activation)
    ac.addOnAppDismissedListener(window_id, on_dismiss)
    ac.addRenderCallback(ENGINE_INFO.get_window_id(), on_render_engine)

    log("Live Telemetry started.")

    return "Live Telemetry"


def acShutdown():
    """ Called when the session ends (or restarts). """
    log("Ending down Live Telemetry...")

    configs = Config()
    global ENGINE_INFO
    global OPTIONS_INFO
    global WHEEL_INFOS

    if OPTIONS_INFO.get_logging():
        log("Saving csv data...")
        for wheel_id in WHEEL_INFOS:
            info = WHEEL_INFOS[wheel_id]
            export_saved_log(info.get_data_log(), wheel_id)
        export_saved_log(ENGINE_INFO.get_data_log(), 'EN')
    else:
        log("Deleting old csv data...")
        clear_logs()

    log("Saving engine configurations...")
    configs.set_engine_active(ENGINE_INFO.is_active())
    ENGINE_INFO.set_active(False)
    pos_x, pos_y = ENGINE_INFO.get_position()
    configs.set_engine_position(pos_x, pos_y)

    log("Saving options configurations...")
    configs.set_logging(OPTIONS_INFO.get_logging())
    configs.set_resolution(OPTIONS_INFO.get_resolution())
    pos_x, pos_y = OPTIONS_INFO.get_position()
    configs.set_options_position(pos_x, pos_y)

    log("Saving wheels configurations...")
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        configs.set_active(wheel_id, info.is_active())
        info.set_active(False)
        pos_x, pos_y = info.get_position()
        configs.set_position(wheel_id, pos_x, pos_y)

    configs.save_config()
    log("Live Telemetry ended.")


def acUpdate(delta_t):
    """ Called every physics update. """
    global ENGINE_INFO
    if ENGINE_INFO.is_active():
        ENGINE_INFO.update()

    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.is_active():
            info.update()


def on_activation(window_id):
    """ Activates a window. """
    global ENGINE_INFO
    if ENGINE_INFO.get_window_id() is window_id:
        ENGINE_INFO.set_active(True)

    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.get_window_id() is window_id:
            info.set_active(True)


def on_click_logging(pos_x, pos_y):
    """ Handles the click in one of the resolution buttons. """
    global ENGINE_INFO
    global OPTIONS_INFO
    global WHEEL_INFOS

    logging = not OPTIONS_INFO.get_logging()

    ENGINE_INFO.set_logging(logging)
    OPTIONS_INFO.set_logging(logging)
    for wheel_id in WHEEL_INFOS:
        WHEEL_INFOS[wheel_id].set_logging(logging)


def on_click_resolution(pos_x, pos_y):
    """ Handles the click in one of the resolution buttons. """
    global ENGINE_INFO
    global OPTIONS_INFO
    global WHEEL_INFOS

    old_resolution = OPTIONS_INFO.get_resolution()
    new_resolution = "480p"
    for index, resolution in enumerate(BoxComponent.resolutions):
        if resolution == old_resolution and index + 1 < len(BoxComponent.resolutions):
            new_resolution = BoxComponent.resolutions[index + 1]

    ENGINE_INFO.resize(new_resolution)
    OPTIONS_INFO.resize(new_resolution)
    for wheel_id in WHEEL_INFOS:
        WHEEL_INFOS[wheel_id].resize(new_resolution)


def on_dismiss(window_id):
    """ Deactivates a window. """
    global ENGINE_INFO
    if ENGINE_INFO.get_window_id() is window_id:
        ENGINE_INFO.set_active(False)

    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.get_window_id() is window_id:
            info.set_active(False)


def on_render_engine(delta_t):
    """ Called every frame. """
    global ENGINE_INFO
    if ENGINE_INFO.is_active():
        ENGINE_INFO.draw()


def on_render_fl(delta_t):
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["FL"]
    if info.is_active():
        info.draw()


def on_render_fr(delta_t):
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["FR"]
    if info.is_active():
        info.draw()


def on_render_rl(delta_t):
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["RL"]
    if info.is_active():
        info.draw()


def on_render_rr(delta_t):
    """ Called every frame. """
    global WHEEL_INFOS
    info = WHEEL_INFOS["RR"]
    if info.is_active():
        info.draw()
