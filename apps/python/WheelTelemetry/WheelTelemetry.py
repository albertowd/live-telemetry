import os
import platform
import sys
STD_LIB = "stdlib"
if platform.architecture()[0] == "64bit":
    STD_LIB = "stdlib64"
sys.path.append(os.path.join(os.path.dirname(__file__), STD_LIB))
os.environ["PATH"] = os.environ["PATH"] + ";."

import ac
from wcomponents import BoxComponent
from winfo import Info
from wconfig import Config
from wutil import log

# Each wheel window
WHEEL_INFOS = {}


def acMain(ac_version):
    """ Setups the app. """
    log("Starting Wheel Telemetry on AC Python API version {}...".format(ac_version))

    global WHEEL_INFOS
    for index in range(4):
        info = Info(index)
        window_id = info.get_window_id()
        ac.addOnAppActivatedListener(window_id, on_activation)
        ac.addOnAppDismissedListener(window_id, on_dismiss)
        WHEEL_INFOS[info.get_id()] = info

    ac.addOnClickedListener(
        WHEEL_INFOS["FL"].get_button_id(), on_click_resolution)
    ac.addOnClickedListener(
        WHEEL_INFOS["FR"].get_button_id(), on_click_resolution)
    ac.addOnClickedListener(
        WHEEL_INFOS["RL"].get_button_id(), on_click_resolution)
    ac.addOnClickedListener(
        WHEEL_INFOS["RR"].get_button_id(), on_click_resolution)

    ac.addRenderCallback(WHEEL_INFOS["FL"].get_window_id(), on_render_fl)
    ac.addRenderCallback(WHEEL_INFOS["FR"].get_window_id(), on_render_fr)
    ac.addRenderCallback(WHEEL_INFOS["RL"].get_window_id(), on_render_rl)
    ac.addRenderCallback(WHEEL_INFOS["RR"].get_window_id(), on_render_rr)

    return "Wheel Telemetry"


def acShutdown():
    """ Called when the session ends (or restarts). """
    log("Shuting down Wheel Telemetry...")

    configs = Config()
    global WHEEL_INFOS

    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        configs.set_active(wheel_id, info.is_active())
        info.set_active(False)
        pos_x, pos_y = info.get_position()
        configs.set_position(wheel_id, pos_x, pos_y)
    configs.save_config()


def acUpdate(delta_t):
    """ Called every physics update. """
    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.is_active():
            info.update()


def on_activation(window_id):
    """ Activates a wheel window. """
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
    for wheel_id in WHEEL_INFOS:
        WHEEL_INFOS[wheel_id].resize(new_resolution)


def on_dismiss(window_id):
    """ Deactivates a wheel window. """
    global WHEEL_INFOS
    for wheel_id in WHEEL_INFOS:
        info = WHEEL_INFOS[wheel_id]
        if info.get_window_id() is window_id:
            info.set_active(False)


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
