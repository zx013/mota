#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
from kivy.config import ConfigParser
#from configparser import ConfigParser #python2应为from Configparser import ConfigParser
from kivy.uix.image import Image

from setting import Setting


class ConfigBase:
    step = 0.05

    def __init__(self):
        self.config = {}
        self.load()

    #解析读到的数字或范围
    def analyse_number(self, string, key):
        plus = key in ('static', 'dynamic', 'action')

        if '-' in string:
            start, stop = string.split('-')
            return range(int(start) - plus, int(stop) + 1 - plus)
        else:
            if string.isdigit():
                return int(string) - plus
            else:
                return float(string) - plus

    #读取info配置
    def read_info(self, path):
        config = ConfigParser()
        config.read(os.path.join(path, 'info'))

        info = dict(config._sections)
        for key in info:
            info[key] = dict(info[key])
            info[key]['size'] = (TextureBase.size, TextureBase.size)
            for k, v in info[key].items():
                if ',' not in v:
                    continue
                v = v.replace(' ', '')
                num_list = [self.analyse_number(num, k) for num in v.split(',')]
                info[key][k] = num_list

                if k in ('static', 'dynamic', 'action'):
                    row, col = num_list
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
                else:
                    info[key]['static'] = (0, 0)
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
                        val['dt'] = 0.1
                    else:
                        val['dt'] = 0.2
                val['dt'] -= 0.01 #有时会有小的波动(0.001)
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
    size = Setting.pos_size

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
    def cut_texture(self, texture, pos, size):
        row, col = pos
        x, y = size
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
            textures.append(texture.get_region(row, col, x, y))
        return textures

    #加载配置，并缓存图片信息
    def load(self):
        self.base = {}
        self.texture = {}
        for key, val in Config.config.items():
            if 'path' not in val:
                continue
            name = val['path']
            if not name.endswith('.png'):
                continue
            if name not in self.base:
                self.base[name] = Image(source=name).texture
            val['path'] = name

            info = {}
            if 'static' in val:
                info['static_textures'] = self.cut_texture(self.base[name], val['static'], val['size'])[0]
            if 'dynamic' in val:
                info['dynamic_textures'] = self.cut_texture(self.base[name], val['dynamic'], val['size'])
                info['dynamic_index'] = 0
                info['dynamic_length'] = len(info['dynamic_textures'])
            if 'action' in val:
                info['action_textures'] = self.cut_texture(self.base[name], val['action'], val['size'])
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
