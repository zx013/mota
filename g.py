# -*- coding: utf-8 -*-
class Global:
    instance = None
    def __getattr__(self, name):
        if name == '__class__':
            return None
        if not hasattr(self.instance, name):
            return None
        attr = getattr(self.instance, name)
        return attr

    def __setattr__(self, name, value):
        if self.__dict__.get(name):
            return None
        self.__dict__[name] = value

if 'gmota' not in dir():
    gmota = Global()

if 'gmaze' not in dir():
    gmaze = Global()

if 'ginfo' not in dir():
    ginfo = Global()

if 'gstatusbar' not in dir():
    gstatusbar = Global()

if 'gprogress' not in dir():
    gprogress = Global()

if 'glayout' not in dir():
    glayout = Global()
