#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from configparser import ConfigParser
from kivy.uix.image import Image

'''
静态
路径，行，列

动态，动作（移动/消除）
路径，行，列，方向（按行还是按列）
只能从左到右或者从上到下
'''

class CacheBase:
    size = 32

    def __init__(self):
        self.config = {}
        self.cache = {}
        self.base = None
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
        return col * self.size, height - (row + 1) * self.size

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
            textures.append(texture.get_region(row, col, self.size, self.size))
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

    def reset(self, key):
        if key not in self.config:
            return None

        info = self.config[key]
        if 'dynamic_index' in info:
            info['dynamic_index'] = 0
        if 'action_index' in info:
            info['action_index'] = 0

    def next(self, key, style='static', base=True):
        if key not in self.config:
            return None

        info = self.config[key]
        if style not in info:
            return None

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
                return None
            else:
                return info['static_textures']
        texture = textures[index]
        info[index_name] += 1
        if style == 'dynamic':
            info[index_name] %= length
        return texture


global Cache
if 'Cache' not in dir():
    Cache = CacheBase()
