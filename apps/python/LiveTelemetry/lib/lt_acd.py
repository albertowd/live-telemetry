#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decrypt and extract information files about a car.
Big thanks for aluigi@ZenHaxs.com that have the patience to help me to open the ACD files.

@author: albertowd
"""

from collections import OrderedDict
from configparser import ConfigParser
from struct import unpack
from sys import exc_info
import os

from lib.lt_util import log


class ACD(object):
    """ Stores the ACD file contents. """

    def __init__(self, path):
        """ Default constructor receives the ACD file path. """
        path_v = path.split("/")

        # Initiate the class fields.
        self.__car = path_v[-1]
        self.__content = bytearray()
        self.__content_size = len(self.__content)
        self.__files = OrderedDict()
        self.__key = generate_key(self.__car)

        # Verify if the data.acd exists to load car information.
        data_acd_path = "{}/data.acd".format(path)
        if os.path.isfile(data_acd_path):
            log("Loading from data.acd...")
            self.__load_from_file(data_acd_path)
        else:
            # If it don't, try to load from data folder.
            log("Loading from data folder...")
            self.__load_from_folder("{}/data".format(path))

    def __load_from_file(self, path):
        """ Loads the car information by the data.acd encrypted file. """

        # Read all the file into memory.
        try:
            with open(path, "rb") as rb:
                self.__content = bytearray(rb.read())
                self.__content_size = len(self.__content)
        except:
            log("Failed to open file {}:".format(path))
            for info in exc_info():
                log(info)

        if self.__content_size > 8:
            # Verify the "version" of the file.
            offset = 0
            dummy = unpack("l", self.__content[offset:offset + 4])[0]
            offset += 4
            if dummy < 0:
                # New cars, just pass the first 8 bytes.
                dummy = unpack("L", self.__content[offset:offset + 4])[0]
                offset += 4
            else:
                # Old cars don't have any version.
                offset = 0

            # Parse each inner file.
            while offset < self.__content_size:
                # Size of the file name.
                name_size = unpack("L", self.__content[offset:offset + 4])[0]
                offset += 4

                # File name.
                file_name = self.__content[offset:offset +
                                           name_size].decode("utf8")
                offset += name_size
                log(file_name)

                # File size.
                file_size = unpack("L", self.__content[offset:offset + 4])[0]
                offset += 4

                # Get the content and slices each 4 bytes.
                packed_content = self.__content[offset:offset +
                                                file_size * 4][::4]
                offset += file_size * 4

                # Decrypt the content of the file.
                decrypted_content = ""
                key_size = len(self.__key)
                for i in range(file_size):
                    code = packed_content[i] - ord(self.__key[i % key_size])
                    decrypted_content += chr(code)

                # Save the decrypted file.
                self.set_file(decrypted_content, file_name)
        elif self.__content_size > 0:
            log("File too small to decrypt: {} bytes.".format(self.__content_size))

    def __load_from_folder(self, path):
        """ Loads the car information by the data folder. """
        for file_name in os.listdir(path):
            file_path = "{}/{}".format(path, file_name)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as r:
                        self.set_file(r.read(), file_name)
                except:
                    log("Failed to open file {}:".format(file_name))
                    for info in exc_info():
                        log(info)

    def __str__(self):
        """ Just print some useful information. """
        info = "Car: {} - {}kb\n".format(self.__car,
                                         self.__content_size // 1024)
        info += "Key: {}\nFiles:\n".format(self.__key)
        for name in self.__files:
            info += "   {} - {}b\n".format(name, len(self.__files[name]))
        return info

    def get_file(self, name):
        """ Returns the content of an inner file. """
        if name in self.__files:
            return self.__files[name]
        else:
            return ""

    def get_ideal_pressure(self, compound, wheel):
        """ Returns the compound ideal pressure. """
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("tyres.ini"))

        try:
            name = get_tire_name(compound, config, wheel)
            return float(config[name]["PRESSURE_IDEAL"])
        except:
            log("Failed to get tire ideal pressure:")
            for info in exc_info():
                log(info)
            raise

    def get_power_curve(self):
        """ Returns the rpm x power curve. """
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("engine.ini"))

        try:
            return self.get_file(config["HEADER"]["POWER_CURVE"])
        except:
            log("Failed to get rpm power curve:")
            for info in exc_info():
                log(info)
            raise

    def get_rpm_downshift(self):
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("drivetrain.ini"))
        try:
            return float(config["AUTO_SHIFTER"]["DOWN"])
        except:
            log("Failed to get rpm downshift value:")
            for info in exc_info():
                log(info)
            raise

    def get_rpm_damage(self):
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("engine.ini"))
        try:
            if config.has_option("DAMAGE", "RPM_THRESHOLD"):
                res = config["DAMAGE"]["RPM_THRESHOLD"]
            else:
                res = self.get_rpm_limiter() + 100
            return float(res)
        except:
            log("Failed to get rpm damage value:")
            for info in exc_info():
                log(info)
            raise

    def get_rpm_limiter(self):
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("engine.ini"))
        try:
            return float(config["ENGINE_DATA"]["LIMITER"])
        except:
            log("Failed to get rpm limiter value:")
            for info in exc_info():
                log(info)
            raise

    def get_rpm_upshift(self):
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("drivetrain.ini"))
        try:
            return float(config["AUTO_SHIFTER"]["UP"])
        except:
            log("Failed to get rpm upshit value:")
            for info in exc_info():
                log(info)
            raise

    def get_temp_curve(self, compound, wheel):
        """ Returns the compound temperature grip curve. """
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("tyres.ini"))

        try:
            name = "THERMAL_{}".format(get_tire_name(compound, config, wheel))
            return self.get_file(config[name]["PERFORMANCE_CURVE"])
        except:
            log("Failed to get tire temperature curve {}:".format(compound))
            for info in exc_info():
                log(info)
            raise

    def get_wear_curve(self, compound, wheel):
        """ Returns the compound wear curve. """
        config = ConfigParser(
            empty_lines_in_values=False, inline_comment_prefixes=(";",))
        config.read_string(self.get_file("tyres.ini"))

        try:
            name = get_tire_name(compound, config, wheel)
            return self.get_file(config[name]["WEAR_CURVE"])
        except:
            log("Failed to get tire wear curve {}:".format(compound))
            for info in exc_info():
                log(info)
            raise

    def set_file(self, content, name):
        """ Sets a new content to an inner file. """
        self.__files[name] = content


def generate_key(car_name):
    """ Generates the 8 values key from the car name. """
    i = 0
    key1 = 0
    while i < len(car_name):
        key1 += ord(car_name[i])
        i += 1
    key1 &= 0xff

    i = 0
    key2 = 0
    while i < len(car_name) - 1:
        key2 *= ord(car_name[i])
        i += 1
        key2 -= ord(car_name[i])
        i += 1
    key2 &= 0xff

    i = 1
    key3 = 0
    while i < len(car_name) - 3:
        key3 *= ord(car_name[i])
        i += 1
        key3 = int(key3 / (ord(car_name[i]) + 0x1b))
        i -= 2
        key3 += -0x1b - ord(car_name[i])
        i += 4
    key3 &= 0xff

    i = 1
    key4 = 0x1683
    while i < len(car_name):
        key4 -= ord(car_name[i])
        i += 1
    key4 &= 0xff

    i = 1
    key5 = 0x42
    while i < len(car_name) - 4:
        tmp = (ord(car_name[i]) + 0xf) * key5
        i -= 1
        key5 = (ord(car_name[i]) + 0xf) * tmp + 0x16
        i += 5
    key5 &= 0xff

    i = 0
    key6 = 0x65
    while i < len(car_name) - 2:
        key6 -= ord(car_name[i])
        i += 2
    key6 &= 0xff

    i = 0
    key7 = 0xab
    while i < len(car_name) - 2:
        key7 %= ord(car_name[i])
        i += 2
    key7 &= 0xff

    i = 0
    key8 = 0xab
    while i < len(car_name) - 1:
        key8 = int(key8 / ord(car_name[i])) + ord(car_name[i + 1])
        i += 1
    key8 &= 0xff

    return "{}-{}-{}-{}-{}-{}-{}-{}".format(key1, key2, key3, key4, key5, key6, key7, key8)


def get_tire_name(compound, config, wheel):
    """ Returns the compound session name on the tire.ini configuration file. """
    prefix = "FRONT{}" if wheel.is_front() else "REAR{}"

    for i in range(10):
        name = prefix.format("" if i == 0 else "_{}".format(i))
        # Check if the SHORT_NAME index exists for tire backward compatibility.
        if config.has_option(name, "SHORT_NAME") and config[name]["SHORT_NAME"] == compound:
            return name

    try:
        i = int(config["COMPOUND_DEFAULT"]["INDEX"])
        return prefix.format("" if i == 0 else "_{}".format(i))
    except:
        log("Failed to get tire name {}:".format(compound))
        for info in exc_info():
            log(info)
        raise
