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
		while True: #�п�����һ֡������ִ�У���֤�ú���ִ����ǰ����֡��ִ��
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


#�ȷ��õ��棬�ٷ�����������Ʒ
#hero����ʹ��һ����
class Show(FocusBehavior, GridLayout):
	def __init__(self, **kwargs):
		self.rows = 3
		self.cols = 2
		self.spacing = 1
		super(Show, self).__init__(**kwargs)
		for i in xrange(self.rows * self.cols):
			self.add_widget(Node())

		#keyboard_on_key_down�ı�Ҫ����
		self.focused = True
		self.movehero = MoveHero(pos=(10, 10))
		self.add_widget(self.movehero)

	def keyboard_on_key_down(self, window, keycode, text, modifiers):
		key = keycode[1]
		if key not in set(('up', 'down', 'left', 'right')):
			return False
		self.movehero.move(key)
		return True

	#����ͼƬ��ȡ����ĳ��λ�ã�ʹ�û��棩
	def load(self):
		pass

	#�ƶ������ڵ�λ��
	def move(self):
		#���μ���hero����
		#��hero������������֮��
		pass

	#ԭ��̤��
	def block(self):
		#���μ���hero����
		pass

	#����Ķ���
	def monster(self):
		#��յ�
		#���μ���monster����
		pass

	#ս��
	def fight(self):
		#ֹͣfight����monster�Ķ���
		#��monster���浯�����ֲ���ʾ����Ч��
		pass

	#����
	def door(self):
		#���μ���door����
		pass

	#���
	def clear(self):
		#ֱ���õ��渲��
		pass

	def die(self):
		pass