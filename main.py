#-*- coding:utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.app import App
from show import Show


class mainApp(App):
	def build(self):
		show = Show()
		return show

if __name__ == '__main__':
	mainApp().run()
