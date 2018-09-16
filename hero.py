# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from setting import MazeBase, MazeSetting

from random import randint

#每一个level的基础数值
class HeroBase:
    def __init__(self):
        self.level = -1
        self.health = 1000
        self.attack = 10
        self.defence = 10

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

    def bind(self, color, label):
        self.__bind[color] = label
        self[color] = self[color]


#实时状态，bind将状态绑定到label上，可以实时显示
class HeroState:
    __bind = {}

    def __init__(self, herobase):
        self.floor = 0
        self.health = herobase.health
        self.attack = herobase.attack
        self.defence = herobase.defence

        self.key = HeroStateDict()
        for color in MazeBase.Value.Color.total:
            self.key[color] = herobase.key[color]

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name in self.__bind:
            text = str(value)
            if name == 'floor':
                text = '{} F'.format(text)
            self.__bind[name].text = text

    def bind(self, name, label):
        self.__bind[name] = label
        value = getattr(self, name)
        setattr(self, name, value)


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
    wall = 2
    wall_dynamic = 1
    weapon = 1

    def __init__(self, maze, row, col, **kwargs):
        self.maze = maze
        self.row = row
        self.col = col
        self.pos = maze.maze_info[0]['init']
        self.wall = 2
        self.wall_dynamic = 1
        self.weapon = 1

    @property
    def name(self):
        return 'hero-{}-{}'.format(self.color, self.key)

    def isfloor(self, floor):
        if self.maze.is_boss_floor(floor - 1): #往上时楼层还不存在
            return True
        if floor in self.maze.maze_info: #楼层存在
            stair = self.maze.maze_info[floor]['stair']
            if self.floor == floor + 1: #下楼
                if not self.maze.is_boss_floor(floor) and MazeBase.Value.Stair.up in stair: #楼梯存在
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
        if self.maze.is_boss_floor(floor - 1):
            self.maze.update()
            self.wall = randint(1, 3)
            self.weapon = randint(1, 5)

        update_pos = None
        self.old_pos = self.pos
        if self.isfloor(floor):
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
