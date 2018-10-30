# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from setting import MazeSetting

class Scene:
    forward = []
    backward = []
    #触发条件，npc, monster
    condition = []

    def __init__(self, trigger=(0, 0, 0), person={}, dialog=[], condition=[], repeat=False):
        self.disable = False
        self.trigger = trigger
        self.person = {} #人物，1表示英雄，2表示对方，其他数字表示其他人物
        self.dialog = dialog #对话
        self.condition = condition
        self.repeat = repeat #是否重复触发，前置中不能设置该参数

    def add_forward(self, forward):
        if not isinstance(forward, tuple) and not isinstance(forward, list):
            forward = [forward]
        self.forward = forward
        for f in self.forward:
            f.backward.append(f)

    def run(self):
        if not self.repeat:
            self.disable = True

'''
condition条件
将人物或怪物加入唯一编号
只判断类型或者值的任务可以为：
1.消灭若干怪物
2.找到商人
'''
class Story:
    def __init__(self, maze):
        self.maze = maze
        self.scene = {}
        self.task = {} #任务指引

    def add_scene(self, pos=(0, 0, 0), **kwargs):
        scene = Scene(trigger=pos, **kwargs)
        if not scene.repeat:
            if pos not in self.task:
                self.task[pos] = []
            self.task[pos].append(scene)
        if pos not in self.scene:
            self.scene[pos] = []
        self.scene[pos].append(scene)
        return scene

    def check(self, pos):
        if pos not in self.scene:
            return None

        #pos_type = self.maze.get_type(pos)
        #pos_value = self.maze.get_value(pos)

        scene_enable = []
        for scene in self.scene[pos]:
            if scene.disable:
                continue
            if sum([not forward.disable for forward in scene.forward]):
                continue
            if sum([not condition for condition in scene.condition]):
                continue
            scene_enable.append(scene)

        sorted(scene_enable, key=lambda scene: 1 - scene.repeat)
        if scene_enable:
            scene = scene_enable.pop()
            scene.run()
            return scene
        return None

    def save(self):
        pass

    def load(self):
        pass
