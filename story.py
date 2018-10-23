# -*- coding: utf-8 -*-
"""
@author: zx013
"""

'''
情节
前置情节：前置情节满足或部分满足可开启该情节
后置情节：完成情节后可激活后置情节
前置条件：满足一定条件时才开启情节
'''
class Scene:
    forward = []
    backward = []
    #触发条件，地点触发，人物触发，怪物触发
    condition = []

    def __init__(self, trigger=(0, 0, 0), person={}, dialog=[], repeat=False, forward=[]):
        self.active = True
        self.trigger = trigger
        self.person = {} #人物，1表示英雄，2表示对方，其他数字表示其他人物
        self.dialog = dialog #对话
        self.repeat = repeat #是否重复触发，前置中不能设置该参数
        if isinstance(forward, tuple) or isinstance(forward, list):
            forward = [forward]
        self.forward = forward
        for f in self.forward:
            f.backward.append(f)

    def run(self):
        if not self.repeat:
            self.active = True

class Story:
    def __init__(self):
        self.id = 0
        self.scene = []

    def add_scene(self):
        pass

    def run(self):
        pass


if __name__ == '__main__':
    Sence(trigger=(0, 1, 1), dialog=[(1, '你好！'), (2, '欢迎进入无尽的魔塔。'), (1, '我为什么在这里？'), (2, '又多了一个送死的勇者。')])
