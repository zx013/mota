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

import os
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
#python2应为from Configparser import ConfigParser
from configparser import ConfigParser

from maze import Maze, MazeSetting, MazeBase

'''
静态
路径，行，列

动态，动作（移动/消除）
路径，行，列，方向（按行还是按列）
只能从左到右或者从上到下
'''

class ShowBase:
    size = 32

class Cache:
    def __init__(self):
        self.config = {}
        self.cache = {}
        self.load()

    #解析读到的数字或范围
    def __analyse_number(self, string):
        if '-' in string:
            start, stop = string.split('-')
            num = range(int(start) - 1, int(stop))
        else:
            num = int(string) - 1
        return num

    #读取info配置
    def __read_info(self, path):
        config = ConfigParser()
        config.read(os.path.join(path, 'info'))

        info = dict(config._sections)
        for key in info:
            info[key] = dict(info[key])
            for k, v in info[key].items():
                if ',' not in v:
                    continue
                row, col = v.split(',')
                row = self.__analyse_number(row)
                col = self.__analyse_number(col)
                info[key][k] = (row, col)
            #dynamic或action的第一个作为static
            if 'static' not in info[key]:
                if 'dynamic' in info[key] or 'action' in info[key]:
                    if 'dynamic' in info[key]:
                        row, col = info[key]['dynamic']
                    elif 'action' in info[key]:
                        row, col = info[key]['action']
                    if not isinstance(row, int):
                        row = row[0]
                    if not isinstance(col, int):
                        col = col[0]
                    info[key]['static'] = (row, col)
        return info

    #将行列换成真实坐标
    def __real_pos(self, size, pos):
        weight, height = size
        row, col = pos
        return col * ShowBase.size, height - (row + 1) * ShowBase.size

    #获取texture中的部分
    def __cut_texture(self, texture, pos):
        row, col = pos
        if isinstance(row, int):
            if isinstance(col, int):
                pos_list = [(row, col)]
            else:
                pos_list = [(row, c) for c in col]
        else:
            if isinstance(col, int):
                pos_list = [(r, col) for r in row]
            else:
                pos_list = []

        textures = []
        for pos in pos_list:
            row, col = self.__real_pos(texture.size, pos)
            textures.append(texture.get_region(row, col, ShowBase.size, ShowBase.size))
        return textures

    #加载配置，并缓存图片信息
    def load(self):
        self.config = {}
        self.cache = {}
        for path, _, filelist in os.walk('data'):
            if 'info' not in filelist:
                continue
            for key, val in self.__read_info(path).items():
                if 'path' in val:
                    continue
                name = os.path.join(path, val['name'])
                if name not in self.cache:
                    self.cache[name] = Image(source=name).texture
                val['path'] = name
                if 'static' in val:
                    val['static_textures'] = self.__cut_texture(self.cache[name], val['static'])[0]
                if 'dynamic' in val:
                    val['dynamic_textures'] = self.__cut_texture(self.cache[name], val['dynamic'])
                    val['dynamic_index'] = 0
                    val['dynamic_length'] = len(val['dynamic_textures'])
                if 'action' in val:
                    val['action_textures'] = self.__cut_texture(self.cache[name], val['action'])
                    val['action_index'] = 0
                    val['action_length'] = len(val['action_textures'])

                self.config[key] = val

    def next(self, key, style='static'):
        if key not in self.config:
            return None

        info = self.config[key]
        textures_name = '{}_textures'.format(style)
        textures = info[textures_name]
        if style == 'static':
            return textures

        index_name = '{}_index'.format(style)
        index = info[index_name]
        length_name = '{}_length'.format(style)
        length = info[length_name]

        if index >= length:
            return None
        texture = textures[index]
        info[index_name] += 1
        if style == 'dynamic':
            info[index_name] %= length
        return texture


