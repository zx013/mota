#-*- coding:utf-8 -*-
import sys
version = sys.version_info.major
if version == 2:
    from Queue import Queue
elif version == 3:
    from queue import Queue

from maze2 import MazeBase, MazeSetting


class Event:
    def __init__(self, maze):
        self.maze = maze
        self.move_queue = Queue()

    def add(self, direct):
        self.move_queue.put(direct)

    def clean(self):
        try:
            while True:
                self.move_queue.get_nowait()
        except Exception as ex:
            print(ex)

    def move(self):
        while True:
            try:
                direct = self.move_queue.get()
                pos = self.maze.move_pos(state.pos, direct)
                pos_type = self.maze.get_type(pos)
                pos_value = self.maze.get_value(pos)

                is_move = False
                if pos_type == MazeBase.ground:
                    is_move = True
                elif pos_type == MazeBase.wall:
                    is_move = False
                elif pos_type == MazeBase.Item.key:
                    self.get_key(pos_value)
                    is_move = True
                elif pos_type == MazeBase.Item.gem_attack:
                    self.get_attack_gem(pos_type, pos_value)
                    is_move = True
                elif pos_type == MazeBase.Item.gem_defence:
                    self.get_attack_gem(pos_type, pos_value)
                    is_move = True
                elif pos_type == MazeBase.Item.potion:
                    self.get_potion(pos_value)
                    is_move = True
                elif pos_type == MazeBase.door:
                    is_move = self.open_door(pos_value)
                elif pos_type == MazeBase.monster:
                    is_move = self.attack_monster(pos_value)
                elif pos_type == MazeBase.stairs:
                    pass
                elif pos_type == MazeBase.other:
                    is_move = False
                else:
                    is_move = False

                if is_move:
                    self.maze.set_type(pos, 0)
                    self.maze.set_value(pos, 0)
                    self.move_hero(pos)
                elif pos_type == MazeBase.monster:
                    self.die()

            except Exception as ex:
                print(ex)


    def die(self):
        self.clean()

    def move_hero(self, pos):
        #hero move
        state.pos = pos


    def get_key(self, color):
        #item clear
        state.key[color] += 1

    def get_attack_gem(self, attack):
        #item clear
        state.hero.attack += attack * level.attack

    def get_attack_gem(self, defence):
        #item clear
        state.hero.defence += defence * level.defence

    def get_potion(self, pos_value):
        #item clear
        state.hero.health += pos_value * level.health


    def open_door(self, color):
        if state.key[color] == 0:
            return False

        state.key[color] -= 1
        return True

    def attack_monster(self, monster):
        #show damage
        #item clear or die
        damage = state.hero.fight(monster)
        if damage < 0:
            return False
        state.hero.health -= damage
        return True

    def climb_stair(self):
        pass

class MoveBase:
    up = (1, 0)
    down = (-1, 0)
    left = (0, 1)
    right = (0, -1)


class Move:
    def __init__(self, maze):
        self.maze = maze

    def get_around(self, pos_list, num):
        around = set()
        for pos in pos_list:
            around |= self.maze.get_beside_except(pos, MazeBase.Type.Static.wall)
        around -= pos_list | self.around[num - 1]
        return around

    def get_way(self, pos, num):
        way = []
        for i in range(num - 1, -1, -1):
            old_z, old_x, old_y = pos
            new_z, new_x, new_y = (self.maze.get_beside_except(pos, MazeBase.Type.Static.wall) & self.around[i]).pop()
            pos = new_z, new_x, new_y
            way.append((new_x - old_x, new_y - old_y))
        return way[::-1]

    def move_pos(self, start_pos, end_pos):
        if self.maze.get_type(end_pos) == MazeBase.Type.Static.wall:
            return
        self.around = {-1: set()}
        around = set([start_pos])
        num = 0
        self.around[num] = around
        while around:
            around = self.get_around(around, num)
            print(around)
            num += 1
            self.around[num] = around
            if end_pos in around:
                return self.get_way(end_pos, num)

class Control:
    pass


if __name__ == '__main__':
    from maze2 import Maze2, hero
    maze = Maze2(hero)
    maze.update()
    #maze.show(lambda pos: maze.get_type(pos))

    stairs_start = set(maze.maze_info[1]['stair'][MazeBase.Value.Stair.down]).pop()
    stairs_end = set(maze.maze_info[1]['stair'][MazeBase.Value.Stair.up]).pop()
    print(stairs_start, stairs_end)
    #print maze.tree_map[1]['info']['area']

    move = Move(maze)
    print(move.move_pos(stairs_start, stairs_end))