#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Live Telemetry App for Assetto Corsa
v 1.2.2
https://github.com/albertowd/WheelTelemetry
@author: albertowd
"""
import os
import platform
import sys

import ac

from lt_components import BoxComponent, update_acd
from lt_config import Config
from lt_engine_info import EngineInfo
from lt_wheel_info import WheelInfo
from lt_util import log

STD_LIB = "stdlib"
if platform.architecture()[0] == "64bit":
    STD_LIB = "stdlib64"
sys.path.append(os.path.join(os.path.dirname(__file__), STD_LIB))
os.environ["PATH"] = os.environ["PATH"] + ";."

# Each window
ENGINE_INFO = None
WHEEL_INFOS = {}


def acMain(ac_version):
    """ Initiates the program. """
    log("Starting Live Telemetry on AC Python API version {}...".format(ac_version))

    try:
        update_acd("content/cars/{}/data.acd".format(ac.getCarName(0)))
        
        global WHEEL_INFOS
        for index in range(4):
            info = WheelInfo(index)
            window_id = info.get_window_id()
            ac.addOnAppActivatedListener(window_id, on_activation)
            ac.addOnAppDismissedListener(window_id, on_dismiss)
            WHEEL_INFOS[info.get_id()] = info

        ac.addOnClickedListener(WHEEL_INFOS["FL"].get_button_id(), on_click_resolution)
        ac.addOnClickedListener(WHEEL_INFOS["FR"].get_button_id(), on_click_resolution)
        ac.addOnClickedListener(WHEEL_INFOS["RL"].get_button_id(), on_click_resolution)
        ac.addOnClickedListener(WHEEL_INFOS["RR"].get_button_id(), on_click_resolution)
    
        ac.addRenderCallback(WHEEL_INFOS["FL"].get_window_id(), on_render_fl)
        ac.addRenderCallback(WHEEL_INFOS["FR"].get_window_id(), on_render_fr)
        ac.addRenderCallback(WHEEL_INFOS["RL"].get_window_id(), on_render_rl)
        ac.addRenderCallback(WHEEL_INFOS["RR"].get_window_id(), on_render_rr)
        
        global ENGINE_INFO
        ENGINE_INFO = EngineInfo()
        window_id = ENGINE_INFO.get_window_id()
        ac.addOnAppActivatedListener(window_id, on_activation)
        ac.addOnAppDismissedListener(window_id, on_dismiss)
        ac.addOnClickedListener(ENGINE_INFO.get_button_id(), on_click_resolution)
        ac.addRenderCallback(ENGINE_INFO.get_window_id(), on_render_engine)
        
        log("Live Telemetry started.")
    except:
        log("Start error:")
        log(sys.exc_info()[0])
        log(sys.exc_info()[1])
        log(sys.exc_info()[2])

    return "Live Telemetry"


def acShutdown():
    """ Called when the session ends (or restarts). """
    log("Ending down Live Telemetry...")

    try:
        configs = Config()
        
        global ENGINE_INFO
        configs.set_engine_active(ENGINE_INFO.is_active())
        ENGINE_INFO.set_active(False)
        pos_x, pos_y = ENGINE_INFO.get_position()
        configs.set_engine_position(pos_x, pos_y)

        global WHEEL_INFOS
        for wheel_id in WHEEL_INFOS:
            info = WHEEL_INFOS[wheel_id]
            configs.set_active(wheel_id, info.is_active())
            info.set_active(False)
            pos_x, pos_y = info.get_position()
            configs.set_position(wheel_id, pos_x, pos_y)
        
        configs.save_config()
        log("Live Telemetry ended.")
    except:
        log("End error:")
        log(sys.exc_info()[0])
        log(sys.exc_info()[1])
        log(sys.exc_info()[2])


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


def on_click_resolution(pos_x, pos_y):
    """ Handles the click in one of the resolution buttons. """
    global WHEEL_INFOS
    old_resolution = ac.getText(WHEEL_INFOS["FL"].get_button_id())
    new_resolution = "HD"
    for index, resolution in enumerate(BoxComponent.resolutions):
        if resolution == old_resolution and index + 1 < len(BoxComponent.resolutions):
            new_resolution = BoxComponent.resolutions[index + 1]
    
    global ENGINE_INFO
    ENGINE_INFO.resize(new_resolution)
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
