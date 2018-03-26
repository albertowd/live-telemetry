#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decrypt and extract information files about a car.
Big thanks for aluigi@ZenHaxs.com that have the patience to help me to open the ACD files.

@author: albertowd
"""

from collections import OrderedDict
import configparser
from struct import unpack

from lib.lt_util import log, WheelPos


class ACD(object):
    """ Stores the ACD file contents. """

    def __init__(self, path):
        """ Default constructor receives the ACD file path. """
        path_v = path.split("/")
        
        # Initiate the class fields.
        self.__car = path_v[-2]
        self.__content = bytearray()
        self.__files = OrderedDict()
        self.__key = generate_key(self.__car)
        
        # Read all the file into memory.
        with open(path, "rb") as rb:
            self.__content = bytearray(rb.read())
            self.__content_size = len(self.__content)
        
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
            file_name = self.__content[offset:offset + name_size].decode("utf8")
            offset += name_size
            
            # File size.
            file_size = unpack("L", self.__content[offset:offset + 4])[0]
            offset += 4
            
            # Get the content and slices each 4 bytes.
            packed_content = self.__content[offset:offset + file_size * 4][::4]
            offset += file_size * 4
            
            # Decrypt the content of the file.
            decrypted_content = ""
            key_size = len(self.__key)
            for i in range(file_size):
                code = packed_content[i] - ord(self.__key[i % key_size])
                decrypted_content += chr(code)
            
            # Save the decrypted file.
            self.set_file(decrypted_content, file_name)
    
    def get_file(self, name):
        """ Returns the content of an inner file. """
        if name in self.__files:
            return self.__files[name]
        else:
            return ""
    
    def get_ideal_pressure(self, compound, wheel):
        """ Returns the compound ideal pressure. """
        config = configparser.ConfigParser(empty_lines_in_values=False, inline_comment_prefixes=(';',))
        config.read_string(self.get_file("tyres.ini"))
        
        name = get_tyre_name(compound, config, wheel)
        return float(config[name]["PRESSURE_IDEAL"])
    
    def get_power_curve(self):
        """ Returns the rpm x power curve. """
        config = configparser.ConfigParser(empty_lines_in_values=False, inline_comment_prefixes=(';',))
        config.read_string(self.get_file("engine.ini"))
        
        return self.get_file(config["HEADER"]["POWER_CURVE"])
    
    def get_temp_curve(self, compound, wheel):
        """ Returns the compound temperature grip curve. """
        config = configparser.ConfigParser(empty_lines_in_values=False, inline_comment_prefixes=(';',))
        config.read_string(self.get_file("tyres.ini"))
        
        name = "THERMAL_{}".format(get_tyre_name(compound, config, wheel))
        return self.get_file(config[name]["PERFORMANCE_CURVE"])

    def get_wear_curve(self, compound, wheel):
        """ Returns the compound wear curve. """
        config = configparser.ConfigParser(empty_lines_in_values=False, inline_comment_prefixes=(';',))
        config.read_string(self.get_file("tyres.ini"))
        
        name = get_tyre_name(compound, config, wheel)
        return self.get_file(config[name]["WEAR_CURVE"])
    
    def set_file(self, content, name):
        """ Sets a new content to an inner file. """
        self.__files[name] = content
    
    def __str__(self):
        """ Just print some useful information. """
        info = "Car: {} - {}kb\n".format(self.__car, self.__content_size // 1024)
        info += "Key: {}\nFiles:\n".format(self.__key)
        for name in self.__files:
            info += "   {} - {}b\n".format(name, len(self.__files[name]))
        return info


def generate_key(car_name):
    """ Generates the 8 values key from the car name. """
    i = 0
    key1 = 0;
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
    key4 = 0x1683;
    while i < len(car_name):
        key4 -= ord(car_name[i])
        i += 1
    key4 &= 0xff
    
    i = 1
    key5 = 0x42;
    while i < len(car_name) - 4:
        tmp = (ord(car_name[i]) + 0xf) * key5
        i -= 1
        key5 = (ord(car_name[i]) + 0xf) * tmp + 0x16
        i += 5
    key5 &= 0xff
    
    i = 0
    key6 = 0x65;
    while i < len(car_name) - 2:
        key6 -= ord(car_name[i])
        i += 2
    key6 &= 0xff
    
    i = 0
    key7 = 0xab;
    while i < len(car_name) - 2:
        key7 %= ord(car_name[i])
        i += 2
    key7 &= 0xff
    
    i = 0
    key8 = 0xab;
    while i < len(car_name) - 1:
        key8 = int(key8 / ord(car_name[i])) + ord(car_name[i + 1])
        i += 1
    key8 &= 0xff
    
    return "{}-{}-{}-{}-{}-{}-{}-{}".format(key1, key2, key3, key4, key5, key6, key7, key8)


def get_tyre_name(compound, config, wheel):
    """ Returns the compound session name on the tyre.ini configuration file. """
    prefix = "FRONT{}" if wheel.is_front() else "REAR{}"
    
    for i in range(10):
        name = prefix.format("" if i == 0 else "_{}".format(i))
        if config[name]["SHORT_NAME"] == compound:
            return name
    
    i = config["COMPOUND_DEFAULT"]["INDEX"]
    return prefix.format("" if i == 0 else "_{}".format(i))


if __name__ == "__main__":
    acd = ACD("D:/Program Files (x86)/Steam/steamapps/common/assettocorsa/content/cars/abarth500/data.acd")
    log(acd)
    log("Ideal Pressures:\nFL: {}\tFR: {}\nRL: {}\tRR: {}\n".format(acd.get_ideal_pressure("SM", WheelPos(0)), acd.get_ideal_pressure("SM", WheelPos(1)), acd.get_ideal_pressure("SM", WheelPos(2)), acd.get_ideal_pressure("SM", WheelPos(3))))
    log("Temp Curve FL:\n{}\n".format(acd.get_temp_curve("SM", WheelPos(0))))
    log("Wear Curve FL:\n{}\n".format(acd.get_wear_curve("SM", WheelPos(0))))
    log("Power Curve:\n{}\n".format(acd.get_power_curve()))
