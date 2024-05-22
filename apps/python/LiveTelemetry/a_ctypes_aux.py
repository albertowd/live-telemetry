#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Important to be the first load the plugin does!

@author: albertowd
"""

from platform import architecture
from sys import path
import os

# Using the right platform ctypes.
path.append(os.path.join(os.path.dirname(__file__), "stdlib64" if architecture()[0] == "64bit" else "stdlib"))

# Using app path to set root folder.
os.environ["PATH"] = "{};.".format(os.environ["PATH"])

"""
Its ok to run whatever the plugin wants now.
"""
