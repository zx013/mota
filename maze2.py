#-*- coding:utf-8 -*-
import random

class MazeBase:
	class Type:
		class Static:
			ground = 11
			wall = 12
			shop = 13
			stair = 14
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

		class Stair:
			up = 1
			down = 2

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
	floor = 3
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
		self.maze_info = {}
		for k in xrange(MazeSetting.floor):
			self.maze_map[k] = {MazeBase.Type.Static.ground: set()}
			self.maze_info[k] = {}
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



	def is_rect(self, pos, rect1, rect2, row, col):
		floor, x, y = pos
		if x + row > MazeSetting.rows + 2 or y + col > MazeSetting.cols + 2:
			return False
		for i in xrange(row):
			for j in xrange(col):
				if self.get_type((floor, x + i, y + j)) != rect1[i][j]:
					return False
		if rect2:
			for i in xrange(row):
				for j in xrange(col):
					if rect2[i][j]:
						self.set_type((floor, x + i, y + j), rect2[i][j])
		return True

	def find_rect(self, floor, rect1, rect2=None):
		_rect1 = zip(*rect1)
		_rect2 = zip(*rect2) if rect2 else None
		row = len(rect1)
		col = len(_rect1)
		pos_list = [(floor, i, j) for i in xrange(0, MazeSetting.rows + 2) for j in xrange(0, MazeSetting.cols + 2)]
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

	def get_area(self, pos):
		area = set()
		beside = set([pos])
		type = MazeBase.NodeType.Area if self.pos_type(pos) in MazeBase.NodeType.Area else MazeBase.NodeType.Road

		while beside:
			pos = beside.pop()
			area.add(pos)
			beside = beside | {beside_pos for beside_pos in self.get_beside(pos, MazeBase.Type.Static.ground) if self.pos_type(beside_pos) in type} - area
		return area

	def area_info(self, floor):
		info = self.maze_info[floor]
		info['area'] = {MazeBase.NodeType.Area: [], MazeBase.NodeType.Road: []}
		ground = set(self.maze_map[floor][MazeBase.Type.Static.ground])
		while ground:
			pos = ground.pop()
			type = MazeBase.NodeType.Area if self.pos_type(pos) in MazeBase.NodeType.Area else MazeBase.NodeType.Road
			area = self.get_area(pos)
			info['area'][type].append(area)
			ground -= area


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


	def merge(self, floor):
		wall = MazeBase.Type.Static.wall
		ground = MazeBase.Type.Static.ground
		rect1 = [[wall, wall, wall, wall],
				[wall, ground, ground, wall],
				[wall, wall, wall, wall],
				[wall, ground, ground, wall],
				[wall, wall, wall, wall]]
		rect2 = [[0, 0, 0, 0],
				[0, 0, 0, 0],
				[0, ground, ground, 0],
				[0, 0, 0, 0],
				[0, 0, 0, 0]]
		self.find_rect(floor, rect1, rect2)
		#self.get_crack(floor)
		#print map(len, self.area_map[floor].values())


	def create_wall(self):
		for floor in xrange(MazeSetting.floor):
			while True:
				pure = self.get_pure(floor)
				if not pure:
					break
				pos = random.choice(tuple(pure))
				self.add_wall(pos)
			self.merge(floor)
			self.area_info(floor)


	def create_stair(self):
		for floor in xrange(MazeSetting.floor):
			info = self.maze_info[floor]
			info['stair'] = {MazeBase.Value.Stair.up: set(), MazeBase.Value.Stair.down: set()}
			next_area = reduce(lambda x, y: x + y, info['area'].values())
			random.shuffle(next_area)
			if floor == 0:
				#生成下行楼梯
				area = next_area.pop()
				for pos in area:
					if self.pos_type(pos) != MazeBase.NodeType.road_normal:
						self.set_type(pos, MazeBase.Type.Static.stair)
						self.set_value(pos, MazeBase.Value.Stair.down)
						info['stair'][MazeBase.Value.Stair.down].add(pos)
						break
			else:
				#生成下行楼梯和上一层上行楼梯
				class StairException(Exception): pass
				try:
					for next in next_area: #选取当前楼层的一个区域
						for prev in prev_area: #选取上一层的一个区域
							#两个区域重叠的点
							for z1, x1, y1 in next:
								if self.pos_type((z1, x1, y1)) == MazeBase.NodeType.road_normal:
									continue
								for z2, x2, y2 in prev:
									if self.pos_type((z2, x2, y2)) == MazeBase.NodeType.road_normal:
										continue
									if x1 == x2 and y1 == y2:
										raise StairException
					#没有上下楼同一位置的楼梯，上下楼楼梯设置为不同位置
					#maze较小时可能触发
					raise StairException
				except StairException:
					next_area.remove(next)
					prev_area.remove(prev)
					self.set_type((z1, x1, y1), MazeBase.Type.Static.stair)
					self.set_value((z1, x1, y1), MazeBase.Value.Stair.up)
					info['stair'][MazeBase.Value.Stair.up].add((z1, x1, y1))
					self.set_type((z2, x2, y2), MazeBase.Type.Static.stair)
					self.set_value((z2, x2, y2), MazeBase.Value.Stair.down)
					info['stair'][MazeBase.Value.Stair.down].add((z2, x2, y2))
				
			prev_area = next_area
		else:
			#生成上行楼梯
			area = next_area.pop()
			for pos in area:
				if self.pos_type(pos) != MazeBase.NodeType.road_normal:
					self.set_type(pos, MazeBase.Type.Static.stair)
					self.set_value(pos, MazeBase.Value.Stair.up)
					info['stair'][MazeBase.Value.Stair.up].add(pos)
					break

	def create(self):
		self.create_wall()
		self.create_stair()

	def show(self):
		for k in xrange(MazeSetting.floor):
			for i in xrange(MazeSetting.rows + 2):
				for j in xrange(MazeSetting.cols + 2):
					if self.get_type((k, i, j)) == MazeBase.Type.Static.ground:
						print ' ',
					elif self.get_type((k, i, j)) == MazeBase.Type.Static.wall:
						print 1,
					else:
						print 2,
				print
			print
			print

if __name__ == '__main__':
	maze = Maze2()
	maze.show()
