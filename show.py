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


#先放置地面，再放置其他的物品
#hero单独使用一个点
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