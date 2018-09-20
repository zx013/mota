# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout

from setting import Setting


class StateLabel(Label): pass
class StateImage(Image): pass

#简易显示，直接显示在边缘
#info配置中可设定配色方案
#如果有具体配置（color-xxx），则用具体配置，没有的话使用color的配置，如果color都没有设置，则设置为默认的白色
#配色的目的是为了状态值在墙的背景下能够清楚显示
class State(FloatLayout):
    def __init__(self, herostate, **kwargs):
        self.herostate = herostate
        self.row = Setting.row_show
        self.col = Setting.col_show
        self.label = {}
        super(State, self).__init__(**kwargs)

        self.herostate.active()

        self.health = [[None for j in range(self.row)] for i in range(self.col)]
        self.attack = [[None for j in range(self.row)] for i in range(self.col)]
        self.defence = [[None for j in range(self.row)] for i in range(self.col)]
        self.damage = [[None for j in range(self.row)] for i in range(self.col)]

        kwargs = {
            'font_size': 12 * Setting.multiple,
            'bold': True,
            'outline_width': Setting.multiple,
            'outline_color': (0.25, 0.25, 0.25)
        }
        for i in range(self.row):
            for j in range(self.col):
                label = Label(pos=(((i - self.row / 2 + 0.5) * Setting.pos_size) * Setting.multiple, ((j - self.col / 2 + 0.5) * Setting.pos_size + 14) * Setting.multiple), color=(1, 1, 0.5, 1), **kwargs)
                self.health[i][j] = label
                self.add_widget(label)

                label = Label(pos=(((i - self.row / 2 + 0.5) * Setting.pos_size - 12) * Setting.multiple, ((j - self.col / 2 + 0.5) * Setting.pos_size + 2) * Setting.multiple), color=(1, 0.5, 0.5, 1), **kwargs)
                self.attack[i][j] = label
                self.add_widget(label)

                label = Label(pos=(((i - self.row / 2 + 0.5) * Setting.pos_size + 12) * Setting.multiple, ((j - self.col / 2 + 0.5) * Setting.pos_size + 2) * Setting.multiple), color=(0.5, 0.5, 1, 1), **kwargs)
                self.defence[i][j] = label
                self.add_widget(label)

                label = Label(pos=(((i - self.row / 2 + 0.5) * Setting.pos_size) * Setting.multiple, ((j - self.col / 2 + 0.5) * Setting.pos_size - 10) * Setting.multiple), **kwargs)
                self.damage[i][j] = label
                self.add_widget(label)


    def real_pos(self, x, y):
        return y, self.col - x - 1

    #显示怪物的属性
    def set_health(self, x, y, health=''):
        x, y = self.real_pos(x, y)
        self.health[x][y].text = str(health)

    def set_attack(self, x, y, attack=''):
        x, y = self.real_pos(x, y)
        self.attack[x][y].text = str(attack)

    def set_defence(self, x, y, defence=''):
        x, y = self.real_pos(x, y)
        self.defence[x][y].text = str(defence)

    def set_damage(self, x, y, health, damage=-1):
        if health <= damage:
            color = (1, 0, 0, 1)
        else:
            color = (0, 1, 0, 1)
        if damage == float('inf'):
            text = '???'
        elif damage >= 0:
            text = str(damage)
        else:
            text = ''
        x, y = self.real_pos(x, y)
        self.damage[x][y].text = text
        self.damage[x][y].color = color

    def set_holy(self, x, y, holy):
        x, y = self.real_pos(x, y)
        self.damage[x][y].text = str(holy)
        self.damage[x][y].color = (0, 1, 0, 1)
