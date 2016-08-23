#-*- coding:utf-8 -*-
from maze import MazeBase, MazeSetting
from maze import state, level
'''
class MazeBase:
	ground = 0
	wall = 1
	item = 2
	door = 3
	monster = 4
	stairs = 5
	other = 100
'''

import Queue

class Event:
	def __init__(self, maze):
		self.maze = maze
		self.move_queue = Queue.Queue()

	def add(self, direct):
		self.move_queue.put(direct)

	def clean(self):
		try:
			while True:
				self.move_queue.get_nowait()
		except Exception, ex:
			print ex

	def move(self):
		while True:
			try:
				direct = self.move_queue.get() #取出移动点
				pos = self.maze.move_pos(state.pos, direct) #移动后位置
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
					pass
				elif pos_type == MazeBase.stairs:
					pass
				elif pos_type == MazeBase.other:
					pass
				else:
					pass

				if is_move:
					self.maze.set_type(pos, 0)
					self.maze.set_value(pos, 0)
					self.move_hero(pos)

			except Exception, ex:
				print ex

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

	def attack_monster(self):
		pass


class MoveBase:
	up = (-1, 0)
	down = (1, 0)
	left = (0, -1)
	right = (0, 1)


class Move:
	def __init__(self, maze):
		self.maze = maze

	def get_around_list(self, pos_list, num):
		around_list = set()
		for pos in pos_list:
			around_list |= {p for p in self.maze.get_around(pos, 1) if self.maze.get_type(p) != MazeBase.wall}
		around_list -= pos_list | self.way[num - 1]
		return around_list

	def get_way(self, pos, num):
		way = []
		for i in xrange(num - 1, 0, -1):
			old_z, old_x, old_y = pos
			new_z, new_x, new_y = (self.maze.get_around(pos, 1) + list(self.way[i]))[0]
			pos = new_z, new_x, new_y
			way.append((new_x - old_x, new_y - old_y))
		return way[::-1]

	def move_pos(self, start_pos, end_pos):
		if self.maze.get_type(end_pos) == MazeBase.wall:
			return
		self.way = {0: set()}
		around = set([start_pos])
		num = 1
		self.way[num] = around
		while around:
			around = self.get_around_list(around, num)
			num += 1
			self.way[num] = around
			if end_pos in around:
				return self.get_way(end_pos, num)

class Control:
	pass


if __name__ == '__main__':
	from maze import Maze
	maze = Maze()
	#maze.show(lambda pos: maze.get_type(pos))

	stairs_start = maze.info[0]['stairs_start']
	stairs_end = maze.info[0]['stairs_end']
	print stairs_start, stairs_end
	#print maze.tree_map[1]['info']['area']

	move = Move(maze)
	print move.move_pos(stairs_start, stairs_end)