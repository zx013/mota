#-*- coding:utf-8 -*-
import random
import pickle



class staticproperty(property):
	def __get__(self, cls, owner):
		return staticmethod(self.fget).__get__(owner)()



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
		class Special:
			boss = 1
			trigger = 2
			item = 3
			shop = 4
			branch = 5

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

			prison = 5
			trap = 6

	class NodeType:
		none = 0
		area_normal = 1
		area_corner = 2
		Area = (area_normal, area_corner)
		road_normal = 3
		road_corner = 4
		Road = (road_normal, road_corner)

#为了使用pickle模块，MazeNode, TreeNode两个类需在最顶级定义
class MazeNode:
	Type = 0
	Value = 0


class TreeNode:
	def __init__(self, area, crack, special=False):
		self.Area = area
		self.Crack = crack
		self.Cover = self.Area | self.Crack

		self.Forward = {}
		self.Backward = {}

		self.Special = special
		self.Space = len(area)

		self.Item.Door = 0
		self.Item.Key = {MazeBase.Value.Color.yellow: 0, MazeBase.Value.Color.blue: 0, MazeBase.Value.Color.red: 0, MazeBase.Value.Color.green: 0}

	class Item:
		pass

	@property
	def floor(self):
		return list(self.Area)[0][0]

	@property
	def forbid(self):
		return filter(lambda x: Pos.inside(x) and (not (Pos.beside(x) & self.Crack)), reduce(lambda x, y: x ^ y, map(lambda x: Pos.corner(x) - self.Cover, self.Crack)))

class MazeSetting:
	#层数
	floor = 7
	#行
	rows = 11
	#列
	cols = 11
	#保存的目录
	save_dir = 'save'
	#保存的文件
	save_file = 'save'
	
	@staticproperty
	def save_format():
		return '{save_dir}/{{0}}.{save_file}'.format(save_dir=MazeSetting.save_dir, save_file=MazeSetting.save_file)
	#保存的层数，10时占用20M左右内存，100时占用50M左右内存
	save_floor = 100
	#每几层一个单元
	base_floor = 3


