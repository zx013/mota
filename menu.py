#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zzy
"""
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

from setting import Setting
from cache import Texture

with open('menu.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())


class MenuLabel(Label): pass

class Menu(FloatLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(size=(Texture.size * Setting.row_show, Texture.size * Setting.col_show), size_hint=(None, None), **kwargs)
        
        self.label = {}
        self.menu = {}
        self.option = {}
        self.current = None

        self.add_menu('main')
        self.add_menu('difficult')
        self.add_menu('setting')
        self.choice_menu('main')


    def main(self):
        label_list = []
        menu_list = []

        title_length = len(Setting.title)
        x_step = Setting.title_width / (title_length - 1)
        r = Setting.title_radius
        for n, c in enumerate(Setting.title):
            x = - Setting.title_width / 2 + n * x_step
            y = 7 + (r ** 2 - x ** 2) ** 0.5 - (r ** 2 - 14 ** 2) ** 0.5
            label_list.append(self.add_label(x, y, c, 8))

        '''
        version = ' '.join([c for c in Setting.version])
        label_list.append(self.add_label(0, 6, version, 4))

        label = self.add_label(0, 0, '开 始', 6)
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, -7, '设 置', 6)
        label.menu = 'difficult'
        label_list.append(label)
        menu_list.append(label)
        '''

        return label_list, menu_list


    def difficult(self):
        label_list = []
        menu_list = []

        '''
        label = self.add_label(0, 10, '新 手', 4)
        label.difficult = 'very-easy'
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, 5, '简 单', 4)
        label.difficult = 'easy'
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, 0, '正 常', 4)
        label.difficult = 'normal'
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, -5, '困 难', 4)
        label.difficult = 'hard'
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, -10, '噩 梦', 4)
        label.difficult = 'very-hard'
        label_list.append(label)
        menu_list.append(label)

        label = self.add_label(0, -15, '返 回', 3)
        label.menu = 'main'
        label_list.append(label)
        menu_list.append(label)
        '''

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
