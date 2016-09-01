#-*- coding:utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle
from kivy.uix.behaviors import FocusBehavior
from kivy.clock import Clock

from kivy.lang import Builder
Builder.load_file('show.kv')


class ShowBase:
	size = 32
	step = 4

def logging(s):
	from kivy.logger import Logger
	Logger.warning(str(s))



class Node(Image):
	pass



class MoveHero:
	def __init__(self, **kwargs):
		canvas = kwargs['canvas']
		pos = kwargs['pos']
		self.image = Image(source='data/action/hero/blue.png')
		with canvas:
			self.rect = Rectangle(texture=self.image.texture.get_region(0, 1, ShowBase.size, ShowBase.size), pos=pos, size=(ShowBase.size, ShowBase.size))

	def next(self, key, is_move=True):
		move = {'up': 0, 'down': 3, 'left': 2, 'right': 1}
		for step in xrange(ShowBase.step):
			texture = self.image.texture.get_region(step * ShowBase.size, move[key] * (ShowBase.size + 1) + 1, ShowBase.size, ShowBase.size)
			self.rect.texture = texture
			if is_move:
				x, y = self.rect.pos
				if key == 'up':
					y += ShowBase.size / 4
				elif key == 'down':
					y -= ShowBase.size / 4
				elif key == 'left':
					x -= ShowBase.size / 4
				elif key == 'right':
					x += ShowBase.size / 4
				self.rect.pos = x, y
			yield

#�ȷ��õ��棬�ٷ�����������Ʒ
#hero����ʹ��һ����
class Show(FocusBehavior, GridLayout):
	def __init__(self, **kwargs):
		self.rows = 3
		self.cols = 2
		#self.spacing = 1
		super(Show, self).__init__(**kwargs)
		for i in xrange(self.rows * self.cols):
			self.add_widget(Node())

		#keyboard_on_key_down�ı�Ҫ����
		self.focused = True
		self.movehero = MoveHero(canvas=self.canvas.after, pos=(10, 10))

	def on_touch_down(self, touch):
		super(Show, self).on_touch_down(touch)
		return True

	def keyboard_on_key_down(self, window, keycode, text, modifiers):
		key = keycode[1]
		if key not in set(('up', 'down', 'left', 'right')):
			return False
		for i in self.movehero.next(key):
			Clock.usleep(100000)
		#Clock.create_trigger(self.movehero.next, key)()
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