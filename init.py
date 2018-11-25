# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.clock import Clock

from menu import MenuLayout
from maze import Maze
from g import gmaze
gmaze.instance = Maze()

from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.graphics import Line
from kivy.graphics import Color
#from kivy.uix.progressbar import ProgressBar
from tools import Tools
from random import random
import math

from kivy.lang import Builder
Builder.load_string('''
#:import Setting setting.Setting
<Init1>:
    text: '测试init'
    font_size: 50
    multiple: 1
    Label:
        text: root.text
        font_size: root.font_size
        font_name: Setting.font_path
        color: (1, 1, 1, 1)
        outline_width: Setting.multiple
        outline_color: (0.25, 0.25, 0.25)
    Label:
        text: root.text
        font_size: root.font_size * root.multiple
        color: (1, 1, 0, 0.5)
        font_name: Setting.font_path
    #on_texture_size:
    #    print(self.text)
    #    self.load() if self.text == 'init' else None
<Init>:
    light: 0.6
    texture: Texture.next('init')
    y: (self.texture.height / self.texture.width * self.width - self.height) / 2
    allow_stretch: False
    canvas.before:
        Color:
            rgba: (1, 1, 1, self.light)
        Rectangle:
            pos: (0, 0)
            size: self.size
''')

class Init1(FloatLayout, ToggleButtonBehavior):
    def __init__(self, app=None, **kwargs):
        super(Init, self).__init__(**kwargs)
        self.app = app
        self.size = Window.size
        Clock.schedule_once(self.disperse, 0.05)

    def disperse(self, dt):
        self.multiple += 0.01
        if self.multiple > 1.1:
            self.multiple = 1
        Clock.schedule_once(self.disperse, 0.05)

#android不生效，原因不明
class Init(Image):
    def __init__(self, app=None, **kwargs):
        super(Init, self).__init__(**kwargs)
        self.app = app
        self.size = Window.size
        print(self.texture.size, self.size, self.texture.height, self.height)
        Clock.schedule_once(self.lightning)
        #self.load()

    def line_length(self, sx, sy, ex, ey):
        return math.sqrt((sx - ex) ** 2 + (sy - ey) ** 2)

    def get_line(self, sx, sy, ex, ey):
        offset = self.line_length(sx, sy, ex, ey) / 2
        if offset < 10:
            return [(sx, sy, ex, ey)]
        mx = (sx + ex) / 2
        my = (sy + ey) / 2
        mx += (random() - 0.5) * offset
        my += (random() - 0.5) * offset
        result = self.get_line(sx, sy, mx, my)
        result += self.get_line(mx, my, ex, ey)
        return result

    def get_points(self, line):
        points = []
        for sx, sy, ex, ey in line:
            points += [sx, sy]
        points += [ex, ey]
        return points

    def lightning(self, dt):
        self.canvas.after.clear()
        with self.canvas.after:
            self.light_color = Color(rgba=(1, 1, 1, 1))
            sx = (0.25 + 0.5 * random()) * self.width
            sy = self.height
            ex = (0.25 + 0.5 * random()) * self.width
            ey = 0
            line = self.get_line(sx, sy, ex, ey)
            Line(points=self.get_points(line), width=1.5)
            for ppoint, point in Tools.iter_previous(line):
                psx, psy, pex, pey = ppoint
                sx, sy, ex, ey = point
                if pey - psy > 0:
                    continue
                a = self.line_length(psx, psy, pex, pey)
                b = self.line_length(pex, pey, ex, ey)
                c = self.line_length(psx, psy, ex, ey)
                degrees = math.degrees(math.acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b)))
                if degrees > 120:
                    continue
                ny = (0.25 + 0.5 * random()) * pey
                nx = sx + (random() - 0.5) * pey
                line = self.get_line(sx, sy, nx, ny)
                Line(points=self.get_points(line), width=1)

        self.light_down()
        Clock.schedule_once(self.lightning, 5)

    def _light_down(self, dt):
        self.light = self.light * 0.95 - 0.001
        self.light_color.rgba = (1, 1, 1, self.light * 1.1)
        if self.light > 0:
            Clock.schedule_once(self._light_down, 0.05)

    def light_down(self):
        self.light = 1
        Clock.schedule_once(self._light_down, 0.05)

    def init(self, dt=0):
        app = self.app
        app.menu = MenuLayout()
        Window.remove_widget(app.root)
        app.root = app.menu
        Window.add_widget(app.root)

    def load(self, *args):
        Clock.schedule_once(self.init, 0)