class Mota(App):
    row = MazeSetting.rows + 2
    col = MazeSetting.cols + 2

    def show(self, floor):
        for i in range(self.row):
            for j in range(self.col):
                pos_type = self.maze.get_type((floor, i, j))
                pos_value = self.maze.get_value((floor, i, j))
                if pos_type == MazeBase.Type.Static.ground:
                    self.image[i][j].texture = self.cache.next('ground')
                elif pos_type == MazeBase.Type.Static.wall:
                    self.image[i][j].texture = self.cache.next('wall')
                elif pos_type == MazeBase.Type.Static.stair:
                    if pos_value == MazeBase.Value.Stair.down:
                        self.image[i][j].texture = self.cache.next('stair-down')
                    elif pos_value == MazeBase.Value.Stair.up:
                        self.image[i][j].texture = self.cache.next('stair-up')
                elif pos_type == MazeBase.Type.Static.door:
                    if pos_value == MazeBase.Value.Color.yellow:
                        self.image[i][j].texture = self.cache.next('door-yellow')
                    elif pos_value == MazeBase.Value.Color.blue:
                        self.image[i][j].texture = self.cache.next('door-blue')
                    elif pos_value == MazeBase.Value.Color.red:
                        self.image[i][j].texture = self.cache.next('door-red')
                    elif pos_value == MazeBase.Value.Color.green:
                        self.image[i][j].texture = self.cache.next('door-green')
                elif pos_type == MazeBase.Type.Item.key:
                    if pos_value == MazeBase.Value.Color.yellow:
                        self.image[i][j].texture = self.cache.next('key-yellow')
                    elif pos_value == MazeBase.Value.Color.blue:
                        self.image[i][j].texture = self.cache.next('key-blue')
                    elif pos_value == MazeBase.Value.Color.red:
                        self.image[i][j].texture = self.cache.next('key-red')
                    elif pos_value == MazeBase.Value.Color.green:
                        self.image[i][j].texture = self.cache.next('key-green')
                elif pos_type == MazeBase.Type.Item.attack:
                    if pos_value == MazeBase.Value.Gem.small:
                        self.image[i][j].texture = self.cache.next('gem-attack-small')
                    elif pos_value == MazeBase.Value.Gem.big:
                        self.image[i][j].texture = self.cache.next('gem-attack-big')
                    elif pos_value == MazeBase.Value.Gem.large:
                        pass
                elif pos_type == MazeBase.Type.Item.defence:
                    if pos_value == MazeBase.Value.Gem.small:
                        self.image[i][j].texture = self.cache.next('gem-defence-small')
                    elif pos_value == MazeBase.Value.Gem.big:
                        self.image[i][j].texture = self.cache.next('gem-defence-big')
                    elif pos_value == MazeBase.Value.Gem.large:
                        pass
                elif pos_type == MazeBase.Type.Item.potion:
                    if pos_value == MazeBase.Value.Potion.red:
                        self.image[i][j].texture = self.cache.next('potion-red')
                    elif pos_value == MazeBase.Value.Potion.blue:
                        self.image[i][j].texture = self.cache.next('potion-blue')
                    elif pos_value == MazeBase.Value.Potion.yellow:
                        self.image[i][j].texture = self.cache.next('potion-yellow')
                    elif pos_value == MazeBase.Value.Potion.green:
                        self.image[i][j].texture = self.cache.next('potion-green')
                elif pos_type == MazeBase.Type.Item.holy:
                    self.image[i][j].texture = self.cache.next('holy')
                    

    def build(self):
        self.cache = Cache()
        self.maze = Maze()
        self.maze.update()

        #javaclass = autoclass('com.test.JavaClass')
        #print(javaclass().show())

        self.image = [[None for j in range(self.col)] for i in range(self.row)]
        self.layout = GridLayout(rows=self.row, cols=self.col, size=(ShowBase.size * self.row, ShowBase.size * self.col), size_hint=(None, None))
        for i in range(self.row):
            for j in range(self.col):
                image = Image(size=(ShowBase.size, ShowBase.size))
                image.texture = self.cache.next('ground')
                self.image[i][j] = image
                self.layout.add_widget(image)
        
        self.show(1)

        #Clock.schedule_interval(self.image.next, 0.2)
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
