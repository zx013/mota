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
        if name == 'instance':
            if self.instance is None:
                self.__dict__[name] = value
        else:
            setattr(self.instance, name, value)

if 'gmota' not in dir():
    gmota = Global()

if 'gmaze' not in dir():
    gmaze = Global()

if 'gtask' not in dir():
    gtask = Global()
    
if 'ginfo' not in dir():
    ginfo = Global()

if 'gstatusbar' not in dir():
    gstatusbar = Global()

if 'gprogress' not in dir():
    gprogress = Global()

if 'glayout' not in dir():
    glayout = Global()
