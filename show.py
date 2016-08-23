#-*- coding:utf-8 -*-
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout

#先放置地面，再放置其他的物品
class Show(GridLayout):
	#移动到相邻的位置
	def move(self):
		pass

	#原地踏步
	def block(self):
		pass

	#怪物的动作
	def monster(self):
		pass

	#战斗
	def fight(self):
		pass

	#清除
	def clear(self):
		pass

	def die(self):
		pass