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
	floor = 1
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

	def get_around(self, pos, type):
		around = set()
		z, x, y = pos
		if x > 0:
			around.add((z, x - 1, y))
		if x < MazeSetting.rows + 1:
			around.add((z, x + 1, y))
		if y > 0:
			around.add((z, x, y - 1))
		if y < MazeSetting.cols + 1:
			around.add((z, x, y + 1))
		return {(z, x, y) for z, x, y in around if self.maze[z][x][y].Type == type}

	def is_pure(self, pos, num):
		around_wall = self.get_around(pos, MazeBase.Type.Static.wall)
		if len(around_wall) != 1:
			return False
		z, x, y = pos
		z_wall, x_wall, y_wall = around_wall.pop()
		x_min = max(x, 0) if x > x_wall else max(x - num, 0)
		x_max = min(x, MazeSetting.rows + 1) if x < x_wall else min(x + num, MazeSetting.rows + 1)
		y_min = max(y, 0) if y > y_wall else max(y - num, 0)
		y_max = min(y, MazeSetting.cols + 1) if y < y_wall else min(y + num, MazeSetting.cols + 1)

		for i in xrange(x_min, x_max + 1):
			for j in xrange(y_min, y_max + 1):
				if self.maze[z][i][j].Type == MazeBase.Type.Static.wall:
					return False
		return True

	#检查邻边的点周围几格内没有其它的边
	def pure_num(self, pos):
		for num in xrange(1, max(MazeSetting.rows, MazeSetting.cols)):
			if not self.is_pure(pos, num):
				return num - 1

	def get_pure(self, floor, num):
		pure = set()
		for i in xrange(MazeSetting.rows + 2):
			for j in xrange(MazeSetting.cols + 2):
				if self.pure_num((floor, i, j)) >= num:
					pure.add((floor, i, j))
		return pure

	#给出一个被墙三面包围的点，获取该点延伸区域的所有点
	def get_end_area(self, pos):
		area = set()
		if len(self.get_around(pos, MazeBase.Type.Static.wall)) != 3:
			return area
		while True:
			around = self.get_around(pos, MazeBase.Type.Static.ground)
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
		while self.pure_num(pos) >= num:
			self[pos].Type = MazeBase.Type.Static.wall
			z, x, y = pos
			z_wall, x_wall, y_wall = self.get_around(pos, MazeBase.Type.Static.wall).pop()
			pos = (z, 2 * x - x_wall, 2 * y - y_wall)
			length += 1
		if length == 0:
			return
		#如果长度为1的墙生成了大小为1的区域
		if length == 1:
			pos_set = set()
			for pos in self.get_around((z, x, y), MazeBase.Type.Static.ground):
				if len(self.get_end_area(pos)) == 1:
					pos_set.add(pos)
			if pos_set:
				return (z, x, y)

	def create(self):
		#from show import logging
		for floor in xrange(MazeSetting.floor):
			clear_wall = set()
			while True:
				pure = self.get_pure(floor, 1)
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
				if maze[(0, i, j)].Type == MazeBase.Type.Static.ground:
					print ' ',
				elif maze[(0, i, j)].Type == MazeBase.Type.Static.wall:
					print 1,
			print

if __name__ == '__main__':
	maze = Maze2()
	maze.show()