# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 18:17:43 2018

@author: zx013
"""

'''
import sys
import platform
if platform.system().lower() == 'windows':
    from build import build
    build()
    sys.exit(0)
'''

#import jnius_config
#jnius_config.add_classpath('jars/javaclass.jar')
#from jnius import autoclass

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.clock import Clock
#python2应为from Configparser import ConfigParser

from cache import Cache
from maze import Maze, MazeSetting, MazeBase
from random import randint

'''
sometimes node is empty, that means we will get nothing in these area
长条形区域有时需要分割一下，不然显得太空旷
'''
class Layer(GridLayout):
    def __init__(self, row, col, **kwargs):
        self.row = row
        self.col = col
        super(Layer, self).__init__(rows=self.row, cols=self.col, size=(Cache.size * self.row, Cache.size * self.col), size_hint=(None, None), **kwargs)
        self.image = [[None for j in range(self.col)] for i in range(self.row)]
        self.texture = None #默认的texture

    def add(self, i, j, texture=None):
        self.texture = texture
        image = Image(size=(Cache.size, Cache.size), size_hint=(None, None))
        image.texture = texture
        self.image[i][j] = image
        self.add_widget(image)
        return image

class Hero:
    color = 'blue'
    key = 'down'
    old_pos = (1, 0, 0)
    pos = (1, 0, 0)
    action = set()
    weapon = 1

    def __init__(self, row, col, **kwargs):
        self.row = row
        self.col = col
        self.weapon = randint(1, 5)

    @property
    def name(self):
        return 'hero-{}-{}'.format(self.color, self.key)

    @property
    def floor(self):
        return self.pos[0]

    @floor.setter
    def floor(self, floor):
        z, x, y = self.pos
        self.pos = (floor, x, y)

    #移动到的位置
    def move_pos(self, key):
        self.key = key
        key_map = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        floor, x1, y1 = self.pos
        x2, y2 = key_map.get(self.key, (0, 0)) #将key转换为具体方向
        return (floor, x1 + x2, y1 + y2)

    def move(self, key):
        self.old_pos = self.pos
        self.pos = self.move_pos(key)


class Layout(FocusBehavior, FloatLayout):
    row = MazeSetting.rows + 2
    col = MazeSetting.cols + 2

    def __init__(self, **kwargs):
        super(Layout, self).__init__(**kwargs)

        self.maze = Maze()
        self.maze.update()

        self.front = Layer(self.row, self.col)
        self.middle = Layer(self.row, self.col)
        self.back = Layer(self.row, self.col)

        self.add_widget(self.back)
        self.add_widget(self.middle)
        self.add_widget(self.front)
        for i in range(self.row):
            for j in range(self.col):
                self.front.add(i, j, Cache.next('empty'))
                self.middle.add(i, j)
                self.back.add(i, j, Cache.next('ground'))

        self.hero = Hero(self.row, self.col)
        self.hero.pos = set(self.maze.maze_info[1]['stair'][MazeBase.Value.Stair.down]).pop()
        self.focus = True
        Clock.schedule_interval(self.show, 0.20)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key = keycode[1]
        if key not in ('up', 'down', 'left', 'right'):
            return False
        self.move(key)
        return True

    def on_touch_down(self, touch):
        if self.maze.is_boss_floor(self.hero.floor):
            self.maze.update()
        self.hero.floor += 1
        if self.collide_point(touch.x, touch.y):
            return True
        super(Layout, self).on_touch_down(touch)


    def moveimage(self):
        _, x, y = self.hero.old_pos
        image = self.front.image[x][y]
        image.texture = Cache.next('empty')

        _, x, y = self.hero.pos
        image = self.front.image[x][y]
        image.texture = Cache.next(self.hero.name, 'action', False)
        
        image = self.middle.image[x][y]
        image.texture = Cache.next('empty')

    def ismove(self, pos):
        floor, x, y = pos
        if x < 0 or x >= self.col or y < 0 or y >= self.row:
            return False
        pos_type = self.maze.get_type(pos)
        pos_value = self.maze.get_value(pos)
        if pos_type == MazeBase.Type.Static.ground:
            return True
        elif pos_type == MazeBase.Type.Static.wall:
            return False
        elif pos_type == MazeBase.Type.Static.stair:
            if pos_value == MazeBase.Value.Stair.down:
                if not self.maze.is_initial_floor(floor - 1) and not self.maze.is_boss_floor(floor - 1):
                    self.hero.floor -= 1
            elif pos_value == MazeBase.Value.Stair.up:
                if self.maze.is_boss_floor(floor):
                    self.maze.update()
                    self.hero.weapon = randint(1, 5)
                self.hero.floor += 1
        elif pos_type == MazeBase.Type.Static.door:
            self.hero.action.add(pos)
            return False
        elif pos_type in (MazeBase.Type.Item.key, MazeBase.Type.Item.attack, MazeBase.Type.Item.defence, MazeBase.Type.Item.potion, MazeBase.Type.Item.holy):
            self.maze.set_type(pos, MazeBase.Type.Static.ground)
        elif pos_type == MazeBase.Type.Active.monster:
            print('Fight monster {}'.format('-'.join(pos_value)))
            self.maze.set_type(pos, MazeBase.Type.Static.ground)  
        return True

    def move(self, key):
        if self.ismove(self.hero.move_pos(key)):
            self.hero.move(key)
        Cache.reset(self.hero.name)
        self.moveimage()

    def get_texture(self, pos, style='static'):
        floor, x, y = pos
        pos_type = self.maze.get_type(pos)
        pos_value = self.maze.get_value(pos)
        if pos_type == MazeBase.Type.Static.ground:
            pos_key = 'ground'
        elif pos_type == MazeBase.Type.Static.wall:
            pos_key = 'wall'
        elif pos_type == MazeBase.Type.Static.stair:
            if pos_value == MazeBase.Value.Stair.down:
                pos_key = 'stair-down'
            elif pos_value == MazeBase.Value.Stair.up:
                pos_key = 'stair-up'
        elif pos_type == MazeBase.Type.Static.door:
            if pos_value == MazeBase.Value.Color.yellow:
                pos_key = 'door-yellow'
            elif pos_value == MazeBase.Value.Color.blue:
                pos_key = 'door-blue'
            elif pos_value == MazeBase.Value.Color.red:
                pos_key = 'door-red'
            elif pos_value == MazeBase.Value.Color.green:
                pos_key = 'door-green'
        elif pos_type == MazeBase.Type.Item.key:
            if pos_value == MazeBase.Value.Color.yellow:
                pos_key = 'key-yellow'
            elif pos_value == MazeBase.Value.Color.blue:
                pos_key = 'key-blue'
            elif pos_value == MazeBase.Value.Color.red:
                pos_key = 'key-red'
            elif pos_value == MazeBase.Value.Color.green:
                pos_key = 'key-green'
        elif pos_type == MazeBase.Type.Item.attack:
            if pos_value == MazeBase.Value.Gem.small:
                pos_key = 'gem-attack-small'
            elif pos_value == MazeBase.Value.Gem.big:
                pos_key = 'gem-attack-big'
            elif pos_value == MazeBase.Value.Gem.large:
                pos_key = 'weapen-attack-{:0>2}'.format(self.hero.weapon)
        elif pos_type == MazeBase.Type.Item.defence:
            if pos_value == MazeBase.Value.Gem.small:
                pos_key = 'gem-defence-small'
            elif pos_value == MazeBase.Value.Gem.big:
                pos_key = 'gem-defence-big'
            elif pos_value == MazeBase.Value.Gem.large:
                pos_key = 'weapen-defence-{:0>2}'.format(self.hero.weapon)
        elif pos_type == MazeBase.Type.Item.potion:
            if pos_value == MazeBase.Value.Potion.red:
                pos_key = 'potion-red'
            elif pos_value == MazeBase.Value.Potion.blue:
                pos_key = 'potion-blue'
            elif pos_value == MazeBase.Value.Potion.yellow:
                pos_key = 'potion-yellow'
            elif pos_value == MazeBase.Value.Potion.green:
                pos_key = 'potion-green'
        elif pos_type == MazeBase.Type.Item.holy:
            pos_key = 'holy'
        elif pos_type == MazeBase.Type.Active.monster:
            pos_key = '-'.join(pos_value)
            style = 'dynamic'

        return Cache.next(pos_key, style)

    def show(self, dt):
        floor = self.hero.floor
        self.moveimage()
        for i in range(self.row):
            for j in range(self.col):
                pos_image = self.middle.image[i][j]
                pos = (floor, i, j)
                if pos not in self.hero.action:
                    texture = self.get_texture(pos)
                else:
                    texture = self.get_texture(pos, 'action')

                if texture:
                    pos_image.texture = texture
                else:
                    pos_image.texture = Cache.next('empty')
                    self.maze.set_type(pos, MazeBase.Type.Static.ground)
                    self.hero.action.remove(pos)
                

class Mota(App):
    def build(self):
        #javaclass = autoclass('com.test.JavaClass')
        #print(javaclass().show())

        self.layout = Layout()
        return self.layout

    def on_start(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    mota = Mota()
    mota.run()
    mota.stop()
