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

	class NodeType:
		none = 0
		area_normal = 1
		area_corner = 2
		Area = (area_normal, area_corner)
		road_normal = 3
		road_corner = 4
		Road = (road_normal, road_corner)


class MazeSetting:
	#层数
	floor = 100
	#行
	rows = 13
	#列
	cols = 13


class Pos:
	@staticmethod
	def add(pos1, pos2):
		z1, x1, y1 = pos1
		z2, x2, y2 = pos2
		return (z1, x1 + x2, y1 + y2)

	@staticmethod
	def sub(pos1, pos2):
		z1, x1, y1 = pos1
		z2, x2, y2 = pos2
		return (z1, x1 - x2, y1 - y2)

	@staticmethod
	def mul(pos, num):
		z, x, y = pos
		return (z, num * x, num * y)

	@staticmethod
	def beside(pos):
		z, x, y = pos
		return ((z, x - 1, y), (z, x + 1, y), (z, x, y - 1), (z, x, y + 1))

	@staticmethod
	def around(pos):
		z, x, y = pos
		return ((z, x - 1, y - 1), (z, x - 1, y), (z, x - 1, y + 1), (z, x, y - 1), (z, x, y + 1), (z, x + 1, y - 1), (z, x + 1, y), (z, x + 1, y + 1))



