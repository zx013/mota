#-*- coding:utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle
from kivy.uix.behaviors import FocusBehavior
from kivy.clock import Clock


class ShowBase:
	size = 32
	step = 4

def logging(s):
	from kivy.logger import Logger
	Logger.warning(str(s))


from Queue import Queue

class Schedule:
	def __init__(self):
		self.event = {}
		Clock.schedule_interval(self.run, 0)

	def run(self, t):
		if self.event.has_key(Clock.frames):
			while not self.event[Clock.frames].empty():
				func, step, kwargs = self.event[Clock.frames].get()
				func(step, **kwargs)
			del self.event[Clock.frames]

	#func: ¶¨Ê±´¥·¢µÄº¯Êý
	#iterator: Éú³ÉÆ÷£¬±éÀúµÄÖµÒÀ´Î´«¸øfunc
	#interval: º¯Êý´¥·¢¼ä¸ô£¬µ¥Î»ÎªframesµÄÊýÁ¿
	#cycle: Ñ­»·£¬¸ºÊýÎªÎÞÏÞÑ­»·
	#kwargs: º¯Êý²ÎÊý
	def trigger(self, func, iterator, interval, cycle, **kwargs):
		frames = Clock.frames
		for step in iter(iterator):
			frames += interval
			self.event.setdefault(frames, Queue())
			self.event[frames].put((func, step, kwargs))
		if cycle > 1 or cycle < 0:
			self.event[frames].put((lambda step, **kwargs: self.trigger(func, iterator, interval, cycle - 1, **kwargs), -1, kwargs))

if 'Trigger' not in dir():
	Trigger = Schedule().trigger


import os

class CacheBase:
	def __init__(self):
		self.image_dir = 'data'
		self.load_image()

	def load_image(self):
		self.data = {}
		for path, dir_list, file_list in os.walk(self.image_dir):
			for file_name in file_list:
				name = '/'.join((path, file_name)).replace('\\', '/')
				texture = Image(source=name).texture
				x, y = texture.size
				x_time = x / ShowBase.size
				y_time = y / ShowBase.size
				x_size = x / x_time
				y_size = y / y_time
				x_offset = x_size - ShowBase.size
				y_offset = y_size - ShowBase.size
				self.data[name] = {}
				for i in range(x_time):
					for j in range(y_time):
						self.data[name][(i, j)] = texture.get_region(i * x_size + x_offset, j * y_size + y_offset, ShowBase.size, ShowBase.size)

	def get_image(self, name, pos=(0, 0)):
		name = '/'.join((self.image_dir, name)).replace('\\', '/')
		return self.data[name][pos]

if 'Cache' not in dir():
	Cache = CacheBase()


class Move(Image):
	def __init__(self, **kwargs):
		self.enable = True
		self.pos = kwargs.get('pos', (0, 0))
		self.size = (ShowBase.size, ShowBase.size)
		super(Move, self).__init__(**kwargs)
		self.texture = Cache.get_image('action/hero/blue.png', (0, 3))

	def next(self, step, key, moveable):
		if self.enable:
			move = {'up': 0, 'down': 3, 'left': 2, 'right': 1}
			self.texture = Cache.get_image('action/hero/blue.png', (step, move[key]))
			if moveable:
					x, y = self.pos
					if key == 'up':
						y += ShowBase.size / ShowBase.step
					elif key == 'down':
						y -= ShowBase.size / ShowBase.step
					elif key == 'left':
						x -= ShowBase.size / ShowBase.step
					elif key == 'right':
						x += ShowBase.size / ShowBase.step
					self.pos = x, y

	def __call__(self, key, moveable=True):
		Trigger(self.next, range(ShowBase.step)[::-1], 5, 1, key=key, moveable=moveable)


from maze2 import MazeBase

