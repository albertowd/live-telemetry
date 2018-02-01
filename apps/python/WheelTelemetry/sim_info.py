"""
Assetto Corsa shared memory for Python applications

_ctypes.pyd must be somewhere in sys.path, because AC doesn't include all Python binaries.

Usage. Let's say you have following folder structure::

    some_app
        DLLs
            _ctypes.pyd
        some_app.py

some_app.py::

    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'DLLs'))

    from sim_info import info

    print(info.graphics.tyreCompound, info.physics.rpms, info.static.playerNick)


Do whatever you want with this code!
WBR, Rombik :)
"""
import mmap
import functools
import ctypes
from ctypes import c_int32, c_float, c_wchar


AC_STATUS = c_int32
AC_OFF = 0
AC_REPLAY = 1
AC_LIVE = 2
AC_PAUSE = 3
AC_SESSION_TYPE = c_int32
AC_UNKNOWN = -1
AC_PRACTICE = 0
AC_QUALIFY = 1
AC_RACE = 2
AC_HOTLAP = 3
AC_TIME_ATTACK = 4
AC_DRIFT = 5
AC_DRAG = 6

# Added on Oct 26, 2015
AC_FLAG_TYPE = c_int32
AC_NO_FLAG = 0
AC_BLUE_FLAG = 1
AC_YELLOW_FLAG = 2
AC_BLACK_FLAG = 3
AC_WHITE_FLAG = 4
AC_CHECKERED_FLAG = 5
AC_PENALTY_FLAG = 6


class SPageFilePhysics(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('packetId', c_int32),
        ('gas', c_float),
        ('brake', c_float),
        ('fuel', c_float),
        ('gear', c_int32),
        ('rpms', c_int32),
        ('steerAngle', c_float),
        ('speedKmh', c_float),
        ('velocity', c_float * 3),
        ('accG', c_float * 3),
        ('wheelSlip', c_float * 4),
        ('wheelLoad', c_float * 4),
        ('wheelsPressure', c_float * 4),
        ('wheelAngularSpeed', c_float * 4),
        ('tyreWear', c_float * 4),
        ('tyreDirtyLevel', c_float * 4),
        ('tyreCoreTemperature', c_float * 4),
        ('camberRAD', c_float * 4),
        ('suspensionTravel', c_float * 4),
        ('drs', c_float),
        ('tc', c_float),
        ('heading', c_float),
        ('pitch', c_float),
        ('roll', c_float),
        ('cgHeight', c_float),
        ('carDamage', c_float * 5),
        ('numberOfTyresOut', c_int32),
        ('pitLimiterOn', c_int32),
        ('abs', c_float),

        # Added on Oct 26, 2015
        ('kersCharge', c_float),
        ('kersInput', c_float),
        ('autoShifterOn', c_int32),
        ('rideHeight', c_float * 2),
    ]


class SPageFileGraphic(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('packetId', c_int32),
        ('status', AC_STATUS),
        ('session', AC_SESSION_TYPE),
        ('currentTime', c_wchar * 15),
        ('lastTime', c_wchar * 15),
        ('bestTime', c_wchar * 15),
        ('split', c_wchar * 15),
        ('completedLaps', c_int32),
        ('position', c_int32),
        ('iCurrentTime', c_int32),
        ('iLastTime', c_int32),
        ('iBestTime', c_int32),
        ('sessionTimeLeft', c_float),
        ('distanceTraveled', c_float),
        ('isInPit', c_int32),
        ('currentSectorIndex', c_int32),
        ('lastSectorTime', c_int32),
        ('numberOfLaps', c_int32),
        ('tyreCompound', c_wchar * 33),

        ('replayTimeMultiplier', c_float),
        ('normalizedCarPosition', c_float),
        ('carCoordinates', c_float * 3),

        # Added on Oct 26, 2015
        ('penaltyTime', c_float),
        ('flag', AC_FLAG_TYPE),
        ('idealLineOn', c_int32),
    ]


class SPageFileStatic(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('_smVersion', c_wchar * 15),
        ('_acVersion', c_wchar * 15),
        # session static info
        ('numberOfSessions', c_int32),
        ('numCars', c_int32),
        ('carModel', c_wchar * 33),
        ('track', c_wchar * 33),
        ('playerName', c_wchar * 33),
        ('playerSurname', c_wchar * 33),
        ('playerNick', c_wchar * 33),
        ('sectorCount', c_int32),

        # car static info
        ('maxTorque', c_float),
        ('maxPower', c_float),
        ('maxRpm', c_int32),
        ('maxFuel', c_float),
        ('suspensionMaxTravel', c_float * 4),
        ('tyreRadius', c_float * 4),
    ]


class SimInfo:
    def __init__(self):
        self._acpmf_physics = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "acpmf_physics")
        self._acpmf_graphics = mmap.mmap(0, ctypes.sizeof(SPageFileGraphic), "acpmf_graphics")
        self._acpmf_static = mmap.mmap(0, ctypes.sizeof(SPageFileStatic), "acpmf_static")
        self.physics = SPageFilePhysics.from_buffer(self._acpmf_physics)
        self.graphics = SPageFileGraphic.from_buffer(self._acpmf_graphics)
        self.static = SPageFileStatic.from_buffer(self._acpmf_static)

    def close(self):
        self._acpmf_physics.close()
        self._acpmf_graphics.close()
        self._acpmf_static.close()

    def __del__(self):
        self.close()

info = SimInfo()


def demo():
    import time

    for _ in range(400):
        print(info.static.track, info.graphics.tyreCompound, info.graphics.currentTime,
              info.physics.rpms, info.graphics.currentTime, info.static.maxRpm, list(info.physics.tyreWear))
        time.sleep(0.1)


def do_test():
    for struct in info.static, info.graphics, info.physics:
        print(struct.__class__.__name__)
        for field, type_spec in struct._fields_:
            value = getattr(struct, field)
            if not isinstance(value, (str, float, int)):
                value = list(value)
            print(" {} -> {} {}".format(field, type(value), value))


if __name__ == '__main__':
    do_test()
    demo()