class Pos:
	@staticmethod
	def inside(pos):
		z, x, y = pos
		if 0 < x < MazeSetting.rows + 1:
			if 0 < y < MazeSetting.cols + 1:
				return True
		return False

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
		for key in self.maze.keys():
			if key < floor - MazeSetting.save_floor:
				del self.maze[key]
				del self.maze_map[key]
				del self.maze_info[key]
		self.maze[floor] = [[MazeNode() for j in xrange(MazeSetting.cols + 2)] for i in xrange(MazeSetting.rows + 2)]
		self.maze_map[floor] = {MazeBase.Type.Static.ground: set()}
		self.maze_info[floor] = {}
		for i in xrange(MazeSetting.rows + 2):
			for j in xrange(MazeSetting.cols + 2):
				if i in (0, MazeSetting.rows + 1) or j in (0, MazeSetting.cols + 1):
					self.maze[floor][i][j].Type = MazeBase.Type.Static.wall
				else:
					self.maze[floor][i][j].Type = MazeBase.Type.Static.ground
					self.maze_map[floor][MazeBase.Type.Static.ground].add((floor, i, j))


	def get_type(self, pos):
		z, x, y = pos
		return self.maze[z][x][y].Type

	def get_value(self, pos):
		z, x, y = pos
		return self.maze[z][x][y].Value

	def set_type(self, pos, value):
		z, x, y = pos
		if x < 1 or x > MazeSetting.rows:
			return
		if y < 1 or y > MazeSetting.cols:
			return
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

	def get_corner(self, pos, type):
		return {(z, x, y) for z, x, y in Pos.corner(pos) if self.maze[z][x][y].Type == type}

	def get_around(self, pos, type):
		return {(z, x, y) for z, x, y in Pos.around(pos) if self.maze[z][x][y].Type == type}


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
		if not self.maze_map[floor].has_key(type):
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
		for i in xrange(row):
			for j in xrange(col):
				if self.get_type((floor, x + i, y + j)) != rect1[i][j]:
					return False
		if rect2:
			for i in xrange(row):
				for j in xrange(col):
					if rect2[i][j]:
						type, value = rect2[i][j]
						if type:
							self.set_type((floor, x + i, y + j), type)
						if value:
							self.set_value((floor, x + i, y + j), value)
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

	def is_start_floor(self, floor):
		if floor:
			return False
		return True

	def is_boss_floor(self, floor):
		if not floor % MazeSetting.base_floor:
			return True
		return False



	def get_rect(self, pos, width, height):
		z, x, y = pos
		rect = set()
		for i in xrange(x, x + width):
			for j in xrange(y, y + height):
				rect.add((z, i, j))
		return rect

	def get_rect_crack(self, pos, width, height):
		z, x, y = pos
		return self.get_rect((z, x - 1, y - 1), width + 2, height + 2) - self.get_rect(pos, width, height)

	#特殊区域，一块较大的矩形
	def create_special(self, floor):
		self.maze_info[floor]['special'] = set()
		if self.is_start_floor(floor):
			pass
		elif self.is_boss_floor(floor): #boss层只有一个特殊区域
			pos_list = [(floor, 1, 1)]
			width = 7
			height = 7
			for pos in pos_list:
				area = self.get_rect(pos, width, height)
				crack = self.get_rect_crack(pos, width, height)
				for pos in crack:
					self.set_type(pos, MazeBase.Type.Static.wall)
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
					break
				else:
					pure -= set(wall)
		self.merge_rect(floor)
		self.node_info(floor)


	def crack_wall(self, floor):
		#special区域只开一个口
		crack_list = self.get_crack(floor) #可打通的墙

		next_node = list(self.maze_info[floor]['node'])
		crack_set = set() #已设置墙和未设置墙区域之间可打通的墙
		special_set = set()

		while next_node:
			if not crack_set:
				node = random.choice(filter(lambda x: not x.Special, next_node))
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


	def overlay_pos(self, node_list):
		pos_list = []
		for node in node_list: #选取当前楼层的一个区域
			if node.Special:
				continue
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
		if self.is_start_floor(floor - 1) or self.is_boss_floor(floor - 1):
			down_overlay = self.overlay_pos(down_node)
			down, down_pos = down_overlay.pop()
		else:
			up_node = list(self.maze_info[floor - 1]['node'])
			random.shuffle(up_node)
			#生成下行楼梯和上一层上行楼梯
			#两个区域重叠的点，尽可能避开特殊区域，如果没有合适的点，则楼梯不在同一位置
			class StairException(Exception): pass
			try:
				down_overlay = self.overlay_pos(down_node)
				up_overlay = self.overlay_pos(up_node)
				if not down_overlay:
					down_overlay = map(lambda x: (x, random.choice(list(x.Area))), down_node)
				if not up_overlay:
					up_overlay = map(lambda x: (x, random.choice(list(x.Area))), up_node)
				for down, down_pos in down_overlay:
					for up, up_pos in up_overlay:
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
	def ergodic(self, floor, across=1):
		node_list = [set(self.maze_info[floor]['tree']).pop()]
		while node_list:
			node = random.choice(node_list)
			node_list += list(set(node.Forward.values()) - set(node_list))
			if floor + across > node.floor + 1:
				if node.Area & self.maze_info[node.floor]['stair'][MazeBase.Value.Stair.up]:
					node_list.append(set(self.maze_info[node.floor + 1]['tree']).pop())
			node_list.remove(node)
			yield node


	def adjust_corner(self, floor):
		corner = set()
		for door in self.find_pos(floor, MazeBase.Type.Static.door):
			for beside in self.get_beside(door, MazeBase.Type.Static.ground):
				if self.pos_type(beside) == MazeBase.NodeType.road_corner:
					corner.add(beside)
		#print len(corner), len(self.find_pos(floor, MazeBase.Type.Static.door))

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
				#print crack

	def adjust(self, floor):
		self.adjust_corner(floor)
		self.adjust_trap(floor)
		self.adjust_crack(floor)



	def set_stair(self, floor):
		for up in self.maze_info[floor]['stair'][MazeBase.Value.Stair.up]:
			self.set_type(up, MazeBase.Type.Static.stair)
			self.set_value(up, MazeBase.Value.Stair.up)
		for down in self.maze_info[floor]['stair'][MazeBase.Value.Stair.down]:
			self.set_type(down, MazeBase.Type.Static.stair)
			self.set_value(down, MazeBase.Value.Stair.down)

	def set_door(self, hero, node_list):
		for node in node_list:
			pass #print node.Area

	def set_start_area(self, floor):
		pass

	def set_boss_area(self, floor):
		pass

	def set_item(self, floor):
		hero = Hero.copy()
		if self.is_start_floor(floor):
			pass
		elif self.is_boss_floor(floor):
			for f in xrange(floor - MazeSetting.base_floor + 1, floor + 1):
				self.set_stair(f)
			node_list = self.ergodic(floor - MazeSetting.base_floor + 1, MazeSetting.base_floor)
			self.set_door(hero, node_list)

			self.set_start_area(floor)
			self.set_boss_area(floor)
			#for f in xrange(floor - MazeSetting.base_floor + 1, floor + 1):
			#	self.show(f)


	def fast_save(self, floor):
		pass

	def fast_load(self, floor):
		pass

	def save(self, num):
		maze = pickle.dumps(self.maze)
		maze_map = pickle.dumps(self.maze_map)
		maze_info = pickle.dumps(self.maze_info)
		maze_record = {'maze': maze, 'maze_map': maze_map, 'maze_info': maze_info}
		record = pickle.dumps(maze_record)

		with open(MazeSetting.save_format.format(num), 'w+') as fp:
			fp.write(record)


	def load(self, num):
		with open(MazeSetting.save_format.format(num), 'r+') as fp:
			record = fp.read()

		maze_record = pickle.loads(record)
		self.maze = pickle.loads(maze_record['maze'])
		self.maze_map = pickle.loads(maze_record['maze_map'])
		self.maze_info = pickle.loads(maze_record['maze_info'])


	def create(self):
		for floor in xrange(MazeSetting.floor):
			self.init(floor)
			if self.is_start_floor(floor):
				continue
			self.create_special(floor)
			self.create_wall(floor)
			self.crack_wall(floor)
			self.create_stair(floor)
			self.create_tree(floor)
			self.adjust(floor)

			self.set_item(floor)

		#self.show(0)
		#self.save(0)
		#self.load(0)
		#self.show()

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
