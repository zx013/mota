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

import jnius_config
jnius_config.add_classpath('jars/javaclass.jar')
from jnius import autoclass

import os
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
#python2应为from Configparser import ConfigParser
from configparser import ConfigParser

from maze import Maze

'''
静态
路径，行，列

动态，动作（移动/消除）
路径，行，列，方向（按行还是按列）
只能从左到右或者从上到下
'''

class ShowBase:
    size = 32

class Config:
    def __init__(self):
        self.cache = {}
        self.config = self.read()

    def analyse_config(self, string):
        if '-' in string:
            start, stop = string.split('-')
            num = range(int(start) - 1, int(stop))
        else:
            num = int(string) - 1
        return num
    
    def read_config(self, path):
        config = ConfigParser()
        config.read(os.path.join(path, 'info'))
    
        info = dict(config._sections)
        for key in info:
            info[key] = dict(info[key])
            for k, v in info[key].items():
                if ',' not in v:
                    continue
                row, col = v.split(',')
                row = self.analyse_config(row)
                col = self.analyse_config(col)
                info[key][k] = (row, col)
            if 'action' in info[key] and 'static' not in info[key]:
                row, col = info[key]['action']
                if not isinstance(row, int):
                    row = row[0]
                if not isinstance(col, int):
                    col = col[0]
                info[key]['static'] = (row, col)
        return info

    def real_pos(self, size, pos):
        row, col = pos
        weight, height = size
        return col * ShowBase.size, height - (row + 1) * ShowBase.size

    def get_texture(self, texture, pos):
        textures = []
        try:
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

            for pos in pos_list:
                row, col = self.real_pos(texture.size, pos)
                textures.append(texture.get_region(row, col, ShowBase.size, ShowBase.size))
        except Exception as ex:
            print(ex)
        return textures
    
    def read(self):
        config = {}
        for path, _, filelist in os.walk('data'):
            if 'info' not in filelist:
                continue
            for key, val in self.read_config(path).items():
                if 'path' in val:
                    continue
                name = os.path.join(path, val['name'])
                if name not in self.cache:
                    self.cache[name] = Image(source=name).texture
                val['path'] = name
                if 'static' in val:
                    val['static_textures'] = self.get_texture(self.cache[name], val['static'])
                if 'action' in val:
                    val['action_textures'] = self.get_texture(self.cache[name], val['action'])
                
                config[key] = val
        return config


class ImageBase(Image):
    def __init__(self, key, **kwargs):
        if key not in g_config:
            print('Can not find key {}'.format(key))
            return
        
        info = g_config[key]
        path = info['path']
        super(ImageBase, self).__init__(source=path, size_hint=(None, None), **kwargs)

        if 'static' in info:
            self.static = self.get_texture(path, info['static'])
        elif 'action' in info:
            self.action = self.get_texture(path, info['action'])
        self.action = []
        self.index = 0
        self.texture = self.static[self.index]

    def real_pos(self, pos):
        row, col = pos
        weight, height = self.texture.size
        return col * ShowBase.size, height - (row + 1) * ShowBase.size

    def get_texture(self, path, pos):
        texture = []
        try:
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

            for pos in pos_list:
                row, col = self.real_pos(pos)
                texture.append(self.texture.get_region(row, col, ShowBase.size, ShowBase.size))
        except Exception as ex:
            print(ex)

        return texture


    def next(self, dt):
        self.index += 1
        self.index %= len(self.static)
        self.texture = self.static[self.index]


class Mota(App):
    def build(self):
        self.maze = Maze()
        self.maze.update()

        javaclass = autoclass('com.test.JavaClass')
        print(javaclass().show())

        self.image = ImageBase('door-yellow')
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.image)

        Clock.schedule_interval(self.image.next, 0.2)
        return self.layout

    def on_start(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def show(self, *args):
        pass

if __name__ == '__main__':
    mota = Mota()
    mota.run()
    mota.stop()
