#-*- coding:utf-8 -*-
from maze import MazeBase, MazeSetting

'''
class MazeBase:
	ground = 0
	wall = 1
	item = 2
	door = 3
	monster = 4
	stairs = 5
	other = 100
'''

class MoveBase:
	#direct = set('up', 'down', 'left', 'right')
	up = (-1, 0)
	down = (1, 0)
	left = (0, -1)
	right = (0, 1)


class Move:
	def __init__(self, maze, pos):
		self.maze = maze
		self.pos = pos

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


	def move_direct(self, direct):
		z, x, y = self.pos
		move_x, move_y = direct
		pos = z, x + move_x, y + move_y
		print self.get_type(pos)


	def get_around(self, pos):
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
		return {pos for pos in around if self.get_type(pos) != MazeBase.wall}

	def get_around_list(self, pos_list, num):
		around_list = set()
		for pos in pos_list:
			around_list |= self.get_around(pos)
		around_list -= pos_list | self.way[num - 1]
		return around_list

	def get_way(self, pos, num):
		way = []
		for i in xrange(num - 1, 0, -1):
			old_z, old_x, old_y = pos
			new_z, new_x, new_y = list(self.get_around(pos) & self.way[i])[0]
			pos = new_z, new_x, new_y
			way.append((new_x - old_x, new_y - old_y))
		return way[::-1]

	def move_pos(self, pos):
		if self.get_type(pos) == MazeBase.wall:
			return
		self.way = {0: set()}
		around = set([self.pos])
		num = 1
		self.way[num] = around
		while around:
			around = self.get_around_list(around, num)
			num += 1
			self.way[num] = around
			if pos in around:
				return self.get_way(pos, num)

class Control:
	pass


if __name__ == '__main__':
	from maze import Maze
	maze = Maze()
	maze.create()
	maze.show(lambda pos: maze.get_type(pos))

	stairs_start = maze.info[0]['stairs_start']
	stairs_end = maze.info[0]['stairs_end']
	print stairs_start, stairs_end
	#print maze.tree_map[1]['info']['area']

	move = Move(maze.maze, stairs_start)
	move.move_direct(MoveBase.up)
	move.move_direct(MoveBase.down)
	move.move_direct(MoveBase.left)
	move.move_direct(MoveBase.right)
	print move.move_pos(stairs_end)