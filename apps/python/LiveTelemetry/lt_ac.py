#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fake AC API import to run tests.

@author: albertowd
"""


class ac(object):

    @staticmethod
    def addButton(name):
        pass

    @staticmethod
    def console(msg=""):
        print(msg)
    
    @staticmethod
    def drawBorder(component_id, draw):
        pass
    
    @staticmethod
    def setFontAlignment(component_id, align):
        pass
    
    @staticmethod
    def getPosition(component_id):
        pass
    
    @staticmethod
    def glBegin(primitive):
        pass
    
    @staticmethod
    def glColor4f(r, g, b, a):
        pass
    
    @staticmethod
    def glEnd():
        pass
    
    @staticmethod
    def glQuad(x, y, w, h):
        pass
    
    @staticmethod
    def glQuadTextured(x, y, w, h, texture_id):
        pass
    
    @staticmethod
    def glVertex2f(x, y):
        pass
    
    @staticmethod
    def log(msg=""):
        pass
    
    @staticmethod
    def newApp(name):
        pass
    
    @staticmethod
    def setBackgroundColor(component_id, r, g, b):
        pass
    
    @staticmethod
    def setBackgroundOpacity(component_id, a):
        pass
    
    @staticmethod
    def setIconPosition(window_id, x, y):
        pass
    
    @staticmethod
    def setPosition(component_id, x, y):
        pass
    
    @staticmethod
    def setSize(component_id, w, h):
        pass
    
    @staticmethod
    def setText(component_id, text):
        pass
    
    @staticmethod
    def setTitle(window_id, title):
        pass


class acsys(object):

    class GL(object):
        
        Quads = 3
