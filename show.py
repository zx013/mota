#-*- coding:utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle
from kivy.uix.behaviors import FocusBehavior

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



class Move:
	def __init__(self, **kwargs):
		canvas = kwargs['canvas']
		self.image = Image(source='data/action/hero/blue.png')
		with canvas:
			self.rect = Rectangle(texture=self.image.texture.get_region(0, 1, 32, 32), pos=(10, 10), size=(80, 80))
		self.step = 0

	def next(self, direct):
		move = {'up': 0, 'down': 3, 'left': 2, 'right': 1}
		if direct not in move.keys():
			return False
		texture = self.image.texture.get_region(self.step * ShowBase.size, move[direct] * (ShowBase.size + 1) + 1, ShowBase.size, ShowBase.size)
		self.rect.texture = texture
		x, y = self.rect.pos
		if direct == 'up':
			y += 20
		elif direct == 'down':
			y -= 20
		elif direct == 'left':
			x -= 20
		elif direct == 'right':
			x += 20
		self.rect.pos = x, y
		self.step = (self.step + 1) % ShowBase.step
		return True

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
		self.move = Move(canvas=self.canvas.after)

	def on_touch_down(self, touch):
		super(Show, self).on_touch_down(touch)
		return True

	def keyboard_on_key_down(self, window, keycode, text, modifiers):
		self.move.next(keycode[1])
		logging((keycode, text))
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