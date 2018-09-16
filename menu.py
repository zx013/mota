#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zzy
"""
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout

from setting import Setting
from cache import Texture


class Menu(FloatLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(size=(Texture.size * Setting.row_show, Texture.size * Setting.col_show), size_hint=(None, None), **kwargs)

        self.main()

    def main(self):
        label_list = []

        title_length = len(Setting.title)
        x_step = Setting.title_width / (title_length - 1)
        r = Setting.title_radius
        for n, c in enumerate(Setting.title):
            x = - Setting.title_width / 2 + n * x_step
            y = 7 + (r ** 2 - x ** 2) ** 0.5 - (r ** 2 - 14 ** 2) ** 0.5
            label_list.append(self.add_label(x, y, c, 8))

        version = ' '.join([c for c in Setting.version])
        label_list.append(self.add_label(0, 6, version, 4))

        label_list.append(self.add_label(0, 0, '开 始', 6))
        label_list.append(self.add_label(0, -7, '设 置', 6))

        return label_list

    def add_label(self, x, y, text='', font_size=4):
        label = Label(text=text, pos=(x * Setting.size, y * Setting.size), font_name=Setting.font_path, font_size=font_size * Setting.size)
        self.add_widget(label)
        return label

    def on_touch_down(self, touch):
        print(touch)