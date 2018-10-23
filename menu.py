#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from setting import Setting

with open('menu.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())

class MenuManager(ScreenManager): pass

class MenuLabel(ToggleButtonBehavior, Label): pass
class MenuImage(Image): pass
class MenuParameter(FloatLayout): pass
class MenuSetting(FloatLayout): pass
class MenuMonster(FloatLayout): pass
class MenuMonsterManual(FloatLayout): pass

#三行分别为7, 10, 10个中文字符
class MenuDialog(FloatLayout):
    def dialog(self, pos1, pos2):
        print(pos1, pos2)
        self.update(pos1, '好的。')

    def update(self, pos, text):
        z, x, y = pos
        self.idx = 1.5 * (y - Setting.size / 2) - 0.75
        self.idy = -1.0 * (x - Setting.size / 2) + 0.75
        self.text = text
        self.page = 0
        self.page_prev.color = self.page_prev.disabled_color if self.page_prev.disabled else self.page_prev.default_color
        self.page_next.color = self.page_next.disabled_color if self.page_next.disabled else self.page_next.default_color
        self.page_exit.color = self.page_exit.default_color
        self.split()

    def split(self):
        text = self.text
        pages = []

        while text:
            lines = []
            for w in (14, 20, 20):
                line = ''
                length = 0
                while len(text) > 1:
                    ps = text[0]
                    ns = text[1]
                    pslen = len(ps.encode('gbk'))
                    nslen = len(ns.encode('gbk'))
                    if length + pslen <= w and length + pslen + nslen > w and ns in ('，', '。', '？', '！', '：', '、', '；'):
                        break
                    if length <= w and length + pslen > w:
                        break
                    line += ps
                    length += pslen
                    text = text[1:]
                else:
                    line += text
                    length += sum([len(s.encode('gbk')) for s in text])
                    text = ''
                line += 2 * (w - length) * ' '
                lines.append(line)
            pages.append(lines)

        if not pages:
            pages = [['', '', '']]
        self.pages = pages
