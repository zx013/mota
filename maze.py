#-*- coding:utf-8 -*-
import os
import random
import pickle
from functools import reduce

from setting import MazeBase, MazeSetting
from cache import Config
from hero import HeroBase, HeroState
from tools import Tools, LoopException


class TreeNode:
    def __init__(self, area, crack, special=False):
        self.Area = area #节点包含的区域
        self.Crack = crack
        self.Cover = self.Area | self.Crack

        self.Index = -1 #用于计算
        self.Forward = {} #节点之前的节点
        self.Backward = {} #节点之后的节点
        self.Up = None #上一层的开始节点
        self.Down = None #下一层的开始节点
        self.UpPos = None
        self.DownPos = None

        self.Deep = -1 #深度，离楼梯间最短路径的最短距离
        self.Special = special #特殊空间
        self.Space = len(area) #空间大小

        self.Door = 0
        self.Key = {
            MazeBase.Value.Color.yellow: 0,
            MazeBase.Value.Color.blue: 0,
            MazeBase.Value.Color.red: 0,
            MazeBase.Value.Color.green: 0
        }

        self.AttackGem = {
            MazeBase.Value.Gem.small: 0,
            MazeBase.Value.Gem.big: 0,
            MazeBase.Value.Gem.large: 0
        }

        self.DefenceGem = {
            MazeBase.Value.Gem.small: 0,
            MazeBase.Value.Gem.big: 0,
            MazeBase.Value.Gem.large: 0
        }

        self.Potion = {
            MazeBase.Value.Potion.red: 0,
            MazeBase.Value.Potion.blue: 0,
            MazeBase.Value.Potion.yellow: 0,
            MazeBase.Value.Potion.green: 0
        }

        self.IsDoor = False
        self.IsMonster = False
        self.IsElite = False
        self.IsBoss = False

        self.DoorPos = None
        self.MonsterPos = None

        #英雄到达区域时获得的宝石属性总和，该值用来设置怪物
        self.Attack = 0
        self.Defence = 0

        self.Monster = None
        self.Damage = 0

        #圣水，开始时放置，用来调整第一个节点无法放置足够药水的问题
        self.HolyWater = 0

    @property
    def floor(self):
        return list(self.Area)[0][0]

    @property
    def space(self):
        space = len(self.Area)
        if self.Down:
            space -= 1
        if self.Up:
            space -= 1
        if self.Door and self.Monster:
            space -= 1
        space -= sum(self.Key.values())
        space -= sum(self.AttackGem.values())
        space -= sum(self.DefenceGem.values())
        space -= sum(self.Potion.values())
        if self.HolyWater:
            space -= 1
        return space

    @property
    def start_floor(self):
        return self.boss_floor - MazeSetting.base_floor + 1

    @property
    def boss_floor(self):
        return int((self.floor - 1) / MazeSetting.base_floor + 1) * MazeSetting.base_floor

    @property
    def forbid(self):
        return filter(lambda x: Pos.inside(x) and (not (Pos.beside(x) & self.Crack)), reduce(lambda x, y: x ^ y, map(lambda x: Pos.corner(x) - self.Cover, self.Crack)))


class MonsterInfo:
    path = 'monster'
    data_fluctuate = 10
    data_range = 20

    base = {'level': 50, 'health': 100, 'ismagic': 0}
    data = {}

    @staticmethod
    def load():
        data = MonsterInfo.data
        for key, config in Config.config.items():
            if 'hero' in key:
                continue
            if not config['path'].startswith(os.path.join('data', MonsterInfo.path)):
                continue
            key_list = key.split('-')
            if len(key_list) != 2:
                continue

            key1, key2 = key_list
            if key1 not in data:
                data[key1] = {}
            if key2 not in data[key1]:
                data[key1][key2] = {}

            for name in MonsterInfo.base:
                if name not in data[key1][key2]:
                    data[key1][key2][name] = MonsterInfo.base[name]
                if name in config and config[name].isdigit():
                    data[key1][key2][name] = int(config[name])


class Pos:
    @staticmethod
    def inside(pos):
        z, x, y = pos
        if 0 < x < MazeSetting.rows + 1:
            if 0 < y < MazeSetting.cols + 1:
                return True
        return False

    @staticmethod
    def add(pos, move):
        z1, x1, y1 = pos
        x2, y2 = move
        return (z1, x1 + x2, y1 + y2)

    @staticmethod
    def sub(pos1, pos2):
        z1, x1, y1 = pos1
        z2, x2, y2 = pos2
        return (x1 - x2, y1 - y2)

    @staticmethod
    def beside(pos):
        z, x, y = pos
        return {(z, x - 1, y), (z, x + 1, y), (z, x, y - 1), (z, x, y + 1)}

    @staticmethod
    def corner(pos):
        z, x, y = pos
        return {(z, x - 1, y - 1), (z, x - 1, y + 1), (z, x + 1, y - 1), (z, x + 1, y + 1)}

    @staticmethod
    def around(pos):
        z, x, y = pos
        return {(z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1), (z, x, y - 1), (z, x, y + 1), (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1)}

    @staticmethod
    def inline(pos_list):
        z, x, y = map(lambda x: len(set(x)), zip(*pos_list))
        if z == 1 and (x == 1 or y == 1):
            return True
        return False


