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

'''
sometimes node is empty, that means we will get nothing in these area
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

        self.floor = 1
        self.pos = (5, 5)
        self.color = 'blue'
        self.key = 'down'
        self.focused = True
        Clock.schedule_interval(self.show, 0.25)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        print(keycode)
        key = keycode[1]
        if key not in ('up', 'down', 'left', 'right'):
            return False
        self.move(key)
        return True
    
    def on_touch_down(self, touch):
        print(touch)
        if self.maze.is_boss_floor(self.floor):
            self.maze.update()
        self.floor += 1
        if self.collide_point(touch.x, touch.y):
            return True
        super(Layout, self).on_touch_down(touch)

    def move(self, key):
        if key == 'up':
            move = (1, 0)
        elif key == 'down':
            move = (1, 0)
        elif key == 'left':
            move = (1, 0)
        elif key == 'right':
            move = (1, 0)
        else:
            move = (0, 0)
        
        x, y = move
        x_before, y_before = self.pos
        x_after, y_after = (x_before + x, y_before + y)
        self.pos = (x_before + x, y_before + y)
        
        self.front.image[x_before][y_before].texture = Cache.next('empty')
        


    def show(self, dt):
        floor = self.floor
        hero_image = self.front.image[self.pos[0]][self.pos[1]]
        hero_image.texture = Cache.next('hero-{}-{}'.format(self.color, self.key), 'action')
        if not hero_image.texture:
            hero_image.texture = Cache.next('hero-{}-{}'.format(self.color, self.key))
        for i in range(self.row):
            for j in range(self.col):
                pos_type = self.maze.get_type((floor, i, j))
                pos_value = self.maze.get_value((floor, i, j))
                pos_image = self.middle.image[i][j]
                if pos_type == MazeBase.Type.Static.ground:
                    pos_image.texture = Cache.next('ground')
                elif pos_type == MazeBase.Type.Static.wall:
                    pos_image.texture = Cache.next('wall')
                elif pos_type == MazeBase.Type.Static.stair:
                    if pos_value == MazeBase.Value.Stair.down:
                        pos_image.texture = Cache.next('stair-down')
                    elif pos_value == MazeBase.Value.Stair.up:
                        pos_image.texture = Cache.next('stair-up')
                elif pos_type == MazeBase.Type.Static.door:
                    if pos_value == MazeBase.Value.Color.yellow:
                        pos_image.texture = Cache.next('door-yellow')
                    elif pos_value == MazeBase.Value.Color.blue:
                        pos_image.texture = Cache.next('door-blue')
                    elif pos_value == MazeBase.Value.Color.red:
                        pos_image.texture = Cache.next('door-red')
                    elif pos_value == MazeBase.Value.Color.green:
                        pos_image.texture = Cache.next('door-green')
                elif pos_type == MazeBase.Type.Item.key:
                    if pos_value == MazeBase.Value.Color.yellow:
                        pos_image.texture = Cache.next('key-yellow')
                    elif pos_value == MazeBase.Value.Color.blue:
                        pos_image.texture = Cache.next('key-blue')
                    elif pos_value == MazeBase.Value.Color.red:
                        pos_image.texture = Cache.next('key-red')
                    elif pos_value == MazeBase.Value.Color.green:
                        pos_image.texture = Cache.next('key-green')
                elif pos_type == MazeBase.Type.Item.attack:
                    if pos_value == MazeBase.Value.Gem.small:
                        pos_image.texture = Cache.next('gem-attack-small')
                    elif pos_value == MazeBase.Value.Gem.big:
                        pos_image.texture = Cache.next('gem-attack-big')
                    elif pos_value == MazeBase.Value.Gem.large:
                        #will random in 5
                        pos_image.texture = Cache.next('weapen-attack-01')
                elif pos_type == MazeBase.Type.Item.defence:
                    if pos_value == MazeBase.Value.Gem.small:
                        pos_image.texture = Cache.next('gem-defence-small')
                    elif pos_value == MazeBase.Value.Gem.big:
                        pos_image.texture = Cache.next('gem-defence-big')
                    elif pos_value == MazeBase.Value.Gem.large:
                        #will random in 5
                        pos_image.texture = Cache.next('weapen-defence-01')
                elif pos_type == MazeBase.Type.Item.potion:
                    if pos_value == MazeBase.Value.Potion.red:
                        pos_image.texture = Cache.next('potion-red')
                    elif pos_value == MazeBase.Value.Potion.blue:
                        pos_image.texture = Cache.next('potion-blue')
                    elif pos_value == MazeBase.Value.Potion.yellow:
                        pos_image.texture = Cache.next('potion-yellow')
                    elif pos_value == MazeBase.Value.Potion.green:
                        pos_image.texture = Cache.next('potion-green')
                elif pos_type == MazeBase.Type.Item.holy:
                    pos_image.texture = Cache.next('holy')
                elif pos_type == MazeBase.Type.Active.monster:
                    pos_image.texture = Cache.next('-'.join(pos_value), 'dynamic')
                if not pos_image.texture:
                    print(pos_type, pos_value)


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
