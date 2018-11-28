# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from tools import Tools
from g import gmaze, gtask
import random

class Scene:
    def __init__(self, name='未知', help='', pos=(0, 0, 0), dialog=[], task=[], repeat=False):
        self.active = False #是否激活过对话
        self.name = name
        self.help = help
        self.pos = pos
        #人物，1表示英雄，2表示对方，其他数字表示其他人物
        self.dialog = dialog #对话
        self.task = task
        self.repeat = repeat #是否重复触发，前置中不能设置该参数

        self.forward = []
        self.backward = []

    def isdialog(self):
        if self.dialog:
            return True
        return False

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
        self.state = {}
        self.repeat = {}

    def create_scene(self, **kwargs):
        scene = Scene(**kwargs)
        self.add_scene(scene)
        return scene

    def add_scene(self, scene, task_id=None):
        for s in Tools.object_list(scene):
            if s.isdialog():
                if s.repeat:
                    self.add_repeat(s)
                else:
                    self.add_dialog(s, task_id)
            else:
                self.add_task(s, task_id)

    def clean_scene(self, scene):
        for s in Tools.object_list(scene):
            if s.isdialog():
                self.clean_dialog(s)
            else:
                self.clean_task(s)

    def del_scene(self, scene, immediate=False):
        for s in Tools.object_list(scene):
            if s.isdialog():
                self.del_dialog(s, immediate)
            else:
                self.del_task(s, immediate)
            self.clean_scene(s)

    def next_scene(self, scene):
        task = scene.run()
        if len(task) > 0:
            self.clean_scene(scene)
            self.add_scene(task, scene.task_id)
        else:
            self.del_scene(scene)

    def add_repeat(self, scene):
        for s in Tools.object_list(scene):
            pos = s.pos
            if pos not in self.repeat:
                self.repeat[pos] = []
            self.repeat[pos].append(s)

    def add_dialog(self, scene, task_id=None):
        for s in Tools.object_list(scene):
            if task_id is None:
                s.task_id = gtask.insert()
            else:
                s.task_id = task_id
            gtask.update(s.task_id, s.name, s.help)

            pos = s.pos
            if pos not in self.task:
                self.task[pos] = []
            self.task[pos].append(s)

    def clean_dialog(self, scene):
        for s in Tools.object_list(scene):
            pos = s.pos
            if s in self.task[pos]:
                self.task[pos].remove(s)
                if not self.task[pos]:
                    del self.task[pos]

    def del_dialog(self, scene, immediate=False):
        for s in Tools.object_list(scene):
            gtask.remove(s.task_id, immediate)

    def add_task(self, scene, task_id=None):
        for s in Tools.object_list(scene):
            name_list, op, goal = s.task
            name_list = Tools.object_list(name_list)

            if task_id is None:
                s.task_id = gtask.insert()
            else:
                s.task_id = task_id
            s.attr = [getattr(gmaze.herostate, name) for name in name_list]
            s.goal = goal
            gtask.update(s.task_id, s.name, s.help, s.goal)

            for name in name_list:
                if name not in self.state:
                    self.state[name] = {}
                self.state[name][s.task_id] = {'name': name_list, 'op': op, 'scene': s}

    def clean_task(self, scene):
        for s in Tools.object_list(scene):
            for task in self.state.values():
                if s.task_id in task:
                    del task[s.task_id]

    def del_task(self, scene, immediate=False):
        for s in Tools.object_list(scene):
            gtask.remove(s.task_id, immediate)

    def connect(self, fscene, bscene):
        for f in Tools.object_list(fscene):
            for b in Tools.object_list(bscene):
                f.backward.append(b)
                b.forward.append(f)
                self.del_scene(b, immediate=True)

    def check_state(self, state, name):
        if name not in self.state:
            return None
        for task in list(self.state[name].values()):
            scene = task['scene']
            attr = [getattr(state, name) for name in task['name']]
            if name in task['name']:
                gtask.achieve(scene.task_id, attr[0] - scene.attr[0])
            if task['op'](*attr, *scene.attr):
                self.next_scene(scene)
                return scene
        return None

    def check_pos(self, pos):
        scene_task = [scene for scene in self.task.get(pos, []) if not scene.active]
        if scene_task:
            scene = scene_task.pop()
            self.next_scene(scene)
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
