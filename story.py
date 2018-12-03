# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from setting import MazeBase
from cache import Config
from tools import Tools
from g import gmaze, gtask
import operator
import random

class Scene:
    def __init__(self, name='', help='', pos=(0, 0, 0), dialog=[], task=[], repeat=False):
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

    def create_dialog_name(self, pos):
        pos_data = gmaze.get_data(pos)
        pos_key = MazeBase.get_key(pos_data)
        pos_name = Config.config[pos_key].get('name', '未知')
        floor = pos[0]
        name = '找到{}层的{}'.format(floor, pos_name)
        return name

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

    def split_task(self, task, ops):
        name, goal = task.split(ops)
        goal = int(goal) if goal.isdigit() else 0
        return name, goal

    def create_task_name(self, name, ops, goal):
        name_dict = {
            'health': ('生命', '恢复', '损失'),
            'attack': ('攻击', '提高', '降低'),
            'defence': ('防御', '提高', '降低'),
            'gold': ('金钱', '获得', '消耗'),
            'experience': ('经验', '获得', '消耗'),
        }
        task_name, task_add, task_del = name_dict.get(name)
        if ops == '+':
            name = '{}{}{}'.format(task_add, goal, task_name)
        elif ops == '-':
            name = '{}{}{}'.format(task_del, goal, task_name)
        elif ops == '*':
            name = '{}{}倍的{}'.format(task_add, goal, task_name)
        elif ops == '/':
            name = '{}{}倍的{}'.format(task_del, goal, task_name)
        elif ops == '<=':
            name = '{}降低至{}'.format(task_name, goal)
        elif ops == '<':
            name = '{}低于{}'.format(task_name, goal)
        elif ops == '>=':
            name = '{}到达{}'.format(task_name, goal)
        elif ops == '>':
            name = '{}超过{}'.format(task_name, goal)
        elif ops == '==':
            name = '{}恰好为{}'.format(task_name, goal)
        elif ops == '!=':
            name = '{}不为{}'.format(task_name, goal)
        else:
            name = ''
        return name

    def create_task(self, task):
        operate_dict = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.floordiv
        } #乘除的显示上应该需要另外的逻辑
        compare_dict = {
            '<=': operator.le,
            '<': operator.lt,
            '>=': operator.ge,
            '>': operator.gt,
            '==': operator.eq,
            '!=': operator.ne
        }
        task = task.replace(' ', '')

        for ops in compare_dict.keys():
            if ops not in task:
                continue
            name, goal = self.split_task(task, ops)
            op = compare_dict.get(ops)
            func = lambda x, y: op(x, goal)
            return name, func, ops, goal, True

        for ops in operate_dict.keys():
            if ops not in task:
                continue
            if '+' in task:
                name, goal = self.split_task(task, '+')
                func = lambda x, y: x >= y + goal
            elif '-' in task:
                name, goal = self.split_task(task, '-')
                func = lambda x, y: x <= y - goal
            elif '*' in task:
                name, goal = self.split_task(task, '*')
                func = lambda x, y: x >= y * goal
            elif '/' in task:
                name, goal = self.split_task(task, '/')
                func = lambda x, y: x <= y / goal
            return name, func, ops, goal, False
        return None

    def add_task(self, scene, task_id=None):
        for s in Tools.object_list(scene):
            name_list = []
            op_list = []
            for task in Tools.object_list(s.task)[::-1]:
                name, op, ops, goal, achieve = self.create_task(task)
                if name not in name_list:
                    name_list.insert(0, name)
                op_list.insert(0, (name, op))

            if task_id is None:
                s.task_id = gtask.insert()
            else:
                s.task_id = task_id
            if not s.name:
                s.name = self.create_task_name(name, ops, goal)
            s.attr = dict([(name, getattr(gmaze.herostate, name)) for name in name_list])
            s.goal = goal
            if achieve:
                achieve = s.attr[name]
                s.attr[name] = 0
            else:
                achieve = 0
            gtask.update(s.task_id, s.name, s.help, s.goal, achieve)

            for name in name_list:
                if name not in self.state:
                    self.state[name] = {}
                self.state[name][s.task_id] = {'name': name_list, 'op': op_list, 'scene': s}

    def clean_task(self, scene):
        for s in Tools.object_list(scene):
            for task in self.state.values():
                if s.task_id in task:
                    del task[s.task_id]

    def del_task(self, scene, immediate=False):
        for s in Tools.object_list(scene):
            gtask.remove(s.task_id, immediate)

    def add_challenge(self):
        self.create_scene(task='health >= 1000')

    def del_challenge(self):
        pass

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
            attr = dict([(name, getattr(gmaze.herostate, name)) for name in task['name']])
            if name == task['name'][0]:
                gtask.achieve(scene.task_id, attr[name] - scene.attr[name])
            for name, op in task['op']:
                if not op(attr[name], scene.attr[name]):
                    break
            else:
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