class Node(Image):
	def __init__(self, **kwargs):
		self.enable = True
		self.pos = kwargs.get('pos', (0, 0))
		self.size = (ShowBase.size, ShowBase.size)
		super(Node, self).__init__(**kwargs)
		node = kwargs['node']
		if node.Type == MazeBase.Type.Static.ground:
			self.texture = Cache.get_image('basic/ground.png', (0, 0))
		elif node.Type == MazeBase.Type.Static.wall:
			self.texture = Cache.get_image('basic/wall.png', (0, 1))
		elif node.Type == MazeBase.Type.Static.stair:
			if node.Value == MazeBase.Value.Stair.up:
				self.texture = Cache.get_image('basic/stair.png', (1, 0))
			elif node.Value == MazeBase.Value.Stair.down:
				self.texture = Cache.get_image('basic/stair.png', (0, 0))
		elif node.Type == MazeBase.Type.Static.door:
			if node.Value == MazeBase.Value.Color.yellow:
				self.texture = Cache.get_image('basic/door.png', (0, 0))
			elif node.Value == MazeBase.Value.Color.blue:
				self.texture = Cache.get_image('basic/door.png', (1, 0))
			elif node.Value == MazeBase.Value.Color.red:
				self.texture = Cache.get_image('basic/door.png', (2, 0))
			elif node.Value == MazeBase.Value.Color.green:
				self.texture = Cache.get_image('basic/door.png', (3, 0))
		elif node.Type == MazeBase.Type.Active.monster:
			self.texture = Cache.get_image('action/monster/003.png', (0, 1))
		else:
			logging(node)

	def show(self):
		pass

	def next(self, step, num):
		if self.enable:
			self.texture = self.image.texture.get_region(step * ShowBase.size, num * ShowBase.size, ShowBase.size, ShowBase.size)

	def __call__(self, num):
		Trigger(self.next, range(ShowBase.step)[::-1], 15, -1, num=num)

#ÏÈ·ÅÖÃµØÃæ£¬ÔÙ·ÅÖÃÆäËûµÄÎïÆ·
#heroµ¥¶ÀÊ¹ÓÃÒ»¸öµã
class Show(FocusBehavior, GridLayout):
	def __init__(self, **kwargs):
		#from maze import Level, MazeSetting
		#Level.next()
		#floor = Level.maze.maze[0]
		from maze2 import Maze2, MazeSetting
		floor = Maze2().maze[0]

		self.rows = MazeSetting.rows + 2
		self.cols = MazeSetting.cols + 2

		self.size_hint = (None, None)
		self.size = (self.cols * ShowBase.size, self.rows * ShowBase.size)
		super(Show, self).__init__(**kwargs)

		texture = Cache.get_image('basic/ground.png', (0, 0))
		with self.canvas:
			for i in range(self.rows):
				for j in range(self.cols):
					Rectangle(texture=texture, pos=(self.x + j * ShowBase.size, self.y + i * ShowBase.size), size=(ShowBase.size, ShowBase.size))
		for i in range(self.rows):
			for j in range(self.cols):
				node = Node(node=floor[i][j])
				self.add_widget(node)

		#keyboard_on_key_downµÄ±ØÒªÌõ¼þ
		self.focused = True
		self.move = Move(pos=(100, 100))
		#self.add_widget(self.move)

	def keyboard_on_key_down(self, window, keycode, text, modifiers):
		key = keycode[1]
		if key not in set(('up', 'down', 'left', 'right')):
			return False
		self.move(key)
		return True

	#¼ÓÔØÍ¼Æ¬£¬È¡ÆäÖÐÄ³¸öÎ»ÖÃ£¨Ê¹ÓÃ»º´æ£©
	def load(self):
		pass

	#ÒÆ¶¯µ½ÏàÁÚµÄÎ»ÖÃ
	def move(self):
		#ÒÀ´Î¼ÓÔØhero¶¯×÷
		#½«hero·ÅÖÃÔÚÁ½¸öµãÖ®¼ä
		pass

	#Ô­µØÌ¤²½
	def block(self):
		#ÒÀ´Î¼ÓÔØhero¶¯×÷
		pass

	#¹ÖÎïµÄ¶¯×÷
	def monster(self):
		#Çå¿Õµã
		#ÒÀ´Î¼ÓÔØmonster¶¯×÷
		pass

	#Õ½¶·
	def fight(self):
		#Í£Ö¹fightÇøÓòmonsterµÄ¶¯×÷
		#ÔÚmonsterÉÏÃæµ¯³öÊý×Ö²¢ÏÔÊ¾¶¯»­Ð§¹û
		pass

	#¿ªÃÅ
	def door(self):
		#ÒÀ´Î¼ÓÔØdoor¶¯×÷
		pass

	#Çå³ý
	def clear(self):
		#Ö±½ÓÓÃµØÃæ¸²¸Ç
		pass

	def die(self):
		pass