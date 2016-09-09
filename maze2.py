#-*- coding:utf-8 -*-
import random

class MazeBase:
	class Type:
		class Static:
			ground = 11
			wall = 12
			shop = 13
			stairs = 14
			door = 15

		class Active:
			monster = 21
			rpc = 22

		class Item:
			key = 31
			potion = 32

			attack = 33
			defence = 34

		unknown = 99

	class Value:
		class Shop:
			gold = 1
			experience = 2

		class Stairs:
			start = 1
			end = 2

		#key和door的颜色
		class Color:
			yellow = 1
			blue = 2
			red = 3
			green = 4

	class Node:
		Type = 0
		Value = 0


class MazeSetting:
	#层数
	floor = 100
	#行
	rows = 13
	#列
	cols = 13


class Maze2:
	maze = []
	def __init__(self):
		for k in xrange(MazeSetting.floor):
			floor_area = []
			for i in xrange(MazeSetting.rows + 2):
				rows_area = []
				for j in xrange(MazeSetting.cols + 2):
					node = MazeBase.Node()
					if i in (0, MazeSetting.rows + 1) or j in (0, MazeSetting.cols + 1):
						node.Type = MazeBase.Type.Static.wall
					else:
						node.Type = MazeBase.Type.Static.ground
					rows_area.append(node)
				floor_area.append(rows_area)
			self.maze.append(floor_area)
		self.create()

	#maze[(0, 1, 1)].Type
	def __getitem__(self, key):
		z, x, y = key
		return self.maze[z][x][y]

	def __iter__(self):
		return ((k, i, j) for k in xrange(MazeSetting.floor) for i in xrange(MazeSetting.rows + 2) for j in xrange(MazeSetting.cols + 2))

	def get_beside(self, pos, type):
		z, x, y = pos
		beside = ((z, x - 1, y), (z, x + 1, y), (z, x, y - 1), (z, x, y + 1))
		return {(z, x, y) for z, x, y in beside if self.maze[z][x][y].Type == type}

	def get_around(self, pos, type):
		z, x, y = pos
		around = ((z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1), (z, x, y - 1), (z, x, y + 1), (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1))
		return {(z, x, y) for z, x, y in around if self.maze[z][x][y].Type == type}

	#在floor层的type类型的区域中寻找符合func要求的点
	def find_pos(self, floor, type, func):
		return {(floor, i, j) for i in xrange(1, MazeSetting.rows + 1) for j in xrange(1, MazeSetting.cols + 1) if self[(floor, i, j)].Type == type and func((floor, i, j))}

	def is_pure(self, pos):
		if len(self.get_beside(pos, MazeBase.Type.Static.wall)) != 1:
			return False
		z, x, y = zip(*self.get_around(pos, MazeBase.Type.Static.wall))
		if len(set(x)) != 1 and len(set(y)) != 1:
			return False
		return True

	def get_pure(self, floor):
		return self.find_pos(floor, MazeBase.Type.Static.ground, self.is_pure)

	#给出一个被墙三面包围的点，获取该点延伸区域的所有点
	def get_endarea(self, pos):
		area = set()
		if len(self.get_beside(pos, MazeBase.Type.Static.wall)) != 3:
			return area
		while True:
			around = self.get_beside(pos, MazeBase.Type.Static.ground)
			if len(around) > 2:
				break
			area.add(pos)
			for around_pos in around:
				if around_pos not in area:
					pos = around_pos
					break
		return area

	def add_wall(self, pos, num):
		length = 0
		while self.is_pure(pos):
			self[pos].Type = MazeBase.Type.Static.wall
			z, x, y = pos
			z_wall, x_wall, y_wall = self.get_beside(pos, MazeBase.Type.Static.wall).pop()
			pos = (z, 2 * x - x_wall, 2 * y - y_wall)
			length += 1
		if length == 0:
			return
		#如果长度为1的墙生成了大小为1的区域
		if length == 1:
			pos_set = set()
			for pos in self.get_beside((z, x, y), MazeBase.Type.Static.ground):
				if len(self.get_endarea(pos)) == 1:
					pos_set.add(pos)
			if pos_set:
				return (z, x, y)

	def create(self):
		#from show import logging
		for floor in xrange(MazeSetting.floor):
			clear_wall = set()
			while True:
				pure = self.get_pure(floor)
				if not pure:
					break
				pos = random.choice(tuple(pure))
				clear_wall.add(self.add_wall(pos, 1))
			for pos in clear_wall:
				if pos:
					self[pos].Type = MazeBase.Type.Static.ground

	def show(self):
		for i in xrange(MazeSetting.rows + 2):
			for j in xrange(MazeSetting.cols + 2):
				if self[(0, i, j)].Type == MazeBase.Type.Static.ground:
					print ' ',
				elif self[(0, i, j)].Type == MazeBase.Type.Static.wall:
					print 1,
			print
		print

if __name__ == '__main__':
	maze = Maze2()
	maze.show()