#-*- coding:utf-8 -*-
import random
import copy

def put(*args):
	print args
	import sys
	sys.stdout.flush()

maze_show = '''
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1     1 1     1 1   1   1 1
1 1 1 1 1 1 1 1 1 1   1   1 1
1   1     1 1 1 1 1 1 1 1 1 1
1   1 1 1 1   1 1   1 1 1 1 1
1 1 1 1 1 1   1 1   1 1     1
1 1     1 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1   1   1
1 1 1 1     1 1     1   1   1
1   1 1 1 1 1 1 1 1 1 1 1 1 1
1   1 1 1 1     1     1     1
1 1 1 1   1 1 1 1 1 1 1 1 1 1
1   1 1   1   1   1   1   1 1
1   1 1 1 1   1   1   1   1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
'''


class MazeBase:
	ground = 0
	wall = 1
	item = 2
	door = 3
	monster = 4
	stairs = 5
	other = 100

	point = 7
	area = 8
	ground_replace = 9

	ground_list = [ground, ground_replace]


	stairs_start = 1
	stairs_end = 2

	maze_node = {'type': 0, 'value': 0}
	tree_node = {'number': 0, 'empty': False, 'info': {'type': 0, 'area': set()}, 'count': {'key': {'yellow': 0, 'blue': 0, 'red': 0, 'green': 0}, 'door': '', 'potion': 0, 'gem': {'attack': 0, 'defence': 0}, 'damage': 0, 'monster': set()}, 'way': {'forward': {}, 'backward': {}}}
	#'count': {'all': 0, 'ground': 0, 'wall': 0, 'item': 0, 'door': 0, 'monster': 0, 'stairs': 0, 'other': 0}


class MazeSetting:
	#层数
	floor = 1
	#行
	rows = 13
	#列
	cols = 13
	#楼梯对齐，禁用可大幅提高地图生成速度
	stairs_align = True


class Hero:
	def __init__(self):
		self.health = 1000
		self.attack = 10
		self.defence = 10

	def fight(self, hero):
		if self.attack <= hero.defence:
			return -1
		if hero.attack <= self.defence:
			return 0;
		hit = round(1.0 * hero.health / (self.attack - hero.defence))
		damage = (hit - 1) * (hero.attack - self.defence)
		self.health -= damage
		return damage;

class Maze:
	maze = []
	def __init__(self):
		for k in range(MazeSetting.floor):
			floor_area = []
			for i in range(MazeSetting.rows + 2):
				rows_area = []
				for j in range(MazeSetting.cols + 2):
					rows_area.append(dict(MazeBase.maze_node))
				floor_area.append(rows_area)
			self.maze.append(floor_area)

	def move_pos(self, pos, move):
		z, x, y = pos
		move_x, move_y = move
		return (z, x + move_x, y + move_y)

	def inside(self, pos):
		z, x, y = pos
		if 0 <= x <= MazeSetting.rows + 1:
			if 0 <= y <= MazeSetting.cols + 1:
				return True
		return False

	def get_type(self, pos):
		z, x, y = pos
		if self.inside(pos):
			value = self.maze[z][x][y]['type']
		else:
			value = MazeBase.ground
		return value

	def get_value(self, pos):
		z, x, y = pos
		value = self.maze[z][x][y]['value']
		return value

	def set_type(self, pos, value):
		z, x, y = pos
		self.maze[z][x][y]['type'] = value

	def set_value(self, pos, value):
		z, x, y = pos
		self.maze[z][x][y]['value'] = value

	def get_around(self, pos, num):
		around = []
		z, x, y = pos
		if x > num - 1:
			around.append((z, x - num, y))
		if x < MazeSetting.rows + 2 - num:
			around.append((z, x + num, y))
		if y > num - 1:
			around.append((z, x, y - num))
		if y < MazeSetting.cols + 2 - num:
			around.append((z, x, y + num))
		return around

	def get_around_floor(self, pos):
		floor = pos[0]
		around = self.get_around(pos, 1)
		#楼梯结束的周围包括了下一层的楼梯
		if self.info[floor]['stairs_end'] == pos and self.info.has_key(floor + 1):
			around.append(self.info[floor + 1]['stairs_start'])
		return around

	def get_around_wall(self, pos):
		around = {around_pos for around_pos in self.get_around(pos, 1) if self.get_type(around_pos) == MazeBase.wall}
		return around

	def get_count(self, pos):
		count = {}
		for count_pos in self.get_around(pos, 1):
			pos_type = self.get_type(count_pos)
			count.setdefault(pos_type, 0)
			count[pos_type] += 1
		return count

	#将type1改变为type2
	def change(self, floor, type1, type2):
		for i in range(1, MazeSetting.rows + 1):
			for j in range(1, MazeSetting.cols + 1):
				pos = (floor, i, j)
				if self.get_type(pos) == type1:
					self.set_type(pos, type2)


	info = {}
	def init_floor(self, floor):
		self.info[floor] = {}

	def init_stairs(self, floor):
		#获取上一层的终止点，没有则随机生成
		pos_list = self.get_pos_list(floor, (1, MazeSetting.rows + 1), (1, MazeSetting.cols + 1))
		pos_list = [pos for pos in pos_list if self.get_type(pos) == MazeBase.ground and len(self.get_around_wall(pos)) == 3]
		if len(pos_list) <= 2: #不足以摆放楼梯
			return False

		if floor <= 0 or not MazeSetting.stairs_align:
			start_pos = random.choice(pos_list)
			self.info[floor]['stairs_start'] = start_pos
		else:
			pos = self.info[floor - 1]['stairs_end']
			start_pos = (pos[0] + 1, pos[1], pos[2])
			self.info[floor]['stairs_start'] = start_pos
			if start_pos not in pos_list:
				return False
		floor, start_x, start_y = start_pos

		for floor, end_x, end_y in pos_list:
			end_pos = (floor, end_x, end_y)
			if abs(end_x - start_x) > 1 or abs(end_y - start_y) > 1:
				break
		else:
			return False
		self.info[floor]['stairs_end'] = end_pos
		return True

	def create_stairs(self, floor):
		start_pos = self.info[floor]['stairs_start']
		self.set_type(start_pos, MazeBase.stairs)
		self.set_value(start_pos, MazeBase.stairs_start)

		end_pos = self.info[floor]['stairs_end']
		self.set_type(end_pos, MazeBase.stairs)
		self.set_value(end_pos, MazeBase.stairs_end)


	def get_pos_list(self, floor, (start_x, end_x), (start_y, end_y)):
		pos_list = []
		for x in range(start_x, end_x):
			for y in range(start_y, end_y):
				pos_list.append((floor, x, y))
		pos_list = random.sample(pos_list, len(pos_list))
		return pos_list

	#填充m*n的方格
	#处理多层的墙
	#建立通道

	def block_init(self, floor):
		for i in range(MazeSetting.rows + 2):
			for j in range(MazeSetting.cols + 2):
				if 0 < i < MazeSetting.rows + 1 and 0 < j < MazeSetting.cols + 1:
					fill_type = MazeBase.ground
				else:
					fill_type = MazeBase.wall
				self.set_type((floor, i, j), fill_type)

	def block_insert(self, floor, width, height):
		pos_list = self.get_pos_list(floor, (1, MazeSetting.rows + 2 - height), (1, MazeSetting.cols + 2 - width))
		for z, x, y in pos_list:
			for i in range(x, x + height):
				for j in range(y, y + width):
					if self.get_type((floor, i, j)) != 0:
						break
				else:
					continue
				break
			else:
				for i in range(x - 1, x + height + 1):
					for j in range(y - 1, y + width + 1):
						if x <= i < x + height and y <= j < y + width:
							fill_type = MazeBase.ground_replace
						else:
							fill_type = MazeBase.wall
						self.set_type((floor, i, j), fill_type)
				return True
		return False

	def block_fill(self, floor):
		choice_type = [1, 2]
		while choice_type:
			r = random.choice(choice_type)
			if not self.block_insert(floor, r, 3 - r):
				choice_type.remove(r)
		self.change(floor, MazeBase.ground_replace, MazeBase.ground)


	def is_special(self, special):
		type1, type2, type3, type4 = map(self.get_type, special)
		if type1 == MazeBase.ground  and type2 == MazeBase.wall and type3 == MazeBase.wall and type4 ==  MazeBase.ground:
			return True
		#if type1 in MazeBase.ground_list and type2 in [MazeBase.wall, MazeBase.ground_replace] and type3 in [MazeBase.wall, MazeBase.ground_replace] and type4 in MazeBase.ground_list:
		#	return True
		return False

	def get_special(self, pos):
		z, x, y = pos
		special_list = (((z, x + 2, y), (z, x + 1, y), (z, x, y), (z, x - 1, y)),
			((z, x + 1, y), (z, x, y), (z, x - 1, y), (z, x - 2, y)),
			((z, x, y + 2), (z, x, y + 1), (z, x, y), (z, x, y - 1)),
			((z, x, y + 1), (z, x, y), (z, x, y - 1), (z, x, y - 2)))
		return special_list

	def check_special(self, pos):
		for special in self.get_special(pos):
			if self.is_special(special):
				return special
		return ()

	#往move_type方向获取可能的special
	def move_special(self, special, move_type):
		special_list = []
		move_value = 1
		while True:
			move = [move_type[0] * move_value, move_type[1] * move_value]
			temp_special = []
			for pos in special:
				temp_special.append(self.move_pos(pos, move))
			if self.is_special(temp_special):
				special_list.append(temp_special)
			else:
				break
			move_value += 1
		return special_list

	def get_move_special(self, special):
		special_list = [special]
		if special[0][1] == special[1][1] == special[2][1] == special[3][1]: #x相等
			special_list += self.move_special(special, (1, 0))
			special_list += self.move_special(special, (-1, 0))
		elif special[0][2] == special[1][2] == special[2][2] == special[3][2]:
			special_list += self.move_special(special, (0, 1))
			special_list += self.move_special(special, (0, -1))
		return special_list

	def set_special(self, special):
		special_list = self.get_move_special(special)
		pos0, pos1, pos2, pos3 = special

		if not self.inside(pos0):
			choose = 2
		elif not self.inside(pos3):
			choose = 1
		else:
			around1 = len(self.get_around_wall(pos1))
			around2 = len(self.get_around_wall(pos2))
			#周围的墙数目，选择较少的一边，可以消除大部分的隔断情况
			if around1 > around2:
				choose = 2
			elif around1 < around2:
				choose = 1
			else:
				choose = random.choice((1, 2))
		for temp_special in special_list:
			pos = temp_special[choose]
			self.set_type(pos, MazeBase.ground)

	#| 0 0 | 0 | 0 1 1 0 | 0 1 1 0
	#| 1 1 | 1 | 0 1 1 0 |
	#| 1 1 | 1 |
	#| 0 0 | 0 |
	def block_check(self, floor):
		check = True
		pos_list = self.get_pos_list(floor, (1, MazeSetting.rows + 1), (1, MazeSetting.cols + 1))
		for pos in pos_list:
			if self.get_type(pos) != MazeBase.wall:
				continue
			special = self.check_special(pos)
			if not special:
				continue
			self.set_special(special)
			check = False
		return check


	#填充一块区域
	#获取区域边界
	#边界上选取一个和其他区域连通的点（条形区域尽量选择在两端）

	def get_edge(self, pos):
		edge = set()
		pos_type = self.get_type(pos)
		if pos_type == MazeBase.wall:
			edge.add(pos)
		if pos_type in [MazeBase.wall, MazeBase.ground_replace]:
			return edge
		self.set_type(pos, MazeBase.ground_replace)
		for around in self.get_around(pos, 1):
			edge |= self.get_edge(around)
		return edge

	def get_edge_pos(self, edge):
		edge = random.sample(edge, len(edge))
		for pos in edge:
			for around in self.get_around(pos, 1):
				if self.get_type(around) == MazeBase.ground:
					return pos
		return ()

	def block_connect(self, floor):
		pos_list = self.get_pos_list(floor, (1, MazeSetting.rows + 1), (1, MazeSetting.cols + 1))
		for pos in pos_list:
			if self.get_type(pos) == MazeBase.wall:
				continue
			break
		while pos:
			self.set_type(pos, MazeBase.ground)
			edge = self.get_edge(pos)
			pos = self.get_edge_pos(edge)
			self.change(floor, MazeBase.ground_replace, MazeBase.ground)


	#对特殊方块进行调整
	#3*2的方块可以去除中间的一块
	#2*2的方块

	def is_solid(self, solid):
		for pos in solid:
			if self.get_type(pos) != MazeBase.wall:
				return False
		return True

	def get_solid(self, pos):
		z, x, y = pos
		solid_list = (((z, x, y), (z, x + 1, y), (z, x + 2, y), (z, x, y + 1), (z, x + 1, y + 1), (z, x + 2, y + 1)),
			((z, x, y), (z, x, y + 1), (z, x, y + 2), (z, x + 1, y), (z, x + 1, y + 1), (z, x + 1, y + 2)))
		return solid_list

	def check_solid(self, pos):
		for solid in self.get_solid(pos):
			if self.is_solid(solid):
				return solid
		return ()

	def set_solid(self, solid):
		#中间两个点
		pos_list = [solid[1], solid[4]]
		#pos_list = random.sample(pos_list, len(pos_list))
		pos_list = [pos for pos in pos_list if self.get_count(pos).get(MazeBase.ground, 0) >= 1]
		if len(pos_list) > 0:
			pos = random.choice(pos_list)
			self.set_type(pos, MazeBase.ground)
			return True
		return False


	#正方形四个角的判定
	#去除后会将墙隔断的区域
	#隔断判断：去除的墙为A，A在正方块内相邻的为B, C，A在正方形外相邻的为D，若B, D呈斜对角，且去除A后B, D的另一边没有墙时，称去除A后隔断B, D
	#去除后会增加一个分支
	#	延长路径
	#去除后会将地面区域扩大
	#	2*2->2*3
	#	路径->2*2
	#全部不符合的，尝试移动墙壁
	#即将墙去除后产生隔断，在隔断的另一边添加一面墙，如果不影响连通性，则进行该处理（递归时可能产生死循环）
	def is_square(self, square):
		for pos in square:
			if self.get_type(pos) != MazeBase.wall:
				return False
		return True

	def get_square(self, pos):
		z, x, y = pos
		square = ((z, x, y), (z, x + 1, y), (z, x, y + 1), (z, x + 1, y + 1))
		return square

	def check_square(self, pos):
		square = self.get_square(pos)
		if self.is_square(square):
			return square
		return ()


	def get_separate(self, square):
		separate_list = []
		for pos in square:
			#相邻的墙，集合形式
			around = self.get_around_wall(pos)
			if len(around) == 4: #四面都是墙
				continue
			beside_in = around & set(square) #正方形内相邻的点
			beside_out = around - beside_in #正方形外相邻的点
			if len(beside_out) == 0: #没有外相邻的点，则不会隔断
				continue
			#如果有外相邻点且不隔断，则为2*3的方块
			separate_list.append(pos)
		return separate_list

	#获取扩张前的形状
	def get_expand(self, pos):
		#向四个方向延伸，计算延伸的值
		expand = []
		for around in self.get_around(pos, 1):
			if self.get_type(around) == MazeBase.wall:
				continue
			move_type = (around[1] - pos[1], around[2] - pos[2])
			move_value = 1
			while True:
				move = [move_type[0] * move_value, move_type[1] * move_value]
				if self.get_type(self.move_pos(pos, move)) == MazeBase.wall:
					break
				move_value += 1
			expand.append(move_value - 1)
		print expand


	def check_separate(self, square):
		 separate_list = self.get_separate(square)
		 if len(separate_list) != 4:
		 	expand_list = list(set(square) - set(separate_list))
		 	#for pos in expand_list:
		 	#	self.get_expand(pos)
		 	pos = random.choice(expand_list)
		 	self.set_type(pos, MazeBase.ground)
		 else:
		 	pass
		 	#print set(separate_list)

	def set_square(self, square):
		self.check_separate(square)
		return False

	def adjust_solid(self, floor):
		check = False
		pos_list = self.get_pos_list(floor, (0, MazeSetting.rows), (0, MazeSetting.cols))
		for pos in pos_list:
			if self.get_type(pos) != MazeBase.wall:
				continue
			solid = self.check_solid(pos)
			if not solid:
				continue
			if self.set_solid(solid):
				check = True
		return check

	def adjust_square(self, floor):
		check = False
		pos_list = self.get_pos_list(floor, (1, MazeSetting.rows), (1, MazeSetting.cols))
		for pos in pos_list:
			if self.get_type(pos) != MazeBase.wall:
				continue
			square = self.check_square(pos)
			if not square:
				continue
			#print square
			if self.set_square(square):
				check = True
		return check

	def block_adjust(self, floor):
		while self.adjust_solid(floor):
			pass
		while self.adjust_square(floor):
			pass


	#方块是否规则
	#是否有对角的墙
	def is_block(self, floor):
		if not self.init_stairs(floor):
			return False
		return True

	def block_create(self): #小地图时有可能卡住
		for floor in range(MazeSetting.floor):
			self.init_floor(floor)
			while True:
				self.block_init(floor)
				self.block_fill(floor)
				while not self.block_check(floor):
					pass
				self.block_connect(floor)
				self.block_adjust(floor)
				if self.is_block(floor):
					break
			self.create_stairs(floor)


	#生成树状结构
	#用2*2的方块移动，该方块能活动的最大范围为一个块状区域
	#周围有小于等于2个ground的ground区域，同类型的方块连通的道路，为路径区域，路径的一端有被墙三面包围的ground，则为尽头
	#无法形成块状区域的点，周围有3个或以上的ground区域，为点分支区域
	#一个区域连接着1个区域的，为尽头区域
	#一个区域连接着2个区域的，为路径区域
	#一个区域连接着3个或以上区域的，为分支区域

	tree = {}
	tree_number = 0
	tree_map = {}
	#人物状态
	fight_state = {}

	def tree_init(self):
		self.tree = copy.deepcopy(MazeBase.tree_node)
		self.tree_number = 0
		self.tree_map = {self.tree_number: self.tree}
		self.fight_state['hero'] = Hero()
		self.fight_state['move_node'] = set([self.tree_number])
		self.fight_state['key'] = {'yellow': 1, 'blue': 0, 'red': 0, 'green': 0}

	def tree_insert_point(self, floor):
		pos_list = self.get_pos_list(floor, (1, MazeSetting.rows + 1), (1, MazeSetting.cols + 1))
		for pos in pos_list:
			if self.get_type(pos) in [MazeBase.wall, MazeBase.area]:
				continue
			if len(self.get_around_wall(pos)) <= 1:
				self.set_type(pos, MazeBase.point)

	def check_area(self, pos):
		square = self.get_square(pos)
		for pos in square:
			if self.get_type(pos) == MazeBase.wall:
				return ()
		return square

	def tree_insert_area(self, floor):
		pos_list = self.get_pos_list(floor, (1, MazeSetting.rows), (1, MazeSetting.cols))
		for pos in pos_list:
			if self.get_type(pos) == MazeBase.wall:
				continue
			square = self.check_area(pos)
			for square_pos in square:
				self.set_type(square_pos, MazeBase.area)

	#以pos为起始，漫延一个区域或道路
	#道路的话，漫延至转折点
	#区域的话，漫延整个区域
	#往不同的分支依次递归
	def spread_pos(self, node, pos):
		node['info']['area'].add(pos)
		if self.get_type(pos) not in [MazeBase.door]:
			self.set_type(pos, MazeBase.ground_replace)

	#点加入区域，递归周围的点
	#点为路径点，加入周围的点
	#点为区域点，加入周围的区域点，不加入周围的路径点或分支点，周围点中的路径点或分支点，加入forward
	#点为分支点，将周围的分支点加入forward，不加入周围的点
	def spread_node(self, pre, node, pos):
		pos_type = self.get_type(pos)
		self.spread_pos(node, pos)
		for around_pos in self.get_around_floor(pos):
			#墙，已经遍历的点
			around_type = self.get_type(around_pos)
			if around_type in [MazeBase.wall, MazeBase.ground_replace]:
				continue
			if pre:
				if pos_type in [MazeBase.point]: #分支点
					node['way']['forward'][around_pos] = {}
					continue
				elif pos_type in [MazeBase.area]: #区域点
					if around_type not in [MazeBase.area]:
						node['way']['forward'][around_pos] = {}
						continue
				else:
					if around_type in [MazeBase.area]:
						node['way']['forward'][around_pos] = {}
						continue
			else:
				if around_type in [MazeBase.door]:
					if map(self.get_type, self.get_around(around_pos, 1)).count(MazeBase.ground): #门两侧没有被填充
						node['way']['forward'][around_pos] = {}
						continue

			self.spread_node(pre, node, around_pos)

	def add_node(self, pre, pos, backward):
		self.tree_number += 1
		node = copy.deepcopy(MazeBase.tree_node)
		node['number'] = self.tree_number
		self.tree_map[self.tree_number] = node
		backward['way']['forward'][pos] = node
		node['way']['backward'][pos] = backward
		node['info']['type'] = self.get_type(pos)
		if node['info']['type'] == MazeBase.stairs: #楼梯归为地面
			node['info']['type'] = MazeBase.ground
		self.spread_node(pre, node, pos)
		#print node['info'], node['way']['forward'].keys()
		#self.show(lambda pos: self.get_type(pos))
		for pos, forward in node['way']['forward'].items():
			self.add_node(pre, pos, node)



	#调整树，减少分支数量
	#单节点尽头
	def tree_adjust(self, floor):
		pass



	#区域单独成块
	#道路和转折点拼接
	def tree_create(self, pre=True):
		self.tree_init()
		if pre:
			for floor in range(MazeSetting.floor):
				self.tree_insert_point(floor)
				self.tree_insert_area(floor)
		self.add_node(pre, self.info[0]['stairs_start'], self.tree)
		#print self.fight_state['move_node']
		#self.tree_travel()

		for floor in range(MazeSetting.floor):
			self.change(floor, MazeBase.ground_replace, MazeBase.ground)


	#没算进楼梯
	def is_slit(self, pos):
		if self.get_type(pos) == MazeBase.wall:
			return False
		around_type = map(self.get_type, self.get_around(pos, 1))
		if around_type not in [[MazeBase.ground, MazeBase.ground, MazeBase.wall, MazeBase.wall], [MazeBase.wall, MazeBase.wall, MazeBase.ground, MazeBase.ground]]:
			return False
		return True

	#点附近的门数量
	def around_door(self, pos):
		z, x, y = pos
		around = [(z, x + 2, y), (z, x + 1, y + 1), (z, x, y + 2), (z, x - 1, y + 1), (z, x - 2, y), (z, x - 1, y - 1), (z, x, y - 2), (z, x + 1, y - 1)]
		return map(self.get_type, around).count(MazeBase.door)

	door_num = 0
	def set_door(self, pos):
		if self.is_slit(pos) and self.around_door(pos) < 2:
			self.set_type(pos, MazeBase.door)
			self.door_num += 1


	area_num = 0
	def set_node(self, node):
		backward = node['way']['backward']
		if len(backward) == 0:
			return
		backward_pos, backward_node = backward.items()[0]
		if node['info']['type'] != MazeBase.area: #路径
			forward = node['way']['forward']
			#尽头路径或上一个node为区域的
			#if len(forward) == 0 or backward_node['info']['type'] == MazeBase.area:
			area = len(node['info']['area'])
			route = len(node['way']['forward']) + len(node['way']['backward'])
			if area <= 2 and route == 1 or area <= 3 and route > 1:
				return
			self.set_door(backward_pos)
		else: #区域
			forward_pos = list(set(self.get_around(backward_pos, 1)) & backward_node['info']['area'])[0]
			self.set_door(forward_pos)
			self.area_num += 1


	#将两个node合并成一个节点
	def merge_node(self, node1, node2):
		node1['empty'] = node1['empty'] and node1['empty']
		#node1['info']['type']
		node1['info']['area'] |= node2['info']['area']
		node1['way']['forward'].update(node2['way']['forward'])
		del node1['way']['forward'][node2['way']['backward'].keys()[0]]

		del self.tree_map[node2['number']]
		del node2

	merge_list = []
	#两个相邻区域没有门，则合并
	def node_door(self, node):

		for forward_pos, forward_node in node['way']['forward'].items():
			if len(node['way']['backward']) == 0:
				continue
			backward_pos, backward_node = node['way']['backward'].items()[0]
			forward_pos_list = list(set(self.get_around(backward_pos, 1)) & backward_node['info']['area'])
			if len(forward_pos_list) == 0:
				continue
			forward_pos = forward_pos_list[0]
			door_num = map(self.get_type, (forward_pos, backward_pos)).count(MazeBase.door)
			if door_num != 0:
				continue
			self.merge_list.append((node['number'], forward_node['number']))
		#	self.merge_node(node, forward_node)
		#	merge_node = True
		#if merge_node:
		#	self.node_door(node)


	def choice_dict(self, d):
		total = sum(d.values())
		rand = random.randint(1, total)
		for key, val in d.items():
			rand -= val
			if rand <= 0:
				return key


	#寻找一条随机路径
	def set_item(self):
		#当前的钥匙
		key_list = copy.deepcopy(self.fight_state['key'])
		#钥匙选择的概率
		key_choice = {'yellow': 65, 'blue': 20, 'red': 10, 'green': 5}

		move_list = [forward_node['number'] for forward_node in self.tree['way']['forward'].values()]
		while move_list:
			#move = random.choice(move_list)
			move = move_list.pop(random.choice(range(len(move_list))))
			node = self.tree_map[move]
			#移除移动的node，添加node的forward
			move_list += [forward_node['number'] for forward_node in node['way']['forward'].values()]

			#从拥有的钥匙中选择一把作为门的颜色
			#随机添加一把钥匙
			door = self.choice_dict(key_list)
			key_list[door] -= 1
			key = self.choice_dict(key_choice)
			key_list[key] += 1

			node['count']['door'] = door
			node['count']['key'][key] += 1
			#print node['count']



	#一个区域，只有物品，合并到上一个区域
	#一个区域，没有物品，合并到下一个区域，没有下一个区域，则忽略该区域
	#1 0 1，缝隙
	#门只能放置在缝隙中，且处于区域周围或尽头路径的起始
	#尽头路径area越大，门的概率越高

	#门后放置怪物
	#区域只放置一个
	#路径依次放置多个，area越大，可能放置的就越多

	#空余部分放置物品

	#路径上尽可能少的放置，一层的一钥匙和门数大约为面积的开方，怪物数稍微多一些


	#计算门链
	#计算怪物链，最后放置生命药水
	#将链嵌入地图结构
	#计算最优解和可能解
	#调整分布（增加怪物或减少物品），直到可能解数量在一个范围内

	#门链计算
	#按比例分布门，分布愈均匀选择可能性愈少
	#随机选取一条路径
	#每个门后都放置一把钥匙，保证该路径畅通
	#将较后区域的部分钥匙移动到较前区域，增加选择性，以3*13*13的区域小于1000万的搜索数为准
	#角色身上的钥匙数越多，选择的数量大幅增加，所以钥匙数量必须严格控制


	#区域或道路通过方式
	#损耗，获得，（扫荡）


	def in_node_fight(self, node):
		door = node['count']['door']
		key = self.fight_state['key']
		hero = self.fight_state['hero']
		node['count']['damage'] = 0

		if door:
			if key[door] == 0:
				return False

		for monster in node['count']['monster']:
			damage = hero.fight(monster)
			if damage < 0:
				return False
			node['count']['damage'] += damage

		if door:
			key[door] -= 1
		for k, v in node['count']['key'].items():
			key[k] += v

		hero.health += node['count']['potion']
		hero.attack += node['count']['gem']['attack']
		hero.defence += node['count']['gem']['defence']
		return True

	def out_node_fight(self, node):
		door = node['count']['door']
		key = self.fight_state['key']
		hero = self.fight_state['hero']
		damage = node['count']['damage']

		hero.health += damage
		if door:
			key[door] += 1
		for k, v in node['count']['key'].items():
			key[k] -= v
		hero.health -= node['count']['potion']
		hero.attack -= node['count']['gem']['attack']
		hero.defence -= node['count']['gem']['defence']

	#移入，remove该点，add该点的forward
	#移出，remove该点的forward，add该点
	def in_move_node(self, move):
		node = self.tree_map[move]
		if not self.in_node_fight(node):
			return False
		self.fight_state['move_node'].remove(node['number'])
		for pos, forward in node['way']['forward'].items():
			if len(forward['info']['area']) == 1 and len(forward['way']['forward']) == 0:
				continue
			self.fight_state['move_node'].add(forward['number'])
		return True

	def out_move_node(self, move):
		node = self.tree_map[move]
		self.fight_state['move_node'].add(node['number'])
		for pos, forward in node['way']['forward'].items():
			if len(forward['info']['area']) == 1 and len(forward['way']['forward']) == 0:
				continue
			self.fight_state['move_node'].remove(forward['number'])
		self.out_node_fight(node)

	num = 0

	def node_travel(self, node_list):
		self.num += 1
		for move in self.fight_state['move_node']:
			if not self.in_move_node(move):
				continue
			self.node_travel(node_list + [move])
			self.out_move_node(move)

	def tree_travel(self):
		self.node_travel([])
		print len(self.tree_map), self.num

	#遍历树，支持中途删除
	def tree_ergodic(self, func):
		move_list = set()
		while True:
			for move in set(self.tree_map.keys()) - move_list:
				func(self.tree_map[move])
				move_list.add(move)
				break
			else:
				break


	def get_ground_num(self):
		ground_num = 0
		for k in range(MazeSetting.floor):
			for i in range(MazeSetting.rows + 2):
				for j in range(MazeSetting.cols + 2):
					if self.get_type((k, i, j)) == MazeBase.ground:
						ground_num += 1
		print 'ground num:', ground_num

	def create(self):
		self.block_create()
		#self.show(lambda pos: self.get_type(pos))
		self.tree_create()
		self.tree_ergodic(self.set_node)
		self.tree_create(pre=False)

		#放置钥匙后，可靠路径在1w左右波动，最大出现过100w，有一次计算超时，完全在计算能力之内（超过若干时间的，超时之后停止计算并重新生成）
		self.set_item()
		#for k, v in self.tree_map.items():
		#	print v['number'], v['info']['area'], v['way']['forward'].keys(), v['way']['backward'].keys()

		#print self.door_num, len(self.tree_map)
		self.tree_travel()
		#self.get_ground_num()
		#self.show(lambda pos: self.get_type(pos))
		hero = self.fight_state['hero']
		print self.fight_state['key'], hero.health, hero.attack, hero.defence


	def show(self, format):
		for k in range(MazeSetting.floor):
			for i in range(MazeSetting.rows + 2):
				for j in range(MazeSetting.cols + 2):
					ret = format((k, i, j))
					if ret in [MazeBase.ground]:
						print ' ',
					else:
						print ret,
				print
			print

	def set_show(self):
		s = ''
		for i in range(MazeSetting.rows + 2):
			for j in range(MazeSetting.cols + 2):
				ret = self.get_type((0, i, j))
				if ret in [MazeBase.ground]:
					s += '  '
				else:
					s += str(ret) + ' '
			s += '\n'
		return s

	def get_show(self, show):
		self.maze[0] = [[{'type': int(col), 'value': 0} for col in row.replace('  ', ' 0').split(' ')] for row in show.split('\n')[1:-1]]


if __name__ == '__main__':
	maze = Maze()
	#maze.get_show(maze_show)
	#maze.show(lambda pos: maze.get_type(pos))
	maze.create()
	#print maze.set_show()