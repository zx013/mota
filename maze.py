#-*- coding:utf-8 -*-
import random

#块状区域
#选择区域
#分支区域

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

	ground_temp = 2

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

	def get_around(self, pos):
		around = []
		z, x, y = pos
		if x > 0:
			around.append((z, x - 1, y))
		if x < MazeBase.rows + 1:
			around.append((z, x + 1, y))
		if y > 0:
			around.append((z, x, y - 1))
		if y < MazeBase.cols + 1:
			around.append((z, x, y + 1))
		return around
	
	def get_count(self, pos):
		if self.get_type(pos) == 1:
			return 0
		count = 0
		around = self.get_around(pos)
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

	def get_line(self, floor, pos1, pos2):
		link = []
		floor1, x1, y1 = pos1
		floor2, x2, y2 = pos2
		if floor1 != floor2:
			return False, link
		if x1 == x2:
			for y in range(*sorted((y1, y2)))[1:]:
				pos = (floor, x1, y)
				if self.get_type(pos):
					return False, link
				link.append(pos)
		elif y1 == y2:
			for x in range(*sorted((x1, x2)))[1:]:
				pos = (floor, x, y1)
				if self.get_type(pos):
					return False, link
				link.append(pos)
		return True, link

	def get_link(self, floor, pos1, pos2):
		link = []
		floor1, x1, y1 = pos1
		floor2, x2, y2 = pos2
		pos_list = ((floor, x1, y2), (floor, x2, y1))
		if random.choice((False, True)):
			pos_list = pos_list[::-1]
		for pos in pos_list:
			result, link1 = self.get_line(floor, pos1, pos)
			if not result:
				continue
			result, link2 = self.get_line(floor, pos, pos2)
			if not result:
				continue
			link += link1
			if pos not in (pos1, pos2):
				link.append(pos)
			link += link2
			return True, link
		return False, link

	def link_pos(self, floor, pos1, pos2, value):
		result, link = self.get_link(floor, pos1, pos2)
		if not result:
			return
		for pos in link:
			self.set_type(pos, value)

	def create_way(self, floor):
		start_pos = self.info[floor]['stairs_start']
		end_pos = self.info[floor]['stairs_end']
		self.link_pos(floor, start_pos, end_pos, MazeBase.ground_temp)
		

	def create(self, floor):
		self.create_floor(floor)
		self.create_stairs(floor)
		self.create_way(floor)


	def get_draw_enable(self, floor):
		draw_enable = []
		for i in range(1, MazeBase.rows + 1):
			for j in range(1, MazeBase.cols + 1):
				pos = (floor, i, j)
				if self.get_count(pos) == 4:
					draw_enable.append(pos)
		return draw_enable
	
	def draw_line(self, pos):
		z, x, y = pos
		operate = random.choice((-1, 1))
		if random.randint(0, 1):
			new_x = x
			while True:
				new_x = new_x + operate
				if self.get_count((z, new_x, y)) < 3:
					break
				if self.get_count((z, new_x + operate, y)) < 3:
					break
				self.maze[z][new_x][y]['type'] = 1
		else:
			new_y = y
			while True:
				new_y = new_y + operate
				if self.get_count((z, x, new_y)) < 3:
					break
				if self.get_count((z, x, new_y + operate)) < 3:
					break
				self.maze[z][x][new_y]['type'] = 1
	
	def draw(self, floor):
		for i in range(1000):
			draw_enable = self.get_draw_enable(floor)
			if not draw_enable:
				break
			draw_pos = random.choice(draw_enable)
			self.draw_line(draw_pos)

	def maze_block(self, ):
		pass



	def show(self, format):
		for k in range(MazeBase.floor):
			for i in range(MazeBase.rows + 2):
				for j in range(MazeBase.cols + 2):
					ret = format(self.maze, (k, i, j))
					if ret == 0:
						print ' ',
					else:
						print ret,
				print
			print


tree_node = {'floor': 0, 'empty': False, 'info': {'type': 0, 'pos': (0, 0), 'area': [], 'count': {'all': 0, 'ground': 0, 'wall': 0, 'item': 0, 'door': 0, 'monster': 0, 'stairs': 0, 'other': 0}}, 'way': {'forward': {}, 'backward': {}}}


if __name__ == '__main__':
	maze = Maze()
	#maze.draw(0)
	maze.create(0)
	maze.show(lambda self, pos: maze.get_type(pos))
	#maze_show(get_count)