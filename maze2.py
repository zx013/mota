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


class MazeTree:
	class Node:
		def __init__(self, area, crack):
			self.Area = area
			self.Crack = crack

			self.Forward = {}
			self.Backward = {}

			self.Space = len(area)

			self.Item = type('Item', (), {})
			self.Item.Door = 0
			self.Item.Key = {MazeBase.Value.Color.yellow: 0, MazeBase.Value.Color.blue: 0, MazeBase.Value.Color.red: 0, MazeBase.Value.Color.green: 0}

		@property
		def floor(self):
			return list(self.Area)[0][0]

class MazeSetting:
	#层数
	floor = 3
	#行
	rows = 11
	#列
	cols = 11


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



class HeroBase:
	def __init__(self, hero=None):
		if hero:
			self.health = hero.health
			self.attack = hero.attack
			self.defence = hero.defence

			self.key = dict(hero.key)
		else:
			self.health = 1000
			self.attack = 10
			self.defence = 10

			self.key = {MazeBase.Value.Color.yellow: 1, MazeBase.Value.Color.blue: 0, MazeBase.Value.Color.red: 0, MazeBase.Value.Color.green: 0}

	def copy(self):
		return HeroBase(self)

Hero = HeroBase()



class Maze2:
	def __init__(self):
		self.maze = {}
		self.maze_map = {} #每一层不同点的分类集合
		self.maze_info = {} #每一层的信息，node, stair等
		self.create()

	def init(self, floor):
		self.maze[floor] = [[MazeBase.Node() for j in xrange(MazeSetting.cols + 2)] for i in xrange(MazeSetting.rows + 2)]
		self.maze_map[floor] = {MazeBase.Type.Static.ground: set()}
		self.maze_info[floor] = {}
		for i in xrange(MazeSetting.rows + 2):
			for j in xrange(MazeSetting.cols + 2):
				if i in (0, MazeSetting.rows + 1) or j in (0, MazeSetting.cols + 1):
					self.maze[floor][i][j].Type = MazeBase.Type.Static.wall
				else:
					self.maze[floor][i][j].Type = MazeBase.Type.Static.ground
					self.maze_map[floor][MazeBase.Type.Static.ground].add((floor, i, j))


	def inside(self, pos):
		z, x, y = pos
		if 0 < x < MazeSetting.rows + 1:
			if 0 < y < MazeSetting.cols + 1:
				return True
		return False

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
	def find_pos(self, floor, type, func=None):
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

	#查找矩形，设置rect2的话则用rect2替换找到的矩形
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
			pos = ground.pop()
			area = self.get_area(pos)
			crack = reduce(lambda x, y: x | y, [self.get_beside(pos, MazeBase.Type.Static.wall) for pos in area]) & crack_list
			node = MazeTree.Node(area=area, crack=crack)
			self.maze_info[floor]['node'].add(node)
			ground -= area

	def find_node(self, pos):
		z, x, y = pos
		for node in self.maze_info[z]['node']:
			if pos in node.Area:
				return node

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


	def create_wall(self, floor):
		while True:
			pure = self.get_pure(floor)
			if not pure:
				break
			pos = random.choice(tuple(pure))
			self.add_wall(pos)
		self.merge(floor)
		self.node_info(floor)


	def crack_wall(self, floor):
		crack_list = self.get_crack(floor) #可打通的墙

		next_node = list(self.maze_info[floor]['node'])
		crack_set = set() #已设置墙和未设置墙区域之间可打通的墙

		while next_node:
			if not crack_set:
				node = random.choice(next_node)
			else:
				crack_pos = random.choice(list(crack_set))
				#该区域和上一个区域之间的墙
				self.set_type(crack_pos, MazeBase.Type.Static.door)
				#self.set_value(crack_pos, MazeBase.Value.Color.yellow)

				for node in next_node:
					if crack_pos in node.Crack:
						break

			crack_set = (crack_set | node.Crack) - (crack_set & node.Crack)
			next_node.remove(node)


	def overlay_pos(self, node_list):
		pos_list = []
		for node in node_list: #选取当前楼层的一个区域
			for pos in node.Area:
				type = self.pos_type(pos)
				if type == MazeBase.NodeType.road_normal:
					continue
				if self.get_beside(pos, MazeBase.Type.Static.door):
					continue
				pos_list.append([node, pos])
		return pos_list

	def create_stair(self, floor):
		self.maze_info[floor]['stair'] = {MazeBase.Value.Stair.up: set(), MazeBase.Value.Stair.down: set()}
		down_node = list(self.maze_info[floor]['node'])
		random.shuffle(down_node)
		if floor == 0:
			#生成下行楼梯
			down, down_pos = self.overlay_pos(down_node).pop()
		else:
			self.maze_info[floor - 1]['stair'][MazeBase.Value.Stair.up] = set()
			up_node = list(self.maze_info[floor - 1]['node'])
			random.shuffle(up_node)
			#生成下行楼梯和上一层上行楼梯
			class StairException(Exception): pass
			try: #两个区域重叠的点
				for down, down_pos in self.overlay_pos(down_node):
					for up, up_pos in self.overlay_pos(up_node):
						if self.maze_info[floor - 1]['stair'][MazeBase.Value.Stair.down] & up.Area:
							continue
						if down_pos[1] == up_pos[1] and down_pos[2] == up_pos[2]:
							raise StairException
				#没有上下楼同一位置的楼梯，上下楼楼梯设置为不同位置
				#maze较小时可能触发
				raise StairException
			except StairException:
				up_node.remove(up)
				self.maze_info[floor - 1]['stair'][MazeBase.Value.Stair.up].add(up_pos)

		down_node.remove(down)
		self.maze_info[floor]['stair'][MazeBase.Value.Stair.down].add(down_pos)



	def create_tree(self, floor):
		self.maze_info[floor]['tree'] = set()
		for down in self.maze_info[floor]['stair'][MazeBase.Value.Stair.down]: #只有一个
			node = self.find_node(down)
			self.maze_info[floor]['tree'].add(node) #每一层起点

			node_list = [node]
			door_list = self.find_pos(floor, MazeBase.Type.Static.door)
			while node_list:
				node = node_list.pop()
				for door in door_list & node.Crack:
					beside_pos = (self.get_beside(door, MazeBase.Type.Static.ground) - node.Area).pop()
					beside_node = self.find_node(beside_pos)
					node.Forward[door] = beside_node
					beside_node.Backward[door] = node
					node_list.append(beside_node)
				door_list -= node.Crack


	#遍历树
	def ergodic(self, floor):
		node_list = [set(self.maze_info[floor]['tree']).pop()]
		while node_list:
			node = random.choice(node_list)
			node_list += list(set(node.Forward.values()) - set(node_list))
			if floor >= 0:
				if node.Area & self.maze_info[node.floor]['stair'][MazeBase.Value.Stair.up]:
					node_list.append(set(self.maze_info[node.floor + 1]['tree']).pop())
			node_list.remove(node)
			yield node


	def set_stair(self, floor):
		for up in self.maze_info[floor]['stair'][MazeBase.Value.Stair.up]:
			self.set_type(up, MazeBase.Type.Static.stair)
			self.set_value(up, MazeBase.Value.Stair.up)
		for down in self.maze_info[floor]['stair'][MazeBase.Value.Stair.down]:
			self.set_type(down, MazeBase.Type.Static.stair)
			self.set_value(down, MazeBase.Value.Stair.down)

	def set_door(self, hero, node_list):
		for node in node_list:
			pass

	def set_item(self):
		hero = Hero.copy()
		for floor in xrange(MazeSetting.floor):
			self.set_stair(floor)
		node_list = self.ergodic(0)
		self.set_door(hero, node_list)

	def create(self):
		for floor in xrange(MazeSetting.floor):
			self.init(floor)
			self.create_wall(floor)
			self.crack_wall(floor)
			self.create_stair(floor)
			self.create_tree(floor)

		#放置物品
		self.set_item()

	def show(self, floor=None):
		for k in xrange(MazeSetting.floor):
			if floor is not None: k = floor
			print 'floor :', k
			for i in xrange(MazeSetting.rows + 2):
				for j in xrange(MazeSetting.cols + 2):
					if self.get_type((k, i, j)) == MazeBase.Type.Static.ground:
						print ' ',
					elif self.get_type((k, i, j)) == MazeBase.Type.Static.wall:
						print 'x',
					elif self.get_type((k, i, j)) == MazeBase.Type.Static.door:
						print 'o',
					else:
						print self.get_value((k, i, j)),
				print
			print
			print
			if floor is not None: break
		import sys
		sys.stdout.flush()

if __name__ == '__main__':
	maze = Maze2()
	maze.show()
