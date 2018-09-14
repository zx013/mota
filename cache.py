#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
from configparser import ConfigParser
from kivy.uix.image import Image
from kivy.config import Config as DefaultConfig

'''
静态
路径，行，列

动态，动作（移动/消除）
路径，行，列，方向（按行还是按列）
只能从左到右或者从上到下
'''
class ConfigBase:
    step = 0.01

    def __init__(self):
        #长宽需要动态调整
        DefaultConfig.set('kivy', 'window_icon', os.path.join('data', 'icon.ico'))
        DefaultConfig.set('graphics', 'height', 416)
        DefaultConfig.set('graphics', 'width', 416)
        DefaultConfig.set('graphics', 'resizable', 0)
        self.config = {}
        self.load()

    #解析读到的数字或范围
    def analyse_number(self, string):
        if '-' in string:
            start, stop = string.split('-')
            num = range(int(start) - 1, int(stop))
        else:
            num = int(string) - 1
        return num

    #读取info配置
    def read_info(self, path):
        config = ConfigParser()
        config.read(os.path.join(path, 'info'))

        info = dict(config._sections)
        for key in info:
            info[key] = dict(info[key])
            for k, v in info[key].items():
                if ',' not in v:
                    continue
                row, col = v.split(',')
                row = self.analyse_number(row)
                col = self.analyse_number(col)
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

    def load(self):
        self.config = {}
        for path, _, filelist in os.walk('data'):
            if 'info' not in filelist:
                continue
            info = self.read_info(path)
            info['hero-click'] = {}
            for key, val in info.items():
                if 'name' not in val:
                    val['name'] = ''
                if 'path' not in val:
                    val['path'] = os.path.join(path, val['name'])
                if 'dt' not in val:
                    if 'hero' in key or 'door' in key:
                        val['dt'] = 0.08
                    else:
                        val['dt'] = 0.2
                val['dt'] -= self.step #有时会有小的波动(0.001)
                val['dtp'] = 0
                self.config[key] = val

    def reset(self, key):
        if key not in self.config:
            return
        info = self.config[key]
        info['dtp'] = 0

    def active(self, key, dt):
        if key not in self.config:
            return False
        info = self.config[key]
        info['dtp'] += dt
        if info['dtp'] >= info['dt']:
            info['dtp'] = 0
            return True
        return False


class TextureBase:
    size = 32

    def __init__(self):
        self.base = {}
        self.texture = {}
        self.load()

    #将行列换成真实坐标
    def real_pos(self, size, pos):
        weight, height = size
        row, col = pos
        return col * self.size, height - (row + 1) * self.size

    #获取texture中的部分
    def cut_texture(self, texture, pos):
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
            row, col = self.real_pos(texture.size, pos)
            textures.append(texture.get_region(row, col, self.size, self.size))
        return textures

    #加载配置，并缓存图片信息
    def load(self):
        self.base = {}
        self.texture = {}
        for key, val in Config.config.items():
            if 'path' not in val:
                continue
            name = val['path']
            if name not in self.base:
                self.base[name] = Image(source=name).texture
            val['path'] = name

            info = {}
            if 'static' in val:
                info['static_textures'] = self.cut_texture(self.base[name], val['static'])[0]
            if 'dynamic' in val:
                info['dynamic_textures'] = self.cut_texture(self.base[name], val['dynamic'])
                info['dynamic_index'] = 0
                info['dynamic_length'] = len(info['dynamic_textures'])
            if 'action' in val:
                info['action_textures'] = self.cut_texture(self.base[name], val['action'])
                info['action_index'] = 0
                info['action_length'] = len(info['action_textures'])
            self.texture[key] = info

    def reset(self, key):
        if key not in self.texture:
            return None

        info = self.texture[key]
        if 'dynamic_index' in info:
            info['dynamic_index'] = 0
        if 'action_index' in info:
            info['action_index'] = 0

    def next(self, key, style='static', base=True):
        if key not in self.texture:
            return None

        info = self.texture[key]

        textures_name = '{}_textures'.format(style)
        textures = info[textures_name]
        if style == 'static':
            return textures

        index_name = '{}_index'.format(style)
        index = info[index_name]
        length_name = '{}_length'.format(style)
        length = info[length_name]

        if index >= length:
            if base:
                self.reset(key)
                return None
            else:
                return info['static_textures']
        texture = textures[index]
        info[index_name] += 1
        if style == 'dynamic':
            info[index_name] %= length
        return texture


from kivy.core.audio import SoundLoader

class MusicBase:
    path = 'music'

    def __init__(self):
        self.music = {}
        self.back = None
        self.back_list = []
        for name in os.listdir(self.path):
            continue #加载太多似乎会出错
            if not name.endswith('.mp3') and not name.endswith('.wav'):
                continue
            key = name.split('.')[0]
            if key.startswith('background-'):
                index = key.split('-')[1]
                if index != 'init':
                    self.back_list.append(index)
            self.music[key] = SoundLoader.load(os.path.join('music', name))
            #self.music[key] = music

    def background(self, init=False):
        if init:
            key = 'init'
        else:
            key = random.choice(self.back_list)
        key = 'background-{}'.format(key)

        if self.back:
            self.back.stop()

        if key in self.music:
            self.back = self.music[key]
            self.back.loop = True
            self.back.seek(0)
            self.back.play()

    def play(self, key):
        if key in self.music:
            music = self.music[key]
            music.seek(0)
            music.play()


global Config
if 'Config' not in dir():
    Config = ConfigBase()

global Texture
if 'Texture' not in dir():
    Texture = TextureBase()

global Music
if 'Music' not in dir():
    Music = MusicBase()

