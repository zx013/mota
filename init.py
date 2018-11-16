# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.clock import Clock

from menu import MenuLayout
from maze import Maze
from g import gmaze
gmaze.instance = Maze()

from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

from kivy.lang import Builder
Builder.load_string('''
<Init>:
    text: 'init'
    on_texture_size:
        print(self.text)
        self.load() if self.text == 'init' else None
''')

#android不生效，原因不明
class Init(Label, ProgressBar):
    def __init__(self, app=None, **kwargs):
        super(Init, self).__init__(**kwargs)
        self.app = app

    def init(self, dt=0):
        app = self.app
        app.menu = MenuLayout()
        Window.remove_widget(app.root)
        app.root = app.menu
        Window.add_widget(app.root)

    def load(self, *args):
        Clock.schedule_once(self.init, 0)