class Maze2:
	def __init__(self):
		self.maze = [[[MazeBase.Node() for j in xrange(MazeSetting.cols + 2)] for i in xrange(MazeSetting.rows + 2)] for k in xrange(MazeSetting.floor)]

		self.maze_map = {}
		for k in xrange(MazeSetting.floor):
			self.maze_map[k] = {MazeBase.Type.Static.ground: set()}
			for i in xrange(MazeSetting.rows + 2):
				for j in xrange(MazeSetting.cols + 2):
					if i in (0, MazeSetting.rows + 1) or j in (0, MazeSetting.cols + 1):
						self.maze[k][i][j].Type = MazeBase.Type.Static.wall
					else:
						self.maze[k][i][j].Type = MazeBase.Type.Static.ground
						self.maze_map[k][MazeBase.Type.Static.ground].add((k, i, j))
		self.create()

	def get_type(self, pos):
		z, x, y = pos
		return self.maze[z][x][y].Type

	def get_value(self, pos):
		z, x, y = pos
		return self.maze[z][x][y].Value

	def set_type(self, pos, value):
		z, x, y = pos
		type = self.maze[z][x][y].Type
		self.maze_map[z].setdefault(type, set())
		self.maze_map[z].setdefault(value, set())
		self.maze_map[z][type].remove(pos)
		self.maze_map[z][value].add(pos)
		self.maze[z][x][y].Type = value

	def set_value(self, pos, value):
		z, x, y = pos
		self.maze[z][x][y].Value = value

	def get_beside(self, pos, type):
		return {(z, x, y) for z, x, y in Pos.beside(pos) if self.maze[z][x][y].Type == type}

	def get_around(self, pos, type):
		return {(z, x, y) for z, x, y in Pos.around(pos) if self.maze[z][x][y].Type == type}

	#在floor层的type类型的区域中寻找符合func要求的点
	def find_pos(self, floor, type, func):
		return {pos for pos in self.maze_map[floor][type] if func(pos)}

	#获取pos的类型area, road, end
	def pos_type(self, pos):
		beside_ground = self.get_beside(pos, MazeBase.Type.Static.ground)
		if len(beside_ground) >= 3:
			return MazeBase.NodeType.area_normal
		if len(beside_ground) == 1:
			return MazeBase.NodeType.road_corner
		if len(beside_ground) == 2:
			(z1, x1, y1), (z2, x2, y2) = beside_ground
			if x1 == x2 or y1 == y2:
				return MazeBase.NodeType.road_normal
			if self.get_type((z2, x2, y1) if pos == (z1, x1, y2) else (z1, x1, y2)) == MazeBase.Type.Static.wall:
				return MazeBase.NodeType.road_normal
			return MazeBase.NodeType.area_corner
		return MazeBase.NodeType.none

	def get_area(self, pos):
		area = set()
		beside = set([pos])
		type = MazeBase.NodeType.Area if self.pos_type(pos) in MazeBase.NodeType.Area else MazeBase.NodeType.Road

		while beside:
			pos = beside.pop()
			area.add(pos)
			beside = beside | {beside_pos for beside_pos in self.get_beside(pos, MazeBase.Type.Static.ground) if self.pos_type(beside_pos) in type} - area
		return area

	def is_pure(self, pos):
		if len(self.get_beside(pos, MazeBase.Type.Static.wall)) != 1:
			return False
		z, x, y = zip(*self.get_around(pos, MazeBase.Type.Static.wall))
		if len(set(x)) != 1 and len(set(y)) != 1:
			return False
		return True

	def get_pure(self, floor):
		#如果需要提高速度，每次放置墙时改变该值
		return self.find_pos(floor, MazeBase.Type.Static.ground, self.is_pure)

	def add_wall(self, pos):
		move = Pos.sub(pos, self.get_beside(pos, MazeBase.Type.Static.wall).pop())
		while self.get_type(pos) == MazeBase.Type.Static.ground:
			self.set_type(pos, MazeBase.Type.Static.wall)
			pos = Pos.add(pos, move)

	def clear_wall(self, floor):
		func = lambda pos: self.pos_type(pos) == MazeBase.NodeType.road_corner and len(self.get_area(pos)) == 1
		for pos in self.find_pos(floor, MazeBase.Type.Static.ground, func):
			pass


	def replace_rect(self, floor, rect1, rect2, x, y, row, col):
		if x + row > MazeSetting.rows + 2 or y + col > MazeSetting.cols + 2:
			return False
		for i in xrange(row):
			for j in xrange(col):
				if self.get_type((floor, x + i, y + j)) != rect1[i][j]:
					return False
		for i in xrange(row):
			for j in xrange(col):
				if rect2[i][j]:
					self.set_type((floor, x + i, y + j), rect2[i][j])
		return True

	def find_rect(self, floor, rect1, rect2):
		_rect1 = zip(*rect1)
		_rect2 = zip(*rect2)
		row = len(rect1)
		col = len(_rect1)
		for x in xrange(0, MazeSetting.rows + 2):
			for y in xrange(0, MazeSetting.cols + 2):
				self.replace_rect(floor, rect1, rect2, x, y, row, col)
				self.replace_rect(floor, _rect1, _rect2, x, y, col, row)

	def merge(self, floor):
		rect1 = [[MazeBase.Type.Static.wall, MazeBase.Type.Static.wall, MazeBase.Type.Static.wall, MazeBase.Type.Static.wall],
				[MazeBase.Type.Static.wall, MazeBase.Type.Static.ground, MazeBase.Type.Static.ground, MazeBase.Type.Static.wall],
				[MazeBase.Type.Static.wall, MazeBase.Type.Static.wall, MazeBase.Type.Static.wall, MazeBase.Type.Static.wall],
				[MazeBase.Type.Static.wall, MazeBase.Type.Static.ground, MazeBase.Type.Static.ground, MazeBase.Type.Static.wall],
				[MazeBase.Type.Static.wall, MazeBase.Type.Static.wall, MazeBase.Type.Static.wall, MazeBase.Type.Static.wall]]
		rect2 = [[0, 0, 0, 0],
			[0, 0, 0, 0],
			[0, MazeBase.Type.Static.ground, MazeBase.Type.Static.ground, 0],
			[0, 0, 0, 0],
			[0, 0, 0, 0]]
		self.find_rect(floor, rect1, rect2)

	def create(self):
		for floor in xrange(MazeSetting.floor):
			while True:
				pure = self.get_pure(floor)
				if not pure:
					break
				pos = random.choice(tuple(pure))
				self.add_wall(pos)
			#self.clear_wall(floor)
			self.merge(floor)

	def show(self):
		for i in xrange(MazeSetting.rows + 2):
			for j in xrange(MazeSetting.cols + 2):
				if self.get_type((0, i, j)) == MazeBase.Type.Static.ground:
					print ' ',
				elif self.get_type((0, i, j)) == MazeBase.Type.Static.wall:
					print 1,
			print
		print

if __name__ == '__main__':
	maze = Maze2()
	maze.show()
