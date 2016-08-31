#-*- coding:utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle

from kivy.lang import Builder
Builder.load_file('show.kv')


def logging(s):
	from kivy.logger import Logger
	Logger.warning(str(s))

class Node(Image):
	pass


#�ȷ��õ��棬�ٷ�����������Ʒ
#hero����ʹ��һ����
class Show(GridLayout):
	def __init__(self, **kwargs):
		self.rows = 3
		self.cols = 2
		self.spacing = 1
		super(Show, self).__init__(**kwargs)
		#for i in xrange(self.rows * self.cols):
		#	self.add_widget(Node())

		self.check = True
		self.image = Image(source='011.png')
		with self.canvas.after:
			self.rect = Rectangle(texture=self.image.texture.get_region(0, 0, 32, 32), pos=(10, 550), size=(40, 40))

	def draw_hero(self):
		self.rect.texture = self.image.texture.get_region(0, 0, 32, 32) if self.check else self.image.texture.get_region(32, 32, 32, 32)
		self.rect.pos = (20, 500)
		self.check = not self.check

	def on_touch_down(self, touch):
		self.draw_hero()
		logging(self.children)
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