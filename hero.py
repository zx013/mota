# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from setting import MazeBase, MazeSetting
from cache import Config, Music

from random import randint

#每一个level的基础数值
class HeroBase:
    def __init__(self):
        self.level = -1
        self.health = 1000
        self.attack = 10
        self.defence = 10
        self.gold = 0
        self.experience = 0

        self.key = {
            MazeBase.Value.Color.yellow: 0,
            MazeBase.Value.Color.blue: 0,
            MazeBase.Value.Color.red: 0,
            MazeBase.Value.Color.green: 0
        }
        self.base = 1

        self.boss_attack = 0
        self.boss_defence = 0

    def update(self):
        self.level += 1
        self.floor = self.level * MazeSetting.base_floor + 1
        self.base = int((self.attack + self.defence) * 0.5 * MazeSetting.attribute_value) + 1

    @property
    def floor_start(self):
        return self.level * MazeSetting.base_floor + 1

    @property
    def floor_end(self):
        return (self.level + 1) * MazeSetting.base_floor


#key的绑定
class HeroStateDict(dict):
    __bind = {}

    def __getitem__(self, color):
        return self.__dict__[color]

    def __setitem__(self, color, value):
        self.__dict__[color] = value
        if color in self.__bind:
            self.__bind[color].text = str(value)

    def set_color(self, color):
        for key, label in self.__bind.items():
            label.color = color

    def bind(self, color, label):
        self.__bind[color] = label

    def active(self):
        for color in self.__bind.keys():
            self[color] = self[color]


#实时状态，bind将状态绑定到label上，可以实时显示
class HeroState:
    __bind = {}

    def __init__(self, herobase):
        self.schedule = ''
        self.progress = 0 #保存update时的进度
        self.floor = 0
        self.health = herobase.health
        self.attack = herobase.attack
        self.defence = herobase.defence
        self.gold = herobase.gold
        self.experience = herobase.experience

        self.key = HeroStateDict()
        for color in MazeBase.Value.Color.total:
            self.key[color] = herobase.key[color]

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name in self.__bind:
            label = self.__bind[name]
            text = str(value)
            if name == 'floor':
                text = '{} F'.format(text)
            elif name == 'health':
                if value < 100:
                    label.color = (1, 0, 0, 1) #红色
                elif value < 200:
                    label.color = (1, 0.5, 0, 1) #橙色
                elif value < 500:
                    label.color = (1, 1, 0.5, 1) #浅黄
                elif value < 2000:
                    label.color = (0.5, 1, 0.5, 1) #浅绿
                else:
                    label.color = (0, 1, 0, 1) #绿色
            label.text = text
        elif name == 'wall':
            color = self.get_color(value)
            for key, label in self.__bind.items():
                label.color = color.get(key, color['color'])
            self.key.set_color(color['key'])

    #可以加入缓存
    def get_color(self, wall):
        default = {
            'color': (1, 1, 1, 1),
            'title': (1, 1, 1, 1),
            'floor': (1, 1, 1, 1),
            'health': (0.5, 1, 0.5, 1),
            'attack': (1, 0.5, 0.5, 1),
            'defence': (0.5, 0.5, 1, 1),
            'gold': (1, 0.84, 0, 1),
            'experience': (0.53, 0.81, 0.92, 1),
            'key': (1, 1, 0.5, 1)
        }

        color = {}
        for key, val in Config.config[wall].items():
            if 'color' not in key:
                continue
            if '-' in key:
                key = key.split('-')[1]
            color[key] = val

        return dict(default, **color)

    def update(self, schedule, progress=0, reset=False):
        self.schedule = schedule
        if reset:
            progress = 0
        else:
            progress += progress
            if progress > 100:
                progress = 100
        self.progress = progress

    def bind(self, name, label):
        self.__bind[name] = label

    #所有bind之后，使用active激活，使初始化时能够显示数字，在bind中直接设置会导致后续设置和开始的重叠
    def active(self):
        for name in self.__bind.keys():
            value = getattr(self, name)
            setattr(self, name, value)
        self.key.active()


class Opacity:
    opacity = 1.0
    minimum = 0.2
    maximum = 1.0
    step = 0.2
    down = True

    dt = 0.1
    dtp = 0

    Run = 1
    Turn = 2
    End = 3

    def next(self, dt):
        if not self.active(dt):
            return self.Run

        if self.down:
            self.opacity -= self.step
            if self.opacity <= self.minimum:
                self.down = False
                return self.Turn
        else:
            self.opacity += self.step
            if self.opacity >= self.maximum:
                self.down = True
                return self.End
        return self.Run

    def active(self, dt):
        self.dtp += dt
        if self.dtp >= self.dt:
            self.dtp = 0
            return True
        return False


class Hero:
    color = 'blue' #颜色
    key = 'down' #朝向
    old_pos = (1, 0, 0)
    pos = (1, 0, 0)
    move_list = []

    opacity = Opacity() #不透明度
    stair = None #是否触发上下楼的动作
    action = set() #执行动画的点

    __wall = 2
    __wall_max = 3
    __wall_dynamic = 1
    __wall_dynamic_max = 1 #暂时没有使用
    __weapon = 1
    __weapon_max = 5

    def __init__(self, maze, **kwargs):
        self.maze = maze
        self.pos = maze.maze_info[0]['init']
        self.__wall = 2
        self.__wall_dynamic = 1
        self.__weapon = 1
        self.maze.herostate.wall = self.wall

    @property
    def name(self):
        return 'hero-{}-{}'.format(self.color, self.key)

    @property
    def wall(self):
        return 'wall-{:0>2}'.format(self.__wall)

    @property
    def wall_dynamic(self):
        return 'wall-dynamic-{:0>2}'.format(self.__wall_dynamic)

    @property
    def weapon_attack(self):
        return 'weapen-attack-{:0>2}'.format(self.__weapon)

    @property
    def weapon_defence(self):
        return 'weapen-defence-{:0>2}'.format(self.__weapon)


    def isfloor(self, floor):
        if self.maze.is_boss_floor(floor - 1): #往上时楼层还不存在
            return True
        if floor in self.maze.maze_info: #楼层存在
            stair = self.maze.maze_info[floor]['stair']
            if self.floor == floor + 1: #下楼
                if not self.maze.is_initial_floor(floor) and not self.maze.is_boss_floor(floor) and MazeBase.Value.Stair.up in stair: #楼梯存在
                    return True
            elif self.floor == floor - 1: #上楼
                if MazeBase.Value.Stair.down in stair:
                    return True
        return False

    @property
    def floor(self):
        return self.pos[0]

    @floor.setter
    def floor(self, floor):
        if self.floor == floor - 1:
            if self.maze.is_initial_floor(floor - 1) or self.maze.is_boss_floor(floor - 1):
                Music.background(change=True)
                self.maze.update()
                if self.maze.is_boss_floor(floor - 1):
                    self.__wall = randint(1, self.__wall_max)
                    self.__weapon = randint(1, self.__weapon_max)
                    self.maze.herostate.wall = self.wall

        update_pos = None
        self.old_pos = self.pos
        if self.isfloor(floor) and floor in self.maze.maze_info:
            stair = self.maze.maze_info[floor]['stair']
            if self.floor == floor + 1: #下楼
                update_pos = set(stair[MazeBase.Value.Stair.up]).pop()
            elif self.floor == floor - 1: #上楼
                update_pos = set(stair[MazeBase.Value.Stair.down]).pop()

        if update_pos:
            self.pos = update_pos
            self.maze.herostate.floor = self.floor

    @property
    def floor_up(self):
        return self.floor + self.isfloor(self.floor + 1)

    @property
    def floor_down(self):
        return self.floor - self.isfloor(self.floor - 1)

    #移动到的位置
    def move_pos(self, key):
        self.key = key
        key_map = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        floor, x1, y1 = self.pos
        x2, y2 = key_map.get(self.key, (0, 0)) #将key转换为具体方向
        return (floor, x1 + x2, y1 + y2)

    def move(self, key):
        self.old_pos = self.pos
        self.pos = self.move_pos(key)
