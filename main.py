#-*- coding:utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.label import Label

from maze import Maze


class mainApp(App):
	def build(self):
		maze = Maze()
		maze.create()
		s = maze.set_show()
		label = Label(text=s)
		return label

if __name__ == '__main__':
	mainApp().run()
