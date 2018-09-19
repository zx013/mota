#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zzy
"""
from kivy.uix.label import Label
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

from kivy.uix.progressbar import ProgressBar

with open('menu.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())


class MenuManager(ScreenManager): pass

class MenuLabel(ToggleButtonBehavior, Label): pass
class MenuParameter(FloatLayout): pass
class MenuSetting(FloatLayout): pass

from kivy.app import App
class MenuTest(App):
    def build(self):
        self.menu = MenuManager()
        return self.menu


if __name__ == '__main__':
    menu = MenuTest()
    menu.run()