class Maze:
    def __init__(self):
        self.maze = {}
        self.maze_map = {} #每一层不同点的分类集合
        self.maze_info = {} #每一层的信息，node, stair等
        self.monster = {}
        self.herobase = HeroBase()
        self.herostate = HeroState(self.herobase)
        self.set_init()
        MonsterInfo.load()

    def init(self, floor):
        for key in list(self.maze.keys()):
            if key < floor - MazeSetting.save_floor:
                del self.maze[key]
                del self.maze_map[key]
                del self.maze_info[key]
        self.maze[floor] = [[[0, 0] for j in range(MazeSetting.cols + 2)] for i in range(MazeSetting.rows + 2)]
        self.maze_map[floor] = {MazeBase.Type.Static.ground: set()}
        self.maze_info[floor] = {}
        for i in range(MazeSetting.rows + 2):
            for j in range(MazeSetting.cols + 2):
                if i in (0, MazeSetting.rows + 1) or j in (0, MazeSetting.cols + 1):
                    self.maze[floor][i][j][0] = MazeBase.Type.Static.wall
                    self.maze[floor][i][j][1] = MazeBase.Value.Wall.static
                else:
                    self.maze[floor][i][j][0] = MazeBase.Type.Static.ground
                    self.maze_map[floor][MazeBase.Type.Static.ground].add((floor, i, j))

        if self.is_boss_floor(floor):
            self.monster = {}

    def outside(self, pos):
        z, x, y = pos
        if x < 1 or x > MazeSetting.rows:
            return True
        if y < 1 or y > MazeSetting.cols:
            return True
        return False

    #大小为5时出现错误，可能是由于没有楼梯导致的
    def get_type(self, pos):
        z, x, y = pos
        return self.maze[z][x][y][0]

    def get_value(self, pos):
        z, x, y = pos
        return self.maze[z][x][y][1]

    def set_type(self, pos, value):
        z, x, y = pos
        if self.outside(pos):
            return
        type = self.maze[z][x][y][0]
        self.maze_map[z].setdefault(type, set())
        self.maze_map[z].setdefault(value, set())
        self.maze_map[z][type].remove(pos)
        self.maze_map[z][value].add(pos)
        self.maze[z][x][y][0] = value

    def set_value(self, pos, value):
        z, x, y = pos
        self.maze[z][x][y][1] = value

    def get_beside(self, pos, type):
        return {(z, x, y) for z, x, y in Pos.beside(pos) if self.maze[z][x][y][0] == type}

    def get_beside_except(self, pos, type):
        return {(z, x, y) for z, x, y in Pos.beside(pos) if self.maze[z][x][y][0] != type}

    def get_corner(self, pos, type):
        return {(z, x, y) for z, x, y in Pos.corner(pos) if self.maze[z][x][y][0] == type}

    def get_around(self, pos, type):
        return {(z, x, y) for z, x, y in Pos.around(pos) if self.maze[z][x][y][0] == type}


    def get_extend(self, pos, type):
        extend = set()
        for beside in self.get_beside(pos, type):
            move = Pos.sub(beside, pos)
            next = beside
            while self.get_type(next) == type:
                beside = next
                next = Pos.add(beside, move)
            extend.add(beside)
        return extend


    #在floor层的type类型的区域中寻找符合func要求的点
    def find_pos(self, floor, type, func=None):
        if type not in self.maze_map[floor]:
            return set()
        if func:
            return {pos for pos in self.maze_map[floor][type] if func(pos)}
        else:
            return set(self.maze_map[floor][type])


    def is_pure(self, pos):
        if len(self.get_beside(pos, MazeBase.Type.Static.wall)) != 1:
            return False
        z, x, y = zip(*self.get_around(pos, MazeBase.Type.Static.wall))
        if len(set(x)) != 1 and len(set(y)) != 1:
            return False
        return True

    def get_pure(self, floor):
        #如果需要提高速度，每次放置wall时改变该值
        ground = self.maze_map[floor][MazeBase.Type.Static.ground] - self.maze_info[floor]['special']
        return {pos for pos in ground if self.is_pure(pos)}

    def is_wall(self, wall):
        for pos in wall[1:-1]:
            if self.get_beside(pos, MazeBase.Type.Static.wall):
                return False
        return True

    def get_wall(self, pos):
        wall = []
        move = Pos.sub(pos, self.get_beside(pos, MazeBase.Type.Static.wall).pop())
        while self.get_type(pos) == MazeBase.Type.Static.ground:
            wall.append(pos)
            pos = Pos.add(pos, move)
        return wall


    def is_rect(self, pos, rect1, rect2, row, col):
        floor, x, y = pos
        if x + row > MazeSetting.rows + 2 or y + col > MazeSetting.cols + 2:
            return False
        for i in range(row):
            for j in range(col):
                if self.get_type((floor, x + i, y + j)) != rect1[i][j]:
                    return False
        if rect2:
            for i in range(row):
                for j in range(col):
                    if rect2[i][j]:
                        type, value = rect2[i][j]
                        if type:
                            self.set_type((floor, x + i, y + j), type)
                        if value:
                            self.set_value((floor, x + i, y + j), value)
        return True

    #查找矩形，设置rect2的话则用rect2替换找到的矩形
    def find_rect(self, floor, rect1, rect2=None):
        _rect1 = list(zip(*rect1))
        _rect2 = list(zip(*rect2) if rect2 else None)
        row = len(rect1)
        col = len(_rect1)
        pos_list = [(floor, i, j) for i in range(0, MazeSetting.rows + 2) for j in range(0, MazeSetting.cols + 2)]
        random.shuffle(pos_list)
        for pos in pos_list:
            self.is_rect(pos, rect1, rect2, row, col)
            self.is_rect(pos, _rect1, _rect2, col, row)


    #获取pos的类型area, road, end
    def pos_type(self, pos):
        beside = self.get_beside(pos, MazeBase.Type.Static.ground)
        if len(beside) >= 3:
            return MazeBase.NodeType.area_normal
        if len(beside) == 1:
            return MazeBase.NodeType.road_corner
        if len(beside) == 2:
            (z1, x1, y1), (z2, x2, y2) = beside
            if x1 == x2 or y1 == y2:
                return MazeBase.NodeType.road_normal
            if self.get_type((z2, x2, y1) if pos == (z1, x1, y2) else (z1, x1, y2)) == MazeBase.Type.Static.wall:
                return MazeBase.NodeType.road_normal
            return MazeBase.NodeType.area_corner
        return MazeBase.NodeType.none

    #获取一片区域
    def get_area(self, pos):
        area = set()
        beside = set([pos])

        while beside:
            pos = beside.pop()
            area.add(pos)
            beside = beside | self.get_beside(pos, MazeBase.Type.Static.ground) - area
        return area


    def is_crack(self, pos):
        beside = self.get_beside(pos, MazeBase.Type.Static.ground)
        if len(beside) != 2:
            return False
        (z1, x1, y1), (z2, x2, y2) = beside
        if x1 != x2 and y1 != y2:
            return False
        return True

    def get_crack(self, floor):
        return self.find_pos(floor, MazeBase.Type.Static.wall, self.is_crack)

    def node_info(self, floor):
        self.maze_info[floor]['node'] = set()
        ground = self.find_pos(floor, MazeBase.Type.Static.ground)

        crack_list = self.get_crack(floor) #可打通的墙
        while ground:
            pos = None
            around = []
            area = self.get_area(ground.pop())
            for pos in area:
                around.append(self.get_beside(pos, MazeBase.Type.Static.wall))
            crack = reduce(lambda x, y: x | y, around) & crack_list
            node = TreeNode(area=area, crack=crack, special=pos in self.maze_info[floor]['special'])
            self.maze_info[floor]['node'].add(node)
            ground -= area

    def find_node(self, pos):
        z, x, y = pos
        for node in self.maze_info[z]['node']:
            if pos in node.Area:
                return node

    def merge_rect(self, floor):
        wall = MazeBase.Type.Static.wall
        ground = MazeBase.Type.Static.ground
        rect1 = [[wall, wall, wall, wall],
                [wall, ground, ground, wall],
                [wall, wall, wall, wall],
                [wall, ground, ground, wall],
                [wall, wall, wall, wall]]
        rect2 = [[0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, (ground, 0), (ground, 0), 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]]
        self.find_rect(floor, rect1, rect2)

    def is_initial_floor(self, floor):
        if floor:
            return False
        return True

    def is_boss_floor(self, floor):
        if floor <= 0:
            return False
        if not floor % MazeSetting.base_floor:
            return True
        return False



    def get_rect(self, pos, width, height):
        z, x, y = pos
        rect = set()
        for i in range(x, x + width):
            for j in range(y, y + height):
                rect.add((z, i, j))
        return rect

    def get_rect_crack(self, pos, width, height):
        z, x, y = pos
        return self.get_rect((z, x - 1, y - 1), width + 2, height + 2) - self.get_rect(pos, width, height)

    #特殊区域，一块较大的矩形
    def create_special(self, floor):
        self.maze_info[floor]['special'] = set()
        if self.is_initial_floor(floor):
            pass
        elif self.is_boss_floor(floor): #boss层只有一个特殊区域
            width = MazeSetting.rows // 3
            if width < 1:
                width = 1
            height = MazeSetting.cols // 3
            if height < 1:
                height = 1
            while True:
                x = random.randint(1, MazeSetting.rows - width + 1)
                if x == 2 or x == MazeSetting.rows - width:
                    continue
                break
            while True:
                y = random.randint(1, MazeSetting.cols - height + 1)
                if y == 2 or y == MazeSetting.cols - height:
                    continue
                break

            pos_list = [(floor, x, y)]
            for pos in pos_list:
                area = self.get_rect(pos, width, height)
                crack = self.get_rect_crack(pos, width, height)
                for pos in crack:
                    self.set_type(pos, MazeBase.Type.Static.wall)
                    self.set_value(pos, MazeBase.Value.Wall.static)
                self.maze_info[floor]['special'] |= area


    def create_wall(self, floor):
        pure = True
        while pure:
            pure = self.get_pure(floor)
            while pure:
                pos = random.choice(tuple(pure))
                wall = self.get_wall(pos)
                if self.is_wall(wall):
                    for pos in wall:
                        self.set_type(pos, MazeBase.Type.Static.wall)
                        self.set_value(pos, MazeBase.Value.Wall.static)
                    break
                else:
                    pure -= set(wall)
        self.merge_rect(floor)
        self.node_info(floor)


    def crack_wall(self, floor):
        #special区域只开一个口
        #crack_list = self.get_crack(floor) #可打通的墙

        next_node = list(self.maze_info[floor]['node'])
        crack_set = set() #已设置墙和未设置墙区域之间可打通的墙
        special_set = set()

        while next_node:
            if not crack_set:
                node = random.choice(list(filter(lambda x: not x.Special, next_node)))
            else:
                crack_pos = random.choice(list(crack_set - special_set))
                #该区域和上一个区域之间的墙
                self.set_type(crack_pos, MazeBase.Type.Static.door)
                #self.set_value(crack_pos, MazeBase.Value.Color.yellow)

                for node in next_node:
                    if crack_pos in node.Crack:
                        break
            if node.Special:
                special_set |= node.Crack

            crack_set = (crack_set | node.Crack) - (crack_set & node.Crack)
            next_node.remove(node)


    def get_stair_pos(self, floor):
        pos_set = set()
        if self.is_initial_floor(floor):
            return pos_set
        for node in self.maze_info[floor]['node']:
            if node.Special:
                continue
            for pos in node.Area:
                if self.pos_type(pos) == MazeBase.NodeType.road_normal:
                    continue
                if self.get_beside(pos, MazeBase.Type.Static.door):
                    continue
                pos_set.add((pos[1], pos[2]))

        #去除已设置的楼梯空间
        stair = self.maze_info[floor]['stair']
        pos_set -= set([(pos[1], pos[2]) for pos in stair[MazeBase.Value.Stair.down]])
        pos_set -= set([(pos[1], pos[2]) for pos in stair[MazeBase.Value.Stair.up]])
        return pos_set

    def create_stair(self, floor):
        self.maze_info[floor]['stair'] = {MazeBase.Value.Stair.up: set(), MazeBase.Value.Stair.down: set()}
        pos_set_down = self.get_stair_pos(floor)
        pos_set_up = self.get_stair_pos(floor - 1)
        pos_set = pos_set_down & pos_set_up #两层相同的位置
        if pos_set:
            pos_list = list(pos_set)
            random.shuffle(pos_list)
            pos = pos_list.pop()
            pos_down = (floor, pos[0], pos[1])
            pos_up = (floor - 1, pos[0], pos[1])
        else:
            if not self.is_initial_floor(floor - 1):
                print('No same pos, use different stair.')
            pos_list_down = list(pos_set_down)
            random.shuffle(pos_list_down)
            if pos_list_down:
                pos = pos_list_down.pop()
                pos_down = (floor, pos[0], pos[1])
            else:
                pos_down = None

            pos_list_up = list(pos_set_up)
            random.shuffle(pos_list_up)
            if pos_list_up:
                pos = pos_list_up.pop()
                pos_up = (floor - 1, pos[0], pos[1])
            else:
                pos_up = None

        if pos_down:
            self.maze_info[floor]['stair'][MazeBase.Value.Stair.down].add(pos_down)
        if pos_up:
            self.maze_info[floor - 1]['stair'][MazeBase.Value.Stair.up].add(pos_up)


    def create_tree(self, floor):
        self.maze_info[floor]['tree'] = set()
        for down in self.maze_info[floor]['stair'][MazeBase.Value.Stair.down]: #只有一个
            node = self.find_node(down)
            self.maze_info[floor]['tree'].add(node) #每一层起点

            node_list = [node]
            door_list = self.find_pos(floor, MazeBase.Type.Static.door)
            while node_list:
                node = node_list.pop()
                if self.is_boss_floor(node.floor) and node.Special:
                    node.IsBoss = True
                for door in door_list & node.Crack:
                    beside_pos = (self.get_beside(door, MazeBase.Type.Static.ground) - node.Area).pop()
                    beside_node = self.find_node(beside_pos)
                    node.Forward[door] = beside_node
                    beside_node.Backward[door] = node
                    node_list.append(beside_node)
                door_list -= node.Crack

        if self.is_initial_floor(floor - 1) or self.is_boss_floor(floor - 1):
            return
        pos_up = set(self.maze_info[floor - 1]['stair'][MazeBase.Value.Stair.up]).pop()
        node_up = self.find_node(pos_up)
        pos_down = set(self.maze_info[floor]['stair'][MazeBase.Value.Stair.down]).pop()
        node_down = self.find_node(pos_down)
        node_up.Up = node_down
        node_up.UpPos = pos_up
        node_down.Down = node_up
        node_down.DownPos = pos_down


    def adjust_corner(self, floor):
        corner = set()
        for door in self.find_pos(floor, MazeBase.Type.Static.door):
            for beside in self.get_beside(door, MazeBase.Type.Static.ground):
                if self.pos_type(beside) == MazeBase.NodeType.road_corner:
                    corner.add(beside)
        #print(len(corner), len(self.find_pos(floor, MazeBase.Type.Static.door)))

    def adjust_trap(self, floor):
        wall = MazeBase.Type.Static.wall
        ground = MazeBase.Type.Static.ground
        rect = [[wall, wall, ground, wall, wall],
                [wall, ground, ground, ground, wall],
                [wall, wall, ground, wall, wall]]

    def adjust_crack(self, floor):
        for node in self.ergodic(floor, 1):
            for pos, forward in node.Forward.items():
                crack = node.Crack & forward.Crack
                if len(crack) <= 1:
                    continue
                if not Pos.inline(crack):
                    continue
                if not len(crack) % 2:
                    continue
                #print(crack)

    def adjust(self, floor):
        self.adjust_corner(floor)
        self.adjust_trap(floor)
        self.adjust_crack(floor)


    #获取楼梯之间的最短路径
    def get_way(self, floor):
        node_list = [set(self.maze_info[floor]['tree']).pop()]

        index = 0
        while node_list:
            node_list_next = []
            for node in node_list:
                node.Index = index
            for node in node_list:
                if node.Up or node.IsBoss:
                    break
                node_list_next += [n for n in node.Forward.values() if n.Index < 0]
            if node.Up or node.IsBoss:
                break
            node_list = node_list_next
            index += 1

        node_list = [node]
        while True:
            backward = node.Backward.values()
            index -= 1
            for node in backward:
                if node.Index == index:
                    node_list.append(node)
                    break
            else:
                break
        return node_list[::-1]

    #获取深度
    def get_deep(self, node_list):
        deep = 0
        while node_list:
            node_list_next = []
            for node in node_list:
                node.Deep = deep
            for node in node_list:
                node_list_next += [n for n in node.Forward.values() if n.Deep < 0]
            node_list = node_list_next
            deep += 1

    def process(self, floor):
        node_list = self.get_way(floor)
        self.get_deep(node_list)


    #遍历树，简单区域（没有怪物，门内有相同钥匙）可以合并
    def ergodic_yield(self, floor, across=1):
        node_list = [set(self.maze_info[floor]['tree']).pop()]
        boss_node = None #boss区域放在最后
        while node_list:
            node = random.choice(node_list)
            node_list = list(set(node.Forward.values()) | set(node_list))
            if node.Up and floor + across > node.floor + 1:
                node_list.append(node.Up)
            node_list.remove(node)
            if node.IsBoss:
                boss_node = node
            else:
               yield node
        if boss_node:
            yield boss_node

    def ergodic(self, floor, across=1):
        ergodic_list = []
        for index, node in enumerate(self.ergodic_yield(floor, across)):
            node.Index = index
            ergodic_list.append(node)
        return ergodic_list


    def set_stair(self, floor):
        for up in self.maze_info[floor]['stair'][MazeBase.Value.Stair.up]:
            self.set_type(up, MazeBase.Type.Static.stair)
            self.set_value(up, MazeBase.Value.Stair.up)
        for down in self.maze_info[floor]['stair'][MazeBase.Value.Stair.down]:
            self.set_type(down, MazeBase.Type.Static.stair)
            self.set_value(down, MazeBase.Value.Stair.down)


    #重新确定space大小，需要排除掉楼梯的空间
    def set_space(self, node_list):
        for node in node_list:
            space = 0
            for pos in node.Area:
                if self.get_type(pos) == MazeBase.Type.Static.stair:
                    continue
                space += 1
            node.Space = space


    #空间小于2不放置key，空间越小放置key概率越小
    def __set_door(self, node_list):
        key_choice = {
            MazeBase.Value.Color.yellow: 60,
            MazeBase.Value.Color.blue: 20,
            MazeBase.Value.Color.red: 5,
            MazeBase.Value.Color.green: 1
        }

        key_choice_normal = {
            MazeBase.Value.Color.yellow: 2,
            MazeBase.Value.Color.blue: 1
        }

        key_choice_special = {
            MazeBase.Value.Color.red: 2,
            MazeBase.Value.Color.green: 1
        }

        #当前key的数量
        key_number = {
            MazeBase.Value.Color.yellow: 0,
            MazeBase.Value.Color.blue: 0,
            MazeBase.Value.Color.red: 0,
            MazeBase.Value.Color.green: 0
        }

        door_number = {
            MazeBase.Value.Color.yellow: 0,
            MazeBase.Value.Color.blue: 0,
            MazeBase.Value.Color.red: 0,
            MazeBase.Value.Color.green: 0
        }

        #前两个节点不设置门，第一个节点可能需要放置圣水，第一个门的钥匙需要放在第二个节点，不然可能导致没有空间放置圣水
        #红绿钥匙也可能在大片区域的入口（Deep == 1）
        length = len(node_list[-2:1:-1])
        door_total = random.randint(int(0.5 * length), int(0.7 * length))
        special_node = set()
        for node in node_list[-2:1:-1]:
            if node.Space < 2:
                continue
            if node.Deep == 0: #主路径上
                continue
            if node.Forward: #不是最终节点
                continue

            keys = []
            door = None
            is_yellows = False
            rand = random.random()
            if node.Deep > 3:
                total = key_number[MazeBase.Value.Color.red] + key_number[MazeBase.Value.Color.green]
                if rand < 1.2 - 0.3 * total: #红绿钥匙
                    node.IsMonster = True
                    keys.append(Tools.dict_choice(key_choice_special))
                    door = Tools.dict_choice(key_choice_normal)
                else:
                    rand = random.random()
                    if rand < 0.5:
                        pass
                    elif rand < 0.8: #多把黄钥匙
                        door = Tools.dict_choice(key_choice_normal)
                        node.IsMonster = True
                        is_yellows = True
                    else: #关键区域
                        door = Tools.dict_choice(key_choice_special)
            else:
                door = Tools.dict_choice(key_choice_normal)
                if door == MazeBase.Value.Color.yellow:
                    if rand < 0.3: #没有黄钥匙（宝石）
                        pass
                    elif rand < 0.7: #多把黄钥匙加怪物
                        node.IsMonster = True
                        is_yellows = True
                    else: #一把蓝钥匙（可能有怪物）
                        if random.random() < 0.3:
                            node.IsMonster = True
                        keys.append(MazeBase.Value.Color.blue)
                else:
                    if rand < 0.5:#没有黄钥匙（宝石）
                        pass
                    else: #多把黄钥匙（可能有怪物）
                        if random.random() < 0.3:
                            node.IsMonster = True
                        is_yellows = True
            if is_yellows == True:
                space = node.Space - node.IsMonster
                while random.random() < 0.5 and space > 0:
                    keys.append(MazeBase.Value.Color.yellow)
                    space -= 1

            for key in keys:
                key_number[key] += 1
                node.Key[key] += 1
                node.Space -= 1
            if door:
                door_number[door] += 1
                node.IsDoor = True
                node.Door = door

            special_node.add(node)


        key_set = {
            MazeBase.Value.Color.yellow: 0,
            MazeBase.Value.Color.blue: 0,
            MazeBase.Value.Color.red: 0,
            MazeBase.Value.Color.green: 0
        }

        door_set = {
            MazeBase.Value.Color.yellow: 0,
            MazeBase.Value.Color.blue: 0,
            MazeBase.Value.Color.red: 0,
            MazeBase.Value.Color.green: 0
        }

        #门比钥匙少
        for color in MazeBase.Value.Color.total:
            num = door_number[color] - key_number[color]
            if num < 0:
                num = -num
                door_set[color] = num
                door_total -= num

        #设置门的数量分配
        for i in range(door_total - sum(door_number.values())):
            door = Tools.dict_choice(key_choice)
            door_set[door] += 1

        #设置钥匙的数量分配
        for color in MazeBase.Value.Color.total:
            num = door_number[color] + door_set[color] - key_number[color]
            key_set[color] = num

        #放置门
        random_node = list(set(node_list[2:-1]) - set(special_node))
        random.shuffle(random_node)
        index = 0
        while sum(door_set.values()) > 0:
            index += 1
            if index > LoopException.retry:
                raise LoopException
            for node in random_node:
                door = None
                if door_set[MazeBase.Value.Color.red] + door_set[MazeBase.Value.Color.green]:
                    rand = random.random()
                    if node.Deep == 1:
                        if rand < 0.2:
                            door = Tools.dict_choice(key_choice_special)
                    if node.Deep == 2:
                        if rand < 0.1:
                            door = Tools.dict_choice(key_choice_special)

                else:
                    if random.random() < 0.3 * (node.Space - 2):
                        door = Tools.dict_choice(key_choice_normal)
                if door and door_set[door] > 0:
                    door_set[door] -= 1
                    node.IsDoor = True
                    node.Door = door
                    random_node.remove(node)

        #boss设置特殊门
        node = node_list[-1]
        door = Tools.dict_choice(key_choice_special)
        node.IsDoor = True
        node.Door = door
        key_set[door] += 1

        #下楼区域没有Backward，所以不设置门
        for node in node_list:
            if not node.Backward:
                if node.IsDoor:
                    node.IsDoor = False
                    node.Door = None
                if node.IsMonster:
                    node.IsMonster = False

        #放置key，使能够走通
        for pnode, node in Tools.iter_previous(node_list[1:]):
            door = node.Door
            if door:
                door_set[door] += 1
            for color in MazeBase.Value.Color.total:
                door_set[color] -= pnode.Key[color]
                if door_set[color] > 0:
                    random_node = []
                    #去除不需要放置钥匙的空间
                    for rnode in set(node_list[1:node.Index]):
                        if rnode.Space <= 1:
                            continue
                        if color != MazeBase.Value.Color.yellow:
                            #门里面有相同的钥匙
                            if rnode.Door == color:
                                continue
                            #不能拿到钥匙就可以开门
                            if [fnode for fnode in rnode.Forward.values() if fnode.Door == color]:
                                continue
                        random_node.append(rnode)
                    while door_set[color] > 0:
                        random.shuffle(random_node) #尽量分散放置
                        for rnode in random_node:
                            rnode.Key[color] += 1
                            rnode.Space -= 1
                            break
                        else:
                            #可以不跳出，将钥匙保留至初始或上一阶段的boss区域
                            print('Can not set key', color)
                            raise Exception
                        door_set[color] -= 1

        #删除多余的钥匙
        door_base = dict(door_set)
        for color in MazeBase.Value.Color.total:
            door_set[color] = 0

        #一定概率会出现无解的情况
        index = 0
        while sum(door_base.values()) < 0:
            index += 1
            if index > LoopException.retry:
                print('This will never run')
                raise LoopException

            for node, pnode in Tools.iter_previous(node_list[:0:-1]):
                door = node.Door
                if door:
                    door_set[door] += 1
                for color in MazeBase.Value.Color.total:
                    door_set[color] -= pnode.Key[color] #多余钥匙的数量
                    if door_set[color] < 0 and door_base[color] < 0:
                        while pnode.Key[color] > 0 and door_set[color] < 0: #有多余钥匙且当前单元有钥匙
                            pnode.Key[color] -= 1
                            pnode.Space += 1
                            door_set[color] += 1
                            door_base[color] += 1

    #设置失败时清空状态重新设置，连续失败多次后才重新生成
    def set_door(self, node_list):
        for i in range(10):
            try:
                self.__set_door(node_list)
                break
            except Exception as ex:
                print('Set door error, retry it.')
                for node in node_list:
                    node.IsDoor = False
                    node.Door = MazeBase.Value.Color.none
                    node.IsMonster = False
                    for color in MazeBase.Value.Color.total:
                        node.Space += node.Key[color]
                        node.Key[color] = 0
        else:
            print('Can not find a way to set door.')
            raise Exception


    def set_monster(self, node_list):
        #没有door的需要放置monster
        #若空间小于等于1，不能放怪物，第一个区域不放置
        for node in node_list[1:-1]:
            if not node.Backward:
                continue
            if node.Space == 0:
                continue

            ismonster = False
            if node.IsMonster:
                ismonster = True
            elif not node.IsDoor:
                ismonster = True
            elif random.random() < 0.3 * (node.Space - 2):
                ismonster = True
            if ismonster:
                node.IsMonster = True
                if node.IsDoor: #door will not in the area
                    node.Space -= 1

        for node in node_list:
            if not node.Backward:
                continue
            pos = set(node.Backward.keys()).pop()

            if node.IsDoor:
                node.DoorPos = pos
                if node.IsMonster:
                    beside = self.get_beside(pos, MazeBase.Type.Static.ground)
                    pos = (beside & node.Area).pop()
            if node.IsMonster:
                node.MonsterPos = pos


    #每个单元提升50%左右
    #应该根据当前属性分配，攻击高于防御时应提高防御宝石的数量，反之亦然
    def set_gem(self, node_list):
        gem_choice_normal = {
            MazeBase.Value.Gem.small: 10,
            MazeBase.Value.Gem.big: 1,
        }

        gem_choice_special = {
            MazeBase.Value.Gem.big: 10,
            MazeBase.Value.Gem.large: 1
        }
        #确保攻防加成接近
        gem_chance = 0.5

        total_attack = 0
        total_defence = 0

        #有门且放置的钥匙数小于等于1，必须放置宝物，第一个位置不放宝石，防止空间不够
        large_attack = False
        large_defence = False
        for node in node_list[1:-1]:
            if node.Space == 0:
                continue
            isgem = False
            if sum(node.Key.values()) == 0:
                isgem = True
            elif node.IsDoor and sum(node.Key.values()) == 1:
                isgem = True
            elif random.random() < 0.1 + 0.1 * node.Space:
                isgem = True
            if isgem:
                if node.Deep < 3 or node.Forward or sum(node.Key.values()) != 0:
                    gem = Tools.dict_choice(gem_choice_normal)
                else:
                    #剑盾需要放置在难以拿到的区域，同时要设置剑盾类型（显示类型）
                    #剑盾每种最多放置一个
                    if large_attack and large_defence:
                        gem = MazeBase.Value.Gem.big
                    else:
                        gem = Tools.dict_choice(gem_choice_special)
                if gem == MazeBase.Value.Gem.large and large_defence or random.random() < gem_chance:
                    itemgem = node.AttackGem
                    gem_chance -= 0.02 * gem
                    total_attack += gem
                    if gem == MazeBase.Value.Gem.large:
                        large_attack = True
                else:
                    itemgem = node.DefenceGem
                    gem_chance += 0.02 * gem
                    total_defence += gem
                    if gem == MazeBase.Value.Gem.large:
                        large_defence = True

                itemgem[gem] += 1
                node.Space -= 1

        if large_attack and large_defence:
            print('set sword and shield')
        elif large_attack:
            print('set sword')
        elif large_defence:
            print('set shield')


    def set_elite(self, node_list):
        #自动生成的elite总数大致8个左右，可能有靠近或连续的情况
        #将elite数量限制在elite种类数，保证每个elite都不同
        list_len = len(node_list) - 1 #除去boss
        elite_number = 0
        elite_max = min(len(MonsterInfo.data['elite']), int(MazeSetting.base_floor / 2)) #最大elite数
        elite_range = MazeSetting.base_floor #两个elite之间的间隔
        elite_enable = [False if n < int(list_len / 4) or n > list_len -  elite_range else True for n in range(list_len)] #开始若干节点不设置elite

        for frequency in range(3):
            index_list = [v for v in range(list_len)]
            random.shuffle(index_list)
            for index in index_list:
                node = node_list[index]
                if not node.IsMonster:
                    continue
                if elite_number >= elite_max:
                    break

                iselite = False

                if frequency == 0:
                    if node.AttackGem[MazeBase.Value.Gem.large] > 0 or node.DefenceGem[MazeBase.Value.Gem.large] > 0: #剑盾
                        iselite = True
                    elif node.AttackGem[MazeBase.Value.Gem.big] > 0 or node.DefenceGem[MazeBase.Value.Gem.big] > 0: #大宝石，如果有钥匙增加几率
                        if random.random() < 0.3 + 0.5 * sum(node.Key.values()):
                            iselite = True
                    elif node.AttackGem[MazeBase.Value.Gem.small] > 0 or node.DefenceGem[MazeBase.Value.Gem.small] > 0: #小宝石，概率取决于钥匙数量
                        if random.random() < 0.2 * sum(node.Key.values()):
                            iselite = True
                    elif node.Key[MazeBase.Value.Color.red] > 0 or node.Key[            MazeBase.Value.Color.green] > 0: #红绿钥匙
                        iselite = True
                    elif sum(node.Key.values()) >= 3: #大量钥匙
                        iselite = True
                elif frequency == 1:
                    #若elite数量不足时，在空间大的区域设置elite
                    if node.Space > elite_number:
                        iselite = True
                elif frequency == 2:
                    #还是不足时，设置普通的monster
                    iselite = True

                if iselite and elite_enable[index]:
                    node.IsElite = True
                    elite_number += 1
                    #范围内不再设置elite
                    for i in range(max(0, index - elite_range), min(list_len, index + elite_range)):
                        elite_enable[i] = False


    def set_attribute(self, node_list):
        for pnode, node in Tools.iter_previous(node_list):
            node.Attack = pnode.Attack
            node.Defence = pnode.Defence

            for gem in MazeBase.Value.Gem.total:
                node.Attack += gem * pnode.AttackGem[gem]
                node.Defence += gem * pnode.DefenceGem[gem]


    def get_damage(self, attack, defence, monster):
        monster_info = self.monster[monster[0]][monster[1]]
        monster_health = monster_info['health']
        monster_attack = monster_info['attack']
        monster_defence = monster_info['defence']

        if attack <= monster_defence:
            return float('inf')

        if monster_info['magic']:
            damage = (monster_health - 1) // (attack - monster_defence) * monster_attack
        else:
            damage = (monster_health - 1) // (attack - monster_defence) * (monster_attack - defence)
        if damage < 0:
            damage = 0

        return damage


    def apply_monster(self, node_list):
        while True:
            random_list = [[] for node in node_list if node.IsMonster and not node.IsElite]
            monster_length = len(random_list)
            for key1, data1 in MonsterInfo.data.items():
                if key1 in ('elite', 'boss'):
                    continue
                for key2, data2 in data1.items():
                    level = random.choice(range(max(0, data2['level'] - MonsterInfo.data_fluctuate), min(100, data2['level'] + MonsterInfo.data_fluctuate)))
                    minimum = max(0, int(float(level - MonsterInfo.data_range) * monster_length / 100))
                    maximum = min(monster_length, int(float(level + MonsterInfo.data_range) * monster_length / 100))
                    for index in range(minimum, maximum):
                        random_list[index].append((key1, key2))

            if [] not in random_list:
                break
            print('random has empty data.')

        index = 0
        for node in node_list:
            if not node.IsMonster or node.IsElite:
                continue
            random_data = random_list[index]
            node.Monster = random.choice(random_data)
            index += 1


    #理论上每个elite应该尽量不同，避免elite间隔太大导致的偏差
    def apply_elite(self, node_list):
        random_list = list(MonsterInfo.data['elite'].keys())
        random.shuffle(random_list)
        for node in node_list:
            if not node.IsElite:
                continue
            node.Monster = ('elite', random_list.pop())


    def apply_boss(self, node_list):
        node = node_list[-1]
        node.IsMonster = True
        node.IsBoss = True
        node.Monster = ('boss', random.choice(list(MonsterInfo.data['boss'])))
        if node.DoorPos:
            beside = self.get_beside(node.DoorPos, MazeBase.Type.Static.ground)
            node.MonsterPos = (beside & node.Area).pop()

        self.herobase.boss_attack = node.Attack
        self.herobase.boss_defence = node.Defence


    def adjust_monster(self, node_list):
        number_enable = [False for node in node_list]
        for number, node in enumerate(node_list):
            if not node.IsMonster:
                continue
            if number_enable[number] == True:
                continue

            monster = node.Monster
            monster_info = MonsterInfo.data[monster[0]][monster[1]]
            monster_health = monster_info['health'] - 10 + random.randint(0, 20)
            monster_ismagic = monster_info['ismagic']
            monster_number = []
            for number, node in enumerate(node_list):
                if node.IsMonster and node.Monster == monster:
                    monster_number.append(number)
                    number_enable[number] = True

            #monster_number跨度越大，越偏向于攻击，跨度越小，越偏向于防御
            #保证能够通过
            if monster_ismagic == True:
                attack = 20 + random.randint(1, 1 + len(monster_number))
            else:
                attack = node_list[monster_number[-1]].Defence + random.randint(1, 1 + len(monster_number))
            defence = node_list[monster_number[0]].Attack - random.randint(1, 1 + len(monster_number))

            #将伤害限制在范围内
            #这里陷入了死循环，应该是范围太大导致的
            index = 0
            while True:
                index += 1
                if index > LoopException.retry:
                    raise LoopException
                damage_list = []
                for number in monster_number:
                    node = node_list[number]
                    if monster_ismagic:
                        damage = (monster_health - 1) // (node.Attack - defence) * attack
                    else:
                        damage = (monster_health - 1) // (node.Attack - defence) * (attack - node.Defence)
                    damage_list.append(damage)
                    node.Damage = damage

                damage = damage_list[0]
                if node.IsBoss:
                    if damage < MazeSetting.boss_min:
                        attack += random.randint(1, 20)
                        continue
                    if damage > MazeSetting.boss_max:
                        defence -= 1
                        continue
                elif node.IsElite:
                    if damage < MazeSetting.elite_min:
                        attack += random.randint(1, 10)
                        continue
                    if damage > MazeSetting.elite_max:
                        defence -= 1
                        continue
                else:
                    if damage < MazeSetting.damage_min:
                        #第一个怪物伤害太低
                        attack += random.randint(1, 5)
                        continue
                    if damage > MazeSetting.damage_max:
                        #第一个怪物伤害太高
                        #正常来说，defence不会小于-100（即实际值小于0）
                        defence -= 1
                        continue
                if len([damage for damage in damage_list if damage < MazeSetting.damage_total_min]) >= MazeSetting.damage_total_num:
                    attack += 1
                    continue
                break

            #初始值不一定为100
            if monster[0] not in self.monster:
                self.monster[monster[0]] = {}
            self.monster[monster[0]][monster[1]] = {'health': monster_health, 'attack': attack, 'defence': defence, 'magic': monster_ismagic}


    #蒙特卡洛模拟获取尽可能的最优解
    def montecarlo(self, node_list, floor, across):
        min_damage = sum([node.Damage for node in node_list if node.IsMonster and not node.IsBoss])
        min_path = node_list
        boss = node_list[-1]

        number = 0
        while number < MazeSetting.montecarlo:
            total_damage = 0
            attack = 0
            defence = 0
            key = {
                MazeBase.Value.Color.yellow: 0,
                MazeBase.Value.Color.blue: 0,
                MazeBase.Value.Color.red: 0,
                MazeBase.Value.Color.green: 0
            }

            node_path = []
            node_list = [set(self.maze_info[floor]['tree']).pop()]
            node_len = len(node_list)
            random.shuffle(node_list)

            while node_list:
                node = None
                damage = 0
                for node in node_list:
                    if node.IsBoss:
                        continue
                    if node.IsDoor:
                        if key[node.Door] == 0:
                            continue
                    if node.IsMonster:
                        damage = self.get_damage(attack, defence, node.Monster)
                        if damage == float('inf'):
                            continue
                        if total_damage + damage > min_damage:
                            continue
                    break
                else: #该次遍历失败
                    break

                for color in MazeBase.Value.Color.total:
                    key[color] += node.Key[color]

                for gem in MazeBase.Value.Gem.total:
                    attack += gem * node.AttackGem[gem]
                    defence += gem * node.DefenceGem[gem]

                total_damage += damage
                node_path.append(node)

                #随机插入到列表中
                for __node in list(set(node.Forward.values()) - set(node_list)):
                    node_list.insert(random.randint(0, node_len), __node)
                    node_len += 1

                if floor + across > node.floor + 1:
                    if node.Area & self.maze_info[node.floor]['stair'][MazeBase.Value.Stair.up]:
                        __node = set(self.maze_info[node.floor + 1]['tree']).pop()
                        node_list.insert(random.randint(0, node_len), __node)
                        node_len += 1

                node_list.remove(node)
                node_len -= 1

            number += 1

            #未找到解决路径
            if len(node_list) > 1:
                continue

            if not node_list[0].IsBoss:
                continue

            node_path.append(boss)
            #找到更优路径
            if min_damage > total_damage:
                print('find min %d, old is %d (%d)' % (total_damage, min_damage, number))
                min_damage = total_damage
                min_path = node_path


        #重设属性值
        self.set_attribute(min_path)
        #重置伤害值，设置血瓶时使用
        for node in min_path:
            if node.IsMonster:
                node.Damage = self.get_damage(node.Attack, node.Defence, node.Monster)

        return min_path


    #总是会少一点
    def set_potion(self, node_list):
        potion_choice = {
            MazeBase.Value.Potion.red: 27,
            MazeBase.Value.Potion.blue: 9,
            MazeBase.Value.Potion.yellow: 3,
            MazeBase.Value.Potion.green: 1
        }
        #需要的总数
        boss = node_list[-1]
        potion = boss.Damage - self.herostate.health
        potion += MazeSetting.remain_potion

        #预先放置一些，防止空的情况
        for node in node_list[1:-1]:
            #放置了特殊的物品可以不用放置其他的东西
            if node.AttackGem[MazeBase.Value.Gem.large] or node.DefenceGem[MazeBase.Value.Gem.large]:
                continue
            if node.Key[MazeBase.Value.Color.red] or node.Key[MazeBase.Value.Color.green]:
                continue

            pos_list = []
            for pos in node.Area:
                if self.get_type(pos) == MazeBase.Type.Static.ground:
                    pos_list.append(pos)
            space = len(pos_list)
            items = sum(node.AttackGem.values()) + sum(node.DefenceGem.values()) + sum(node.Key.values())
            if space < 4 or items > 1:
                continue

            color = Tools.dict_choice(potion_choice)
            node.Potion[color] += 1
            node.Space -= 1

            while random.random() < 0.5 and node.Space > 0:
                color = Tools.dict_choice(potion_choice)
                node.Potion[color] += 1
                node.Space -= 1

        #boss区域不设置potion
        for node in node_list[-2::-1]:
            for color in MazeBase.Value.Potion.total:
                potion -= color * node.Potion[color]

            while node.Space > 0 and potion > 0:
                if potion >= MazeBase.Value.Potion.green:
                    node.Potion[MazeBase.Value.Potion.green] += 1
                    potion -= MazeBase.Value.Potion.green
                    node.Space -= 1
                elif potion >= MazeBase.Value.Potion.yellow:
                    node.Potion[MazeBase.Value.Potion.yellow] += 1
                    potion -= MazeBase.Value.Potion.yellow
                    node.Space -= 1
                elif potion >= MazeBase.Value.Potion.blue:
                    node.Potion[MazeBase.Value.Potion.blue] += 1
                    potion -= MazeBase.Value.Potion.blue
                    node.Space -= 1
                else:
                    node.Potion[MazeBase.Value.Potion.red] += 1
                    potion -= MazeBase.Value.Potion.red
                    node.Space -= 1

            if node.IsMonster:
                potion += node.Damage

        #第一格空间不够，去除放置的所有血瓶，放置圣水
        if potion >= 0:
            node = node_list[0]
            for color in MazeBase.Value.Potion.total:
                potion += color * node.Potion[color]
                node.Potion[color] = 0

            #圣水为100的倍数
            node.HolyWater = potion + 1
            node.HolyWater = ((node.HolyWater - 1) // 100 + 1) * 100
            potion -= node.HolyWater
            print('set holy: %d' % node.HolyWater)
        print('best way: %d' % (MazeSetting.remain_potion - potion))


    def set_maze(self, node_list):
        for node in node_list:
            if node.DoorPos:
                self.set_type(node.DoorPos, MazeBase.Type.Static.door)
                self.set_value(node.DoorPos, node.Door)
            if node.MonsterPos:
                self.set_type(node.MonsterPos, MazeBase.Type.Active.monster)
                self.set_value(node.MonsterPos, node.Monster)

            pos_area = []
            pos_list = []

            for pos in node.Area:
                if self.get_type(pos) == MazeBase.Type.Static.ground:
                    pos_list.append(pos)

            #三面靠墙
            for pos in pos_list:
                beside = self.get_beside(pos, MazeBase.Type.Static.wall)
                if len(beside) == 3:
                    if self.get_type(pos) == MazeBase.Type.Static.ground:
                        pos_area.append(pos)
                        pos_list.remove(pos)

            #长条形，按顺序添加
            while pos_list:
                for pos in pos_list:
                    beside = self.get_beside(pos, MazeBase.Type.Static.ground)
                    if beside & set(pos_area):
                        pos_area.append(pos)
                        pos_list.remove(pos)
                        break
                else: #没有改变就退出
                    break

            #方形角上的
            for pos in pos_list:
                beside = self.get_beside(pos, MazeBase.Type.Static.wall)
                if len(beside) == 2:
                    pos_area.append(pos)
                    pos_list.remove(pos)

            #方形，按顺序添加
            while pos_list:
                for pos in pos_list:
                    beside = self.get_beside(pos, MazeBase.Type.Static.ground)
                    if beside & set(pos_area):
                        pos_area.append(pos)
                        pos_list.remove(pos)
                        break
                else:
                    break

            #剩下一些特殊的情况
            pos_area += pos_list

            for gem in MazeBase.Value.Gem.total[::-1]:
                for i in range(node.AttackGem[gem]):
                    pos = pos_area.pop(0)
                    self.set_type(pos, MazeBase.Type.Item.attack)
                    self.set_value(pos, gem)
                for i in range(node.DefenceGem[gem]):
                    pos = pos_area.pop(0)
                    self.set_type(pos, MazeBase.Type.Item.defence)
                    self.set_value(pos, gem)

            for color in MazeBase.Value.Color.total[::-1]:
                for i in range(node.Key[color]):
                    pos = pos_area.pop(0)
                    self.set_type(pos, MazeBase.Type.Item.key)
                    self.set_value(pos, color)

            for potion in MazeBase.Value.Potion.total[::-1]:
                for i in range(node.Potion[potion]):
                    pos = pos_area.pop(0)
                    self.set_type(pos, MazeBase.Type.Item.potion)
                    self.set_value(pos, potion)

            if node.HolyWater > 0:
                pos = pos_area.pop(0)
                self.set_type(pos, MazeBase.Type.Item.holy)
                self.set_value(pos, node.HolyWater)


    def set_init(self):
        floor = 0
        middle = int((MazeSetting.cols + 1) / 2)
        self.init(floor)

        pos = (floor, MazeSetting.rows, middle)
        self.set_type(pos, MazeBase.Type.Static.init)
        self.set_value(pos, 0)
        self.maze_info[floor]['init'] = pos

        pos = (floor, 1, middle)
        self.set_type(pos, MazeBase.Type.Static.stair)
        self.set_value(pos, MazeBase.Value.Stair.up)
        self.maze_info[floor]['stair'] = {}
        self.maze_info[floor]['stair'][MazeBase.Value.Stair.up] = set((pos,))

        pos_list = []
        for i in range(1, 4):
            pos_list += [(floor, i, middle - 1), (floor, i, middle + 1)]
        for pos in pos_list:
            self.set_type(pos, MazeBase.Type.Static.wall)
            self.set_value(pos, MazeBase.Value.Wall.static)

        pos_list = []
        for i in range(0, middle - 2):
            pos_list += [(floor, MazeSetting.rows - i, middle - i - 1), (floor, MazeSetting.rows - i, middle + i + 1)]
            pos_list += [(floor, MazeSetting.rows - i - 3, middle - i - 1), (floor, MazeSetting.rows - i - 3, middle + i + 1)]
        for pos in pos_list:
            self.set_type(pos, MazeBase.Type.Static.wall)
            self.set_value(pos, MazeBase.Value.Wall.dynamic)

        pos = (floor, 1, 1)
        self.set_type(pos, MazeBase.Type.Active.rpc)
        self.set_value(pos, MazeBase.Value.Rpc.wisdom)

        pos = (floor, 1, MazeSetting.cols)
        self.set_type(pos, MazeBase.Type.Active.rpc)
        self.set_value(pos, MazeBase.Value.Rpc.trader)

        pos = (floor, MazeSetting.rows, 1)
        self.set_type(pos, MazeBase.Type.Active.rpc)
        self.set_value(pos, MazeBase.Value.Rpc.thief)

        pos = (floor, MazeSetting.rows, MazeSetting.cols)
        self.set_type(pos, MazeBase.Type.Active.rpc)
        self.set_value(pos, MazeBase.Value.Rpc.fairy)

    def set_boss(self):
        pass

    def kill_boss(self, pos):
        area = self.get_area(pos)
        area.remove(pos)

        while True:
            pos = area.pop()
            if self.get_type(pos) == MazeBase.Type.Static.ground:
                self.set_type(pos, MazeBase.Type.Static.stair)
                self.set_value(pos, MazeBase.Value.Stair.up)
                break

    #先确定一个较优路线，再通过蒙特卡洛模拟逼近最优路线
    def set_item(self):
        for f in range(self.herobase.floor_start, self.herobase.floor_end + 1):
            self.set_stair(f)
        node_list = self.ergodic(self.herobase.floor_start, MazeSetting.base_floor)
        self.set_space(node_list)
        self.set_door(node_list)
        self.set_monster(node_list)
        self.set_gem(node_list)
        self.set_elite(node_list)
        self.set_attribute(node_list)
        self.apply_monster(node_list)
        self.apply_elite(node_list)
        self.apply_boss(node_list)
        self.adjust_monster(node_list)

        node_list = self.montecarlo(node_list, self.herobase.floor_start, MazeSetting.base_floor)
        self.set_potion(node_list)
        self.set_maze(node_list)


    #更新为具体数值
    def update_monster(self):
        for name1, info1 in self.monster.items():
            for name2, info2 in info1.items():
                info2['health'] *= self.herobase.base
                info2['attack'] *= self.herobase.base
                if not info2['magic']:
                    info2['attack'] += self.herobase.defence
                info2['defence'] *= self.herobase.base
                info2['defence'] += self.herobase.attack


    def update(self):
        self.herobase.update() #进入下一个level
        #set_items该值才会被刷新
        self.herobase.attack += self.herobase.base * self.herobase.boss_attack
        self.herobase.defence += self.herobase.base * self.herobase.boss_defence

        for i in range(3):
            try:
                for floor in range(self.herobase.floor_start, self.herobase.floor_end + 1):
                    self.init(floor)
                    self.create_special(floor)
                    self.create_wall(floor)
                    self.crack_wall(floor)
                    self.create_stair(floor)
                    self.create_tree(floor)
                    self.adjust(floor)

                #等楼梯设置好再进行
                for floor in range(self.herobase.floor_start, self.herobase.floor_end + 1):
                    self.process(floor)

                self.set_item()
                self.set_boss()
            except LoopException:
                #生成异常时重新生成
                print('loop reset')
                continue
            except Exception as ex:
                print('reset :', ex)
                continue
            break

        self.update_monster()


    def show(self, floor=None):
        for k in range(self.herobase.floor_start, self.herobase.floor_end + 1):
            if floor:
                k = floor
            print('floor :', k)
            for i in range(MazeSetting.rows + 2):
                line = ''
                for j in range(MazeSetting.cols + 2):
                    if self.get_type((k, i, j)) == MazeBase.Type.Static.ground:
                        line += '  '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Static.wall:
                        line += 'x '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Static.door:
                        line += 'o '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Active.monster:
                        line += 'm '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Item.key:
                        line += 'k '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Item.attack:
                        line += 'a '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Item.defence:
                        line += 'd '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Item.potion:
                        line += 'p '
                    elif self.get_type((k, i, j)) == MazeBase.Type.Item.holy:
                        line += 'h '
                    else:
                        line += str(self.get_value((k, i, j))) + ' '
                print(line)
            print()
            print()
            if floor:
                break
        import sys
        sys.stdout.flush()


    def save(self, num):
        record_dict = {
            'maze': self.maze, #迷宫构成
            'monster': self.monster, #怪物属性
            'herobase': self.herobase.__dict__, #等级状态
            'herostate': self.herostate.__dict__ #实时状态
        }

        if not os.path.exists(MazeSetting.save_dir):
            os.mkdir(MazeSetting.save_dir)
            print('save dir not exist.')
        record = pickle.dumps(record_dict, protocol=2)
        with open(MazeSetting.save_file(num), 'wb') as fp:
            fp.write(record)


    def load(self, num):
        try:
            with open(MazeSetting.save_file(num), 'rb') as fp:
                record = fp.read()

            record_dict = pickle.loads(record)
            self.maze = record_dict['maze']
            self.monster = record_dict['monster']
            for k, v in record_dict['herobase'].items():
                setattr(self, k, v)
            for k, v in record_dict['herostate'].items():
                setattr(self, k, v)
        except Exception as ex:
            print('load error: ', ex)


    def get_monster(self, monster):
        key1, key2 = monster
        return self.monster[key1][key2]


    #向外扩张，每一圈计数加一
    def find_around(self, pos_list, end_pos, num):
        around = set()
        for pos in pos_list:
            beside = self.get_beside_except(pos, MazeBase.Type.Static.wall)
            stair = self.get_beside(pos, MazeBase.Type.Static.stair)
            beside -= stair
            if end_pos in stair:
                beside.add(end_pos)
            around |= beside
        around -= pos_list | self.around[num - 1]
        return around

    #@except_default([])
    def find_path(self, start_pos, end_pos):
        move_map = {
            (1, 0): 'up',
            (-1, 0): 'down',
            (0, 1): 'left',
            (0, -1): 'right'
        }
        if self.get_type(end_pos) == MazeBase.Type.Static.wall:
            return []
        self.around = {-1: set()}
        around = set([start_pos])
        way = []
        num = 0
        while around:
            self.around[num] = around
            around = self.find_around(around, end_pos, num)
            num += 1
            if end_pos in around:
                pos = end_pos
                for i in range(num)[::-1]:
                    old_z, old_x, old_y = pos
                    new_z, new_x, new_y = (self.get_beside_except(pos, MazeBase.Type.Static.wall) & self.around[i]).pop()
                    pos = new_z, new_x, new_y
                    move = (new_x - old_x, new_y - old_y)
                    if move in move_map:
                        way.insert(0, move_map[move])
                break
            if around == []:
                if self.get_type(end_pos) == MazeBase.Type.Static.stair:
                    print(pos, end_pos)

        return way


if __name__ == '__main__':
    maze = Maze()
    maze.update()

    stairs_start = set(maze.maze_info[1]['stair'][MazeBase.Value.Stair.down]).pop()
    stairs_end = set(maze.maze_info[1]['stair'][MazeBase.Value.Stair.up]).pop()
    print(stairs_start, stairs_end)
    #print maze.tree_map[1]['info']['area']

    print(maze.find_path(stairs_start, stairs_end))

