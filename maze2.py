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

	def increase_wall(self, pos, num):
		while self.pure_num(pos) >= num:
			self[pos].Type = MazeBase.Type.Static.wall
			z, x, y = pos
			z_wall, x_wall, y_wall = self.get_around(pos, MazeBase.Type.Static.wall).pop()
			pos = (z, 2 * x - x_wall, 2 * y - y_wall)

	def create(self):
		from show import logging
		while True:
			num = 1
			pure = self.get_pure(0, num)
			if not pure:
				return
			pos = random.choice(tuple(pure))
			self.increase_wall(pos, num)

if __name__ == '__main__':
	maze = Maze2()
	maze.increase_wall((0, 3, 1), 2)
	#for i in xrange(MazeSetting.rows + 2):
	#	for j in xrange(MazeSetting.cols + 2):
	#		print maze.pure_num((0, i, j)),
	#	print