"""
Module to log app messages.
"""
import ac


def log(message, console=True, app_log=True):
    """ Logs a message on the log and console. """
    formated = "[WT] {}".format(message)
    if console:
        ac.console(formated)
    if app_log:
        ac.log(formated)
