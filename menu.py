#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zzy
"""
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

from setting import Setting
from cache import Texture

with open('menu.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())


class MenuManager(ScreenManager): pass

class MenuMain(Screen): pass
class MenuSetting(Screen): pass
class MenuBattle(Screen): pass

class MenuLabel(ToggleButtonBehavior, Label): pass

class Menu(FloatLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        
        self.label = {}
        self.menu = {}
        self.option = {}
        self.current = None

        self.main()
        #self.add_menu('main')
        #self.add_menu('difficult')
        #self.add_menu('setting')
        #self.choice_menu('main')


    def main(self):
        for n, c in enumerate(Setting.title):
            label = MenuButton(idx=self.title_x[n], idy=self.title_y[n], text=c, fsize=8)
            self.add_widget(label)

    def difficult(self):
        label_list = []
        menu_list = []

        checkbox = CheckBox(group='1', pos_hint={'center_x': 0.2, 'center_y': 0.2}, color=(1, 1, 0, 1))
        self.add_widget(checkbox)
        
        checkbox = CheckBox(group='1', pos_hint={'center_x': 0.5, 'center_y': 0.2}, color=(1, 1, 0, 1))
        self.add_widget(checkbox)
        
        checkbox = CheckBox(group='1', pos_hint={'center_x': 0.8, 'center_y': 0.2}, color=(1, 1, 0, 1))
        self.add_widget(checkbox)

        return label_list, menu_list


    def setting(self):
        label_list = []
        menu_list = []

        label = self.add_label(0, 0, '难 度', 6)
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, 0, '层 数', 6)
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, 0, '大 小', 6)
        label_list.append(label)
        menu_list.append(label)
        
        label = self.add_label(0, 0, '显 示', 6)
        label_list.append(label)
        menu_list.append(label)

        return label_list, menu_list


    def choice_menu(self, menu):
        if self.current:
            label_list = self.label[self.current]
            for label in label_list:
                label.opacity = 0
        if menu:
            label_list = self.label[menu]
            for label in label_list:
                label.opacity = 1
        self.current = menu

    def add_menu(self, menu):
        func = getattr(self, menu)
        label_list, menu_list = func()
        self.label[menu] = label_list
        self.menu[menu] = menu_list
        self.option[menu] = -1
        self.current = menu
        for label in label_list:
            label.opacity = 0

    def add_label(self, x, y, text='', font_size=4):
        x = x * Setting.size / self.width + 0.5
        y = y * Setting.size / self.height + 0.5
        length = sum([1 if c.isalpha() else 0.5 for c in text])
        size = (length * font_size * Setting.size, font_size * Setting.size)
        label = Label(text=text, pos_hint={'center_x': x, 'center_y': y}, size=size, size_hint=(None, None), font_name=Setting.font_path, font_size=font_size * Setting.size)
        self.add_widget(label)
        return label


    def key_down(self, key):
        print('menu key')
        if key in ('up', 'down', 'left', 'right'):
            pass

    def touch_down(self, x, y):
        return

        current = self.current
        menu_list = self.menu[current]

        for menu in menu_list:
            menu.color = (1, 1, 1, 1)
            self.option[current] = -1
        for index, menu in enumerate(menu_list):
            if menu.collide_point(x, y):
                menu.color = (1, 1, 0, 1)
                self.option[current] = index
                break

    def touch_up(self, x, y):
        return

        current = self.current
        if not current:
            return False
        index = self.option[current]
        if index < 0:
            return False
        menu_list = self.menu[current]
        menu = menu_list[index]
        if menu.collide_point(x, y):
            if hasattr(menu, 'menu'):
                self.choice_menu(menu.menu)
            if hasattr(menu, 'difficult'):
                Setting.difficult_type = menu.difficult
        else:
            menu.color = (1, 1, 1, 1)
            self.option[current] = -1

from kivy.app import App
class MenuTest(App):
    def build(self):
        self.menu = MenuManager()
        return self.menu


if __name__ == '__main__':
    menu = MenuTest()
    menu.run()
