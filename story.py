# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from setting import MazeSetting
import random

class Scene:
    def __init__(self, name='未知', trigger=(0, 0, 0), person={}, dialog=[], condition=[], repeat=False):
        self.active = False #是否激活过对话
        self.name = name
        self.trigger = trigger
        self.person = {} #人物，1表示英雄，2表示对方，其他数字表示其他人物
        self.dialog = dialog #对话
        self.condition = condition
        self.repeat = repeat #是否重复触发，前置中不能设置该参数

        self.forward = []
        self.backward = []

    def run(self):
        self.active = True
        task = []
        for b in self.backward:
            if not sum([not f.active for f in b.forward]):
                task.append(b)
        return task

class Story:
    def __init__(self, maze):
        self.maze = maze
        self.task = {} #任务指引
        self.repeat = {}

    def add_scene(self, pos=(0, 0, 0), **kwargs):
        scene = Scene(trigger=pos, **kwargs)
        if scene.repeat:
            self.add_repeat(scene)
        else:
            self.add_task(scene)
        return scene

    def add_repeat(self, scene):
        if not isinstance(scene, tuple) and not isinstance(scene, list):
            scene = [scene]
        for s in scene:
            pos = s.trigger
            if pos not in self.repeat:
                self.repeat[pos] = []
            self.repeat[pos].append(s)

    def add_task(self, scene):
        if not isinstance(scene, tuple) and not isinstance(scene, list):
            scene = [scene]
        for s in scene:
            pos = s.trigger
            if pos not in self.task:
                self.task[pos] = []
            self.task[pos].append(s)

    def del_task(self, scene):
        if not isinstance(scene, tuple) and not isinstance(scene, list):
            scene = [scene]
        for s in scene:
            pos = s.trigger
            if s in self.task[pos]:
                self.task[pos].remove(s)
                if not self.task[pos]:
                    del self.task[pos]

    @property
    def task_list(self):
        task_list = []
        for pos, task in self.task.items():
            for scene in task:
                task_list.append((scene.name, pos))
        return task_list

    def connect(self, fscene, bscene):
        if not isinstance(fscene, tuple) and not isinstance(fscene, list):
            fscene = [fscene]
        if not isinstance(bscene, tuple) and not isinstance(bscene, list):
            bscene = [bscene]
        for f in fscene:
            for b in bscene:
                f.backward.append(b)
                b.forward.append(f)
                self.del_task(b)

    def check(self, pos):
        #pos_type = self.maze.get_type(pos)
        #pos_value = self.maze.get_value(pos)

        scene_task = [scene for scene in self.task.get(pos, []) if not scene.active]
        if scene_task:
            scene = scene_task.pop()
            task = scene.run()
            self.del_task(scene)
            self.add_task(task)
            print('task', task)
            return scene

        scene_repeat = [scene for scene in self.repeat.get(pos, [])]
        random.shuffle(scene_repeat)
        if scene_repeat:
            scene = scene_repeat.pop()
            task = scene.run()
            print('repeat', task)
            return scene
        return None

    def save(self):
        pass

    def load(self):
        pass
