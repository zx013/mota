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


class Schedule:
	from Queue import Queue

	def __init__(self):
		self.event = {}
		Clock.schedule_interval(self.run, 0)

	def run(self, t):
		if self.event.has_key(Clock.frames):
			while not self.event[Clock.frames].empty():
				func, step, kwargs = self.event[Clock.frames].get()
				func(step, **kwargs)
			del self.event[Clock.frames]

	#func: 定时触发的函数
	#iterator: 生成器，遍历的值依次传给func
	#interval: 函数触发间隔，单位为frames的数量
	#cycle: 循环，负数为无限循环
	#kwargs: 函数参数
	def trigger(self, func, iterator, interval, cycle, **kwargs):
		frames = Clock.frames
		for step in iter(iterator):
			frames += interval
			self.event.setdefault(frames, self.Queue())
			self.event[frames].put((func, step, kwargs))
		if cycle > 1 or cycle < 0:
			self.event[frames].put((lambda step, **kwargs: self.trigger(func, iterator, interval, cycle - 1, **kwargs), -1, kwargs))

if 'Trigger' not in dir():
	Trigger = Schedule().trigger


class Data:
	import os

	def __init__(self):
		pass

	def put(self):
		self.data = {}
		for path, dir_list, file_list in self.os.walk('data'):
			self.data[path] = {}
			for file_name in file_list:
				pass

	def get(self):
		pass


class Move(Image):
	def __init__(self, **kwargs):
		self.enable = True
		self.pos = kwargs.get('pos', (0, 0))
		self.size = (ShowBase.size, ShowBase.size)
		super(Move, self).__init__(**kwargs)
		self.image = Image(source='data/action/hero/blue.png')
		self.texture = self.image.texture.get_region(0, 1, ShowBase.size, ShowBase.size)

	def next(self, step, key, moveable):
		if self.enable:
			move = {'up': 0, 'down': 3, 'left': 2, 'right': 1}
			self.texture = self.image.texture.get_region(step * ShowBase.size, move[key] * (ShowBase.size + 1) + 1, ShowBase.size, ShowBase.size)
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


class Node(Image):
	def __init__(self, **kwargs):
		self.enable = True
		self.pos = kwargs.get('pos', (0, 0))
		self.size = (ShowBase.size, ShowBase.size)
		super(Node, self).__init__(**kwargs)
		#self.image = Image(source='data/action/monster/003.png')
		#self.texture = self.image.texture.get_region(0, 0, ShowBase.size, ShowBase.size)
		self.image = Image(source='data/basic/wall.png')
		self.texture = self.image.texture.get_region(0, 32, ShowBase.size, ShowBase.size)

	def show(self):
		pass

	def next(self, step, num):
		if self.enable:
			self.texture = self.image.texture.get_region(step * ShowBase.size, num * ShowBase.size, ShowBase.size, ShowBase.size)

	def __call__(self, num):
		Trigger(self.next, range(ShowBase.step)[::-1], 15, -1, num=num)

#先放置地面，再放置其他的物品
#hero单独使用一个点
class Show(FocusBehavior, GridLayout):
	def __init__(self, **kwargs):
		from maze import Maze, MazeSetting
		maze = Maze()
		floor = maze.maze[0]

		self.rows = 1 #MazeSetting.rows
		self.cols = 2 #MazeSetting.cols

		self.size_hint = (None, None)
		self.size = (self.cols * ShowBase.size, self.rows * ShowBase.size)
		super(Show, self).__init__(**kwargs)

		texture = Image(source='data/basic/ground.png').texture
		with self.canvas:
			for i in xrange(self.cols):
				for j in xrange(self.rows):
					Rectangle(texture=texture, pos=(self.x + i * ShowBase.size, self.y + j * ShowBase.size), size=(ShowBase.size, ShowBase.size))
		for i in xrange(self.cols):
			for j in xrange(self.rows):
				node = Node(node=floor[i][j])
				self.add_widget(node)

		#keyboard_on_key_down的必要条件
		self.focused = True
		self.move = Move(pos=(100, 100))
		#self.add_widget(self.move)

	def keyboard_on_key_down(self, window, keycode, text, modifiers):
		key = keycode[1]
		if key not in set(('up', 'down', 'left', 'right')):
			return False
		self.move(key)
		return True

	#加载图片，取其中某个位置（使用缓存）
	def load(self):
		pass

	#移动到相邻的位置
	def move(self):
		#依次加载hero动作
		#将hero放置在两个点之间
		pass

	#原地踏步
	def block(self):
		#依次加载hero动作
		pass

	#怪物的动作
	def monster(self):
		#清空点
		#依次加载monster动作
		pass

	#战斗
	def fight(self):
		#停止fight区域monster的动作
		#在monster上面弹出数字并显示动画效果
		pass

	#开门
	def door(self):
		#依次加载door动作
		pass

	#清除
	def clear(self):
		#直接用地面覆盖
		pass

	def die(self):
		pass