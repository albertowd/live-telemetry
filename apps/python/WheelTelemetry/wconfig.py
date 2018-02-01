"""
Module to load and save app options.
"""
import configparser
import os

WHEEL_TELEMETRY_CONFIGS = configparser.ConfigParser()


def load_config():
    """ Loads or creates the app config file. """
    if os.path.isfile("apps/python/WheelTelemetry/cfg.ini"):
        WHEEL_TELEMETRY_CONFIGS.read("apps/python/WheelTelemetry/cfg.ini")
    else:
        WHEEL_TELEMETRY_CONFIGS["Windows"] = {
            "FL": "False", "FR": "False", "RL": "False", "RR": "False", "SIZE": "HD"}
        WHEEL_TELEMETRY_CONFIGS["Positions"] = {"FL_x": "100", "FL_y": "100", "FR_x": "780",
                                                "FR_y": "100", "RL_x": "100", "RL_y": "420",
                                                "RR_x": "780", "RR_y": "420"}


def get_resolution():
    """ Returns the windows resolution. """
    return get_str("Windows", "SIZE")


def get_str(section, option):
    """ Returns an option. """
    global WHEEL_TELEMETRY_CONFIGS
    return WHEEL_TELEMETRY_CONFIGS.get(section, option)


def get_x(wheel_id):
    """ Returns the x position of window. """
    return float(get_str("Positions", "{}_x".format(wheel_id)))


def get_y(wheel_id):
    """ Returns the y position of window. """
    return float(get_str("Positions", "{}_y".format(wheel_id)))


def is_active(wheel_id):
    """ Returns if window is active. """
    return bool(get_str("Windows", wheel_id))


def save_config():
    """ Writes the actual options on the config file. """
    global WHEEL_TELEMETRY_CONFIGS
    cfg_file = open("apps/python/WheelTelemetry/cfg.ini", 'w')
    WHEEL_TELEMETRY_CONFIGS.write(cfg_file)
    cfg_file.close()


def set_active(wheel_id, active):
    """ Updates if window is active. """
    set_str("Windows", wheel_id, str(active))


def set_position(wheel_id, pos_x, pos_y):
    """ Updates window position. """
    set_str("Positions", "{}_x".format(wheel_id), str(pos_x))
    set_str("Positions", "{}_y".format(wheel_id), str(pos_y))


def set_str(section, option, value):
    """ Updates an option. """
    global WHEEL_TELEMETRY_CONFIGS
    WHEEL_TELEMETRY_CONFIGS.set(section, option, value)
