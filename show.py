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

#先放置地面，再放置其他的物品
#hero单独使用一个点
class Show(FocusBehavior, GridLayout):
	def __init__(self, **kwargs):
		self.rows = 3
		self.cols = 2
		#self.spacing = 1
		super(Show, self).__init__(**kwargs)
		for i in xrange(self.rows * self.cols):
			self.add_widget(Node())

		#keyboard_on_key_down的必要条件
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