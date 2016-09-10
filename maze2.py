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
	floor = 1
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

	def get_beside(self, pos, type):
		return {(z, x, y) for z, x, y in Pos.beside(pos) if self.maze[z][x][y].Type == type}

	def get_around(self, pos, type):
		return {(z, x, y) for z, x, y in Pos.around(pos) if self.maze[z][x][y].Type == type}

	#在floor层的type类型的区域中寻找符合func要求的点
	def find_pos(self, floor, type, func):
		return {(floor, i, j) for i in xrange(1, MazeSetting.rows + 1) for j in xrange(1, MazeSetting.cols + 1) if self[(floor, i, j)].Type == type and func((floor, i, j))}

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
			if self[(z2, x2, y1) if pos == (z1, x1, y2) else (z1, x1, y2)].Type == MazeBase.Type.Static.wall:
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

	#点pos向各个方向移动，最大移动步数
	def get_forward(self, pos):
		forward = []
		for beside in self.get_beside(pos, MazeBase.Type.Static.ground):
			move = Pos.sub(beside, pos)
			num = 0
			while self[beside].Type == MazeBase.Type.Static.ground:
				beside = Pos.add(beside, move)
				num += 1
			forward.append(num)
		return forward

	def is_pure(self, pos):
		if len(self.get_beside(pos, MazeBase.Type.Static.wall)) != 1:
			return False
		z, x, y = zip(*self.get_around(pos, MazeBase.Type.Static.wall))
		if len(set(x)) != 1 and len(set(y)) != 1:
			return False
		#if min(*self.get_forward(pos)) % 2 == 0:
		#	return False
		#z, x, y = map(lambda x: max(x) - min(x) + 1, zip(*self.get_area(pos)))
		#if x <= 3 or y <= 3:
		#	return False
		
		return True

	def get_pure(self, floor):
		return self.find_pos(floor, MazeBase.Type.Static.ground, self.is_pure)

	def add_wall(self, pos):
		while self.is_pure(pos):
			self[pos].Type = MazeBase.Type.Static.wall
			pos = Pos.sub(Pos.mul(pos, 2), self.get_beside(pos, MazeBase.Type.Static.wall).pop())

	def clear_wall(self, floor):
		func = lambda pos: self.pos_type(pos) == MazeBase.NodeType.road_corner and len(self.get_area(pos)) == 1
		for pos in self.find_pos(floor, MazeBase.Type.Static.ground, func):
			pass

	def create(self):
		#from show import logging
		for floor in xrange(MazeSetting.floor):
			while True:
				pure = self.get_pure(floor)
				if not pure:
					break
				pos = random.choice(tuple(pure))
				self.add_wall(pos)
			self.clear_wall(floor)

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
