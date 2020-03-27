#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Important to be the first load the plugin does!

@author: albertowd
"""

import ac
import os
import platform
import sys

# Using the right platform ctypes.
sys.path.append(os.path.join(os.path.dirname(
    __file__), "stdlib64" if platform.architecture()[0] == "64bit" else "stdlib"))

# Using app path to set root folder.
os.environ["PATH"] = "{};.".format(os.environ["PATH"])

ac.log(os.environ["PATH"])

"""
Its ok to run whatever the plugin wants now.
"""
