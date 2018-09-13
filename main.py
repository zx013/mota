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

from cache import Cache, Music
from maze import Maze, MazeSetting, MazeBase
from random import randint

'''
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
    opacity = 1
    action = set()
    wall = 2
    weapon = 1

    def __init__(self, maze, row, col, **kwargs):
        self.maze = maze
        self.row = row
        self.col = col
        self.wall = 2
        self.weapon = 1

    @property
    def name(self):
        return 'hero-{}-{}'.format(self.color, self.key)

    @property
    def floor(self):
        return self.pos[0]

    @floor.setter
    def floor(self, floor):
        if self.maze.is_boss_floor(floor - 1):
            self.maze.update()
            self.wall = randint(1, 3)
            self.weapon = randint(1, 5)

        update_pos = None
        self.old_pos = self.pos
        if floor in self.maze.maze_info: #楼层存在
            stair = self.maze.maze_info[floor]['stair']
            if self.floor == floor + 1: #下楼
                if not self.maze.is_boss_floor(floor) and MazeBase.Value.Stair.up in stair: #楼梯存在
                        update_pos = set(stair[MazeBase.Value.Stair.up]).pop()
            elif self.floor == floor - 1: #上楼
                if MazeBase.Value.Stair.down in stair:
                    update_pos = set(stair[MazeBase.Value.Stair.down]).pop()

        if update_pos:
            self.pos = update_pos
            Music.play('floor')

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


class Map(FocusBehavior, FloatLayout):
    row = MazeSetting.rows + 2
    col = MazeSetting.cols + 2

    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)

        self.maze = Maze()
        self.maze.update()
        self.maze.set_init()

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

        self.hero = Hero(self.maze, self.row, self.col)
        self.hero.pos = self.maze.maze_info[0]['init']
        self.focus = True
        Clock.schedule_interval(self.show, 0.1)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key = keycode[1]
        if key not in ('up', 'down', 'left', 'right'):
            return False
        self.move(key)
        return True

    def on_touch_down(self, touch):
        self.hero.floor += 1
        if self.collide_point(touch.x, touch.y):
            return True
        super(Map, self).on_touch_down(touch)


    def ismove(self, pos):
        if pos in self.hero.action:
            return False
        floor, x, y = pos
        if x < 0 or x >= self.col or y < 0 or y >= self.row:
            return False
        pos_type = self.maze.get_type(pos)
        pos_value = self.maze.get_value(pos)
        herobase = self.maze.herobase
        herostate = self.maze.herostate

        if pos_type == MazeBase.Type.Static.wall:
            return False
        elif pos_type == MazeBase.Type.Static.stair:
            if pos_value == MazeBase.Value.Stair.down:
                self.hero.floor -= 1
            elif pos_value == MazeBase.Value.Stair.up:
                self.hero.floor += 1
            return True
        elif pos_type == MazeBase.Type.Static.door:
            if herostate.key[pos_value] == 0:
                return False
            herostate.key[pos_value] -= 1
            self.hero.action.add(pos)
            Music.play('opendoor')
            return False
        elif pos_type == MazeBase.Type.Item.key:
            herostate.key[pos_value] += 1
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.attack:
            herostate.attack += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.defence:
            herostate.defence += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.potion:
            herostate.health += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.holy:
            herostate.health += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Active.monster:
            print('Fight monster {}'.format('-'.join(pos_value)))
            Music.play('blood')
        elif pos_type == MazeBase.Type.Active.rpc:
            return False

        self.maze.set_type(pos, MazeBase.Type.Static.ground)
        self.maze.set_value(pos, 0)
        return True

    def move(self, key):
        if self.ismove(self.hero.move_pos(key)):
            self.hero.move(key)
        Cache.reset(self.hero.name)
        self.show_hero()


    def get_texture(self, pos, pos_style='static'):
        floor, x, y = pos
        pos_type = self.maze.get_type(pos)
        pos_value = self.maze.get_value(pos)
        
        if pos_type == MazeBase.Type.Static.init:
            pos_key = 'ground'
        elif pos_type == MazeBase.Type.Static.ground:
            pos_key = 'ground'
        elif pos_type == MazeBase.Type.Static.wall:
            pos_key = 'wall-{:0>2}'.format(self.hero.wall)
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
            pos_style = 'dynamic'
        elif pos_type == MazeBase.Type.Active.rpc:
            if pos_value == MazeBase.Value.Rpc.wisdom:
                pos_key = 'npc-wisdom'
            elif pos_value == MazeBase.Value.Rpc.trader:
                pos_key = 'npc-trader'
            elif pos_value == MazeBase.Value.Rpc.thief:
                pos_key = 'npc-thief'
            elif pos_value == MazeBase.Value.Rpc.fairy:
                pos_key = 'npc-fairy'
            pos_style = 'dynamic'

        return Cache.next(pos_key, pos_style)

    def show_hero(self):
        _, x, y = self.hero.old_pos
        image = self.front.image[x][y]
        image.texture = Cache.next('empty')

        _, x, y = self.hero.pos
        image = self.front.image[x][y]
        image.texture = Cache.next(self.hero.name, 'action', False)

        image = self.middle.image[x][y]
        image.texture = Cache.next('empty')

    def show(self, dt):
        floor = self.hero.floor
        opacity = self.hero.opacity
        self.show_hero()
        for i in range(self.row):
            for j in range(self.col):
                pos_image = self.middle.image[i][j]
                pos = (floor, i, j)
                if pos in self.hero.action:
                    texture = self.get_texture(pos, 'action')
                else:
                    texture = self.get_texture(pos)

                if texture:
                    pos_image.texture = texture
                else:
                    pos_image.texture = Cache.next('empty')
                    self.maze.set_type(pos, MazeBase.Type.Static.ground)
                    self.maze.set_value(pos, 0)
                    self.hero.action.remove(pos)
                pos_image.canvas.opacity = opacity


class State(FloatLayout):
    pass

class Layout(FloatLayout):
    pass

class Mota(App):
    def build(self):
        #javaclass = autoclass('com.test.JavaClass')
        #print(javaclass().show())

        self.layout = Map()
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
