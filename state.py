# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout

from setting import MazeBase
from cache import Setting, Texture


#简易显示，直接显示在边缘
class State(FloatLayout):
    def __init__(self, herostate, row, col, **kwargs):
        self.herostate = herostate
        self.row = row
        self.col = col
        super(State, self).__init__(size=(Texture.size * self.row, Texture.size * self.col), size_hint=(None, None), **kwargs)

    def easy(self):
        label = self.add_label(0, - (self.col - 1) / 2, font_size=24)
        label.text = Setting.title

        self.add_label((self.row - 3) / 2, - (self.col - 1) / 2, bind='floor', font_size=24)

        self.add_label(0, (self.col - 1) / 2, bind='health', font_size=28)

        self.add_image(- (self.row - 2.5) / 2, (self.col - 1.5) / 2, name='attack-16')
        self.add_label(- (self.row - 3) / 2, (self.col - 1) / 2, bind='attack', font_size=24)

        self.add_image((self.row - 1.5) / 2, (self.col - 1.5) / 2, name='defence-16')
        self.add_label((self.row - 3) / 2, (self.col - 1) / 2, bind='defence', font_size=24)

        self.add_image((self.row - 0.5) / 2, - (self.col - 9) / 2, name='key-yellow-16')
        self.add_label((self.row - 1) / 2, - (self.col - 8.5) / 2, offset=(-1, 1), bind='key', color=MazeBase.Value.Color.yellow)

        self.add_image((self.row - 0.5) / 2, - (self.col - 7) / 2, name='key-blue-16')
        self.add_label((self.row - 1) / 2, - (self.col - 6.5) / 2, offset=(-1, 1), bind='key', color=MazeBase.Value.Color.blue)

        self.add_image((self.row - 0.5) / 2, - (self.col - 5) / 2, name='key-red-16')
        self.add_label((self.row - 1) / 2, - (self.col - 4.5) / 2, offset=(-1, 1), bind='key', color=MazeBase.Value.Color.red)

        self.add_image((self.row - 0.5) / 2, - (self.col - 3) / 2, name='key-green-16')
        self.add_label((self.row - 1) / 2, - (self.col - 2.5) / 2, offset=(-1, 1), bind='key', color=MazeBase.Value.Color.green)

    #offset用来微调
    def add_label(self, x, y, offset=(0, 0), bind='', color=None, font_size=20):
        offset_x, offset_y = offset
        label = Label(pos=(x * Texture.size + offset_x, y * Texture.size + offset_y), font_name=Setting.font_path, font_size=font_size)
        if bind:
            if bind == 'key':
                self.herostate.key.bind(color, label)
            else:
                self.herostate.bind(bind, label)
        self.add_widget(label)
        return label

    def add_image(self, x, y, offset=(0, 0), name=''):
        offset_x, offset_y = offset
        image = Image(pos=(x * Texture.size + offset_x, y * Texture.size + offset_y))
        image.texture = Texture.next(name)
        self.add_widget(image)
        return image
