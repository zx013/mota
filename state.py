# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout

from setting import Setting, MazeBase
from cache import Config, Texture


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
        super(State, self).__init__(size=(Setting.row_size, Setting.col_size), size_hint=(None, None), **kwargs)

        self.health = [[None for j in range(self.row)] for i in range(self.col)]
        self.attack = [[None for j in range(self.row)] for i in range(self.col)]
        self.defence = [[None for j in range(self.row)] for i in range(self.col)]
        self.damage = [[None for j in range(self.row)] for i in range(self.col)]

        kwargs = {
            'font_size': 12,
            'bold': True,
            'outline_width': 1,
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


    def easy(self):
        self.label = {}

        label = self.add_label(0, - (self.col - 1) / 2, font_size=24)
        label.text = Setting.title
        self.label['title'] = label

        self.label['floor'] = self.add_label((self.row - 3) / 2, - (self.col - 1) / 2, bind='floor', font_size=24)

        self.label['health'] = self.add_label(0, (self.col - 1) / 2, offset=(0, 3), bind='health', font_size=28)

        self.add_image(- (self.row - 2.5) / 2, (self.col - 1.5) / 2, name='attack-16')
        self.label['attack'] = self.add_label(- (self.row - 3) / 2, (self.col - 1) / 2, offset=(0, 2), bind='attack', font_size=24, halign='left')

        self.add_image((self.row - 1.5) / 2, (self.col - 1.5) / 2, name='defence-16')
        self.label['defence'] = self.add_label((self.row - 3) / 2, (self.col - 1) / 2, offset=(0, 2), bind='defence', font_size=24, halign='right')

        self.label['key'] = {}
        self.add_image((self.row - 0.5) / 2, - (self.col - 9) / 2, name='key-yellow-16')
        self.label['key']['yellow'] = self.add_label((self.row - 1) / 2, - (self.col - 8.5) / 2, offset=(-1, 1), bind='key', key_color=MazeBase.Value.Color.yellow)

        self.add_image((self.row - 0.5) / 2, - (self.col - 7) / 2, name='key-blue-16')
        self.label['key']['blue'] = self.add_label((self.row - 1) / 2, - (self.col - 6.5) / 2, offset=(-1, 1), bind='key', key_color=MazeBase.Value.Color.blue)

        self.add_image((self.row - 0.5) / 2, - (self.col - 5) / 2, name='key-red-16')
        self.label['key']['red'] = self.add_label((self.row - 1) / 2, - (self.col - 4.5) / 2, offset=(-1, 1), bind='key', key_color=MazeBase.Value.Color.red)

        self.add_image((self.row - 0.5) / 2, - (self.col - 3) / 2, name='key-green-16')
        self.label['key']['green'] = self.add_label((self.row - 1) / 2, - (self.col - 2.5) / 2, offset=(-1, 1), bind='key', key_color=MazeBase.Value.Color.green)


    #offset用来微调
    def add_label(self, x, y, offset=(0, 0), bind='', key_color=None, font_size=20, halign='center', color=(1, 1, 1, 1)):
        offset_x, offset_y = offset
        label = Label(pos=((x * Setting.pos_size + offset_x) * Setting.multiple, (y * Setting.pos_size + offset_y) * Setting.multiple), font_name=Setting.font_path, font_size=font_size * Setting.multiple, halign=halign, color=color, outline_width=Setting.multiple, outline_color=(0.25, 0.25, 0.25))
        if bind:
            if bind == 'key':
                self.herostate.key.bind(key_color, label)
            else:
                self.herostate.bind(bind, label)
        self.add_widget(label)
        return label

    def add_image(self, x, y, offset=(0, 0), name=''):
        offset_x, offset_y = offset
        image = Image(pos=((x * Setting.pos_size + offset_x) * Setting.multiple, (y * Setting.pos_size + offset_y) * Setting.multiple))
        image.texture = Texture.next(name)
        self.add_widget(image)
        return image


    #设置状态栏的颜色
    def set_color(self, wall):
        default = {
            'title': (1, 1, 1, 1),
            'floor': (1, 1, 1, 1),
            'health': (0.5, 1, 0.5, 1),
            'attack': (1, 0.5, 0.5, 1),
            'defence': (0.5, 0.5, 1, 1),
            'key': (1, 1, 0.5, 1)
        }

        color = {}
        for key, val in Config.config[wall].items():
            if 'color' not in key:
                continue
            if '-' in key:
                key = key.split('-')[1]
            color[key] = val

        for key, val in self.label.items():
            if key != 'key':
                val.color = color.get(key, color.get('color', default[key]))
                continue
            for k, v in val.items():
                v.color = color.get(key, color.get('color', default[key]))

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
