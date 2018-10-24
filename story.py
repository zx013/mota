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

    def __init__(self, trigger=(0, 0, 0), person={}, dialog=[], condition=[], repeat=False, forward=[]):
        self.disable = False
        self.trigger = trigger
        self.person = {} #人物，1表示英雄，2表示对方，其他数字表示其他人物
        self.dialog = dialog #对话
        self.condition = condition
        self.repeat = repeat #是否重复触发，前置中不能设置该参数
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

    def add_scene(self, scene):
        if scene.trigger not in self.scene:
            self.scene[scene.trigger] = []
        self.scene[scene.trigger].append(scene)

    def check(self, pos):
        if pos not in self.scene:
            return None

        #pos_type = self.maze.get_type(pos)
        #pos_value = self.maze.get_value(pos)

        for scene in self.scene[pos]:
            if scene.disable:
                continue
            if sum([not forward.disable for forward in scene.forward]):
                continue
            if sum([not condition for condition in scene.condition]):
                continue
            scene.run()
            return scene
        return None

    def save(self):
        pass

    def load(self):
        scene = Scene(trigger=(0, 1, 1), dialog=[(1, '你好！'), (2, '欢迎进入无尽的魔塔。')], repeat=True)
        self.add_scene(scene)
        scene = Scene(trigger=(0, 1, MazeSetting.cols), dialog=[(1, '你为什么在这里？'), (2, '你可以在我这里购买东西。')], repeat=True)
        self.add_scene(scene)
        scene = Scene(trigger=(0, MazeSetting.rows, 1), dialog=[(1, '我为什么在这里？'), (2, '又多了一个送死的勇者。')], repeat=True)
        self.add_scene(scene)
        scene = Scene(trigger=(0, MazeSetting.rows, MazeSetting.cols), dialog=[(1, '又见到你了，小精灵。'), (2, '神圣十字架在魔塔的深处，给我神圣十字架，我可以增强你的能力。')], repeat=True)
        self.add_scene(scene)
