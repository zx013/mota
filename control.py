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

	def move_pos(self, pos):
		pass

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