#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.lang import Builder

from setting import Setting, MazeBase
from cache import Config
from maze import gmaze

from random import random

with open('menu.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())


class MenuLabel(ToggleButtonBehavior, Label): pass
class MenuImage(ToggleButtonBehavior, FloatLayout):
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if not touch.is_double_tap:
            for image in self.parent.children:
                image.selected = False
            self.selected = True
        else:
            opened = self.opened
            for image in self.parent.children:
                image.opened = False
                image.exit += 1
            if not opened:
                self.enter += 1
                if self.used:
                    herostate = gmaze.herostate
                    used = True
                    for key, data in self.attribute.items():
                        if key == 'key':
                            for k, v in data.items():
                                if herostate.key[k] + v < 0:
                                    used = False
                        else:
                            if getattr(herostate, key) + data < 0:
                                used = False
                    if used:
                        for key, data in self.attribute.items():
                            if key == 'key':
                                for k, v in data.items():
                                    herostate.key[k] += v
                            else:
                                setattr(herostate, key, getattr(herostate, key) + data)
                        self.number -= 1
                        if self.number == 0:
                            self.parent.remove_widget(self)
        return True

class MenuWelcomeLabel(MenuLabel):
    def __init__(self, **kwargs):
        super(MenuWelcomeLabel, self).__init__(**kwargs)
        self.pos = (Setting.row_size, 0)
        self.text = Setting.status_text

        offset = Setting.row_size + self.texture_size[0]
        anim = Animation(x=-offset, duration=offset / Setting.status_speed) + Animation(x=0, duration=0)
        anim.repeat = True
        anim.start(self)

class MenuStatusLabel(MenuLabel):
    def __init__(self, **kwargs):
        super(MenuStatusLabel, self).__init__(**kwargs)
        self.anim = None

    def update(self, text):
        self.pos = (0, 0)
        self.pos_hint = {}
        self.text = text
        self.color = (0.5 + random() / 2, 0.5 + random() / 2, 0.5 + random() / 2, 1)
        self.texture_update()
        offset = self.texture_size[0] - Setting.col_size + Setting.pos_real
        if offset < 0:
            offset = 0
        if self.anim:
            self.anim.cancel(self)
        self.anim = Animation(x=0) + Animation(x=-offset, duration=offset / Setting.status_speed) + Animation(x=-offset) + Animation(x=0, duration=0)
        self.anim.repeat = True
        self.anim.start(self)

class MenuItemBoard(GridLayout):
    def __init__(self, **kwargs):
        super(MenuItemBoard, self).__init__(**kwargs)

class MenuShop(FloatLayout):
    def __init__(self, **kwargs):
        super(MenuShop, self).__init__(**kwargs)
        #python3中似乎是按顺序的
        self.item_info = {'gem-attack-small': {'number': 10, 'price': 20}, 'gem-attack-big': {'number': 3, 'price': 50}, 'gem-defence-small': {'number': 8, 'price': 15}, 'gem-defence-big': {'number': 5, 'price': 40}, 'sword-silver': {'number': 1, 'price': 150}, 'potion-red': {'number': 20, 'price': 10}, 'key-yellow': {'number': 3, 'price': 20}}
        self.select = None

    def update(self):
        for name, info in self.item_info.items():
            if 'image' not in info:
                image = MenuImage()
                self.board.add_widget(image)
                info['image'] = image
            else:
                image = info['image']
            image.name = name
            image.number = info.get('number', 1)
            image.price = info['price']
            image.used = True
            image.attribute = MazeBase.get_attribute(name)
            image.attribute['gold'] = -info['price']

class MenuLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MenuLayout, self).__init__(**kwargs)


#三行分别为7, 10, 10个中文字符
class MenuDialog(FloatLayout):
    l = 1.5 * Setting.multiple #线条宽度
    w = 0.4 * Setting.row_size + 2 * l #宽度
    h = 0.25 * Setting.col_size + 2 * l #高度

    dialog = []
    person = {}

    def on_touch_up(self, touch):
        if self.mota.operate:
            return False
        super(MenuDialog, self).on_touch_down(touch)
        if self.page_prev.collide_point(*touch.pos):
            return False
        if self.page_next.collide_point(*touch.pos):
            return False
        if self.page_enter.collide_point(*touch.pos):
            return False
        if self.page_exit.collide_point(*touch.pos):
            return False

        if self.page < len(self.pages) - 1:
            self.page += 1
            self.show()
        elif not self.update():
            self.dialog_end()
        return True

    def dialog_start(self, pos1, pos2, scene):
        self.mota.operate = False
        self.dialog = list(scene.dialog)
        self.person = {1: (pos1[0], pos1[1] - 3 * (pos2[1] - pos1[1]), pos1[2] - 3 * (pos2[2] - pos1[2])), 2: pos2}
        self.update()

    def dialog_end(self):
        self.idx = 128
        self.idy = 128
        self.opacity = 0
        self.mota.operate = True

    def update(self):
        if len(self.dialog) == 0:
            return False

        posd, text = self.dialog.pop(0)
        pos = self.person[posd]
        if posd == 1:
            self.role_label.text = '勇 者'
            self.role_image.name = self.mota.hero.name_show #texture = Texture.next(self.name)
        else:
            key = self.mota.get_key(pos)
            self.role_label.text = ' '.join(Config.config[key].get('name', '未知'))
            self.role_image.name = key
        z, x, y = pos
        self.idx = (y - Setting.size / 2) - 0.75
        self.idy = -(x - Setting.size / 2) + 0.75
        self.opacity = 1
        self.text = text
        self.page = 0
        self.split()
        self.show()
        return True

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

    def show(self):
        self.page_prev.color = self.page_prev.disabled_color if self.page_prev.disabled else self.page_prev.default_color
        self.page_next.color = self.page_next.disabled_color if self.page_next.disabled else self.page_next.default_color
        self.page_enter.color = self.page_enter.disabled_color if self.page_enter.disabled else self.page_enter.default_color
        self.page_exit.color = self.page_exit.default_color
