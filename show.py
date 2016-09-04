#-*- coding:utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle
from kivy.uix.behaviors import FocusBehavior
from kivy.clock import Clock

from kivy.lang import Builder
Builder.load_string('''
<Node>:
	size_hint: None, None
	size: 40, 40
	canvas:
		Rectangle:
			source: '121.png'
			pos: self.pos
			size: self.size
		Rectangle:
			source: '132.png'
			pos: self.pos
			size: self.size
''')


class ShowBase:
	size = 32
	step = 4

def logging(s):
	from kivy.logger import Logger
	Logger.warning(str(s))


class Node(Image):
	pass


class Schedule:
	from Queue import Queue

	def __init__(self):
		self.event = {}
		Clock.schedule_interval(self.run, 0)

	def run(self, t):
		if self.event.has_key(Clock.frames):
			while not self.event[Clock.frames].empty():
				func, step, args, kwargs = self.event[Clock.frames].get()
				func(step, *args, **kwargs)
			del self.event[Clock.frames]

	def trigger(self, func, iterator, interval, *args, **kwargs):
		while True: #有可能下一帧会立刻执行，保证该函数执行完前，该帧不执行
			frames = Clock.frames + 1
			old_frames = frames
			for step in iterator:
				frames += interval
				self.event.setdefault(frames, self.Queue())
				self.event[frames].put((func, step, args, kwargs))
			if old_frames == Clock.frames + 1:
				break

if 'Trigger' not in dir():
	Trigger = Schedule().trigger


class MoveHero(Image):
	def __init__(self, **kwargs):
		self.enable = True
		self.pos = kwargs.get('pos', (0, 0))
		self.size = (ShowBase.size, ShowBase.size)
		super(MoveHero, self).__init__(**kwargs)
		self.image = Image(source='data/action/hero/blue.png')
		self.texture = self.image.texture.get_region(0, 1, ShowBase.size, ShowBase.size)

	def next(self, step, key, moveable):
		move = {'up': 0, 'down': 3, 'left': 2, 'right': 1}
		self.texture = self.image.texture.get_region(step * ShowBase.size, move[key] * (ShowBase.size + 1) + 1, ShowBase.size, ShowBase.size)
		if moveable:
				x, y = self.pos
				if key == 'up':
					y += ShowBase.size / 4
				elif key == 'down':
					y -= ShowBase.size / 4
				elif key == 'left':
					x -= ShowBase.size / 4
				elif key == 'right':
					x += ShowBase.size / 4
				self.pos = x, y

	def move(self, key, moveable=True):
		Trigger(self.next, range(ShowBase.step)[::-1], 5, key, moveable)


#先放置地面，再放置其他的物品
#hero单独使用一个点
class Show(FocusBehavior, GridLayout):
	def __init__(self, **kwargs):
		self.rows = 3
		self.cols = 2
		self.spacing = 1
		super(Show, self).__init__(**kwargs)
		for i in xrange(self.rows * self.cols):
			self.add_widget(Node())

		#keyboard_on_key_down的必要条件
		self.focused = True
		self.movehero = MoveHero(pos=(10, 10))
		self.add_widget(self.movehero)

	def keyboard_on_key_down(self, window, keycode, text, modifiers):
		key = keycode[1]
		if key not in set(('up', 'down', 'left', 'right')):
			return False
		self.movehero.move(key)
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