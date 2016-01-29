#-*- coding:utf-8 -*-
import random

#块状区域
#选择区域
#分支区域

def add_pos(pos1, pos2):
	z1, x1, y1 = pos1
	x2, y2 = pos2
	pos = z1, x1 + x2, y1 + y2
	return pos

class MazeBase:
	floor = 1
	rows = 13
	cols = 13

	ground = 0
	wall = 1
	item = 2
	door = 3
	monster = 4
	stairs = 5
	other = 100

	ground_bar_temp = 7
	ground_block_temp = 8
	

	stairs_start = 1
	stairs_end = 2

	maze_node = {'type': 0, 'value': 0}
	maze_inside = dict(maze_node)
	maze_outside = dict(maze_node)
	maze_outside['type'] = 1

class Maze:
	maze = []
	def __init__(self):
		for k in range(MazeBase.floor):
			floor_area = []
			for i in range(MazeBase.rows + 2):
				rows_area = []
				for j in range(MazeBase.cols + 2):
					if i in [0, MazeBase.rows + 1] or j in [0, MazeBase.cols + 1]:
						rows_area.append(dict(MazeBase.maze_outside))
					else:
						rows_area.append(dict(MazeBase.maze_inside))
				floor_area.append(rows_area)
			self.maze.append(floor_area)
		#maze[0][2][2]['type'] = 1
		#maze[0][3][3]['type'] = 1

	def get_type(self, pos):
		z, x, y = pos
		value = self.maze[z][x][y]['type']
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
		if x < MazeBase.rows + 2 - num:
			around.append((z, x + num, y))
		if y > num - 1:
			around.append((z, x, y - num))
		if y < MazeBase.cols + 2 - num:
			around.append((z, x, y + num))
		return around

	def get_count(self, pos):
		if self.get_type(pos) == 1:
			return 0
		count = 0
		around = self.get_around(pos, 1)
		for pos in around:
			if self.get_type(pos) != 1:
				count += 1
		return count

#生成起止点
#生成最短路径
#路径调整
#路径空余插入区块，不足以插入区块的部分插入路径
#在适当的位置开出缺口，使全地图连通
#分割大区块

	#将type1改变为type2
	def change(self, floor, type1, type2):
		for i in range(1, MazeBase.rows + 1):
			for j in range(1, MazeBase.cols + 1):
				pos = (floor, i, j)
				if self.get_type(pos) == type1:
					self.set_type(pos, type2)

	info = {}
	def create_floor(self, floor):
		self.info[floor] = {}

	def create_stairs(self, floor):
		#获取上一层的终止点，没有则随机生成
		start_x = random.randint(1, MazeBase.rows)
		start_y = random.randint(1, MazeBase.cols)
		start_pos = (floor, start_x, start_y)
		self.set_type(start_pos, MazeBase.stairs)
		self.set_value(start_pos, MazeBase.stairs_start)
		self.info[floor]['stairs_start'] = start_pos
		while True:
			end_x = random.randint(1, MazeBase.rows)
			end_y = random.randint(1, MazeBase.cols)
			if abs(end_x - start_x) > 1 or abs(end_y - start_y) > 1:
				break
		end_pos = (floor, end_x, end_y)
		self.set_type(end_pos, MazeBase.stairs)
		self.set_value(end_pos, MazeBase.stairs_end)
		self.info[floor]['stairs_end'] = end_pos

	def get_line(self, pos1, pos2, check):
		link = []
		floor1, x1, y1 = pos1
		floor2, x2, y2 = pos2
		if floor1 != floor2:
			return False, link
		if x1 == x2:
			for y in range(*sorted((y1, y2)))[1:]:
				pos = (floor1, x1, y)
				if self.get_type(pos):
					if check:
						return False, link
					else:
						continue
				link.append(pos)
		elif y1 == y2:
			for x in range(*sorted((x1, x2)))[1:]:
				pos = (floor1, x, y1)
				if self.get_type(pos):
					if check:
						return False, link
					else:
						continue
				link.append(pos)
		return True, link

	def get_link(self, floor, pos1, pos2):
		link = []
		floor1, x1, y1 = pos1
		floor2, x2, y2 = pos2
		pos3 = (floor, x1, y2)
		pos4 = (floor, x2, y1)
		result, link1 = self.get_line(pos1, pos3, False)
		result, link2 = self.get_line(pos1, pos4, False)
		link1.append(pos3)
		link2.append(pos1)
		pos_list = link1 + link2
		pos_list = random.sample(pos_list, len(pos_list))
		for pos_turn1 in pos_list:
			if pos_turn1 in link1:
				pos_turn2 = (floor, x2, pos_turn1[2])
			elif pos_turn1 in link2:
				pos_turn2 = (floor, pos_turn1[1], y2)

			result, link_turn1 = self.get_line(pos1, pos_turn1, True)
			if not result:
				continue
			result, link_turn2 = self.get_line(pos_turn1, pos_turn2, True)
			if not result:
				continue
			result, link_turn3 = self.get_line(pos_turn2, pos2, True)
			if not result:
				continue

			link += link_turn1
			if pos_turn1 not in (pos1, pos2):
				link.append(pos_turn1)
			link += link_turn2
			if pos_turn2 not in (pos1, pos2):
				link.append(pos_turn2)
			link += link_turn3
			return True, link
		return False, link

	def link_pos(self, floor, pos1, pos2, value):
		result, link = self.get_link(floor, pos1, pos2)
		if not result:
			return
		print link
		for pos in link:
			self.set_type(pos, value)

	def create_way(self, floor):
		start_pos = self.info[floor]['stairs_start']
		end_pos = self.info[floor]['stairs_end']
		self.link_pos(floor, start_pos, end_pos, MazeBase.ground_block_temp)

	def create(self, floor):
		self.create_floor(floor)
		self.create_stairs(floor)
		self.create_way(floor)


#填充m*n的方格
#处理多层的墙
#建立通道

	def block_fill(self, floor, width, height):
		fill_pos = []
		for x in range(1, MazeBase.rows + 2 - height):
			for y in range(1, MazeBase.cols + 2 - width):
				fill_pos.append((floor, x, y))
		fill_pos = random.sample(fill_pos, len(fill_pos))
		for pos in fill_pos:
			z, x, y = pos
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
							if height == 1 or width == 1:
								fill_type = MazeBase.ground_bar_temp
							else:
								fill_type = MazeBase.ground_block_temp
						else:
							fill_type = MazeBase.wall
						self.set_type((floor, i, j), fill_type)
				break


	#| 0 0 | 0 | 0 1 1 0 | 0 1 1 0
	#| 1 1 | 1 | 0 1 1 0 |
	#| 1 1 | 1 |
	#| 0 0 | 0 |
	def block_check(self, floor):
		pass


	def show(self, format):
		for k in range(MazeBase.floor):
			for i in range(MazeBase.rows + 2):
				for j in range(MazeBase.cols + 2):
					ret = format(self.maze, (k, i, j))
					if ret in [MazeBase.ground, MazeBase.ground_bar_temp, MazeBase.ground_block_temp]:
						print ' ',
					else:
						print ret,
				print
			print

'''
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
1     1 1 1 1 1       1     1
1     1       1       1     1
1     1       1 1 1 1 1     1
1 1 1 1 1 1 1 1 1 1 1 1 1   1
1 1       1     1       1   1
1 1       1     1       1   1
1 1 1 1 1 1 1   1 1 1 1 1   1
1   1       1   1       1   1
1   1       1   1       1   1
1   1 1 1 1 1 1 1 1 1 1 1   1
1 1 1 1 1 1       1 1 1 1 1 1
1 1       1       1 1       1
1 1       1 1 1 1 1 1       1
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
'''

tree_node = {'floor': 0, 'empty': False, 'info': {'type': 0, 'pos': (0, 0), 'area': [], 'count': {'all': 0, 'ground': 0, 'wall': 0, 'item': 0, 'door': 0, 'monster': 0, 'stairs': 0, 'other': 0}}, 'way': {'forward': {}, 'backward': {}}}


if __name__ == '__main__':
	maze = Maze()
	#maze.create(0)
	for i in range(8):
		r = random.randint(1, 4)
		maze.block_fill(0, r, 5 - r)
	maze.show(lambda self, pos: maze.get_type(pos))
	#maze.show(maze.get_count, 2)