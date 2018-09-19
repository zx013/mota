#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zzy
"""
from kivy.uix.label import Label
#from kivy.uix.scatter import Scatter
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

with open('menu.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())

class MenuManager(ScreenManager): pass

class MenuLabel(ToggleButtonBehavior, Label): pass
class MenuParameter(FloatLayout): pass
class MenuSetting(FloatLayout): pass
