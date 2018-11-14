# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.clock import Clock

from menu import MenuLayout
from maze import Maze
from g import gmaze
gmaze.instance = Maze()

from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.videoplayer import VideoPlayer
from threading import Thread

from kivy.lang import Builder
Builder.load_string('''
<Init>:
    text: 'init'
    on_texture_size:
        print(self.text)
        self.load() if self.text == 'init' else None
        #self.value += 10
    #source: 'data/init.mpg'
    #state: 'play'
    #Label:
    #    text: 'init'
    #    on_texture_size:
    #        self.parent.load()
    #        #self.parent.remove_widget(self)
''')

class Init(Label, ProgressBar):
    def __init__(self, app=None, **kwargs):
        super(Init, self).__init__(**kwargs)
        self.app = app
        #Clock.schedule_interval(self.progress, 0.1)

    def init(self, dt=0):
        app = self.app
        app.menu = MenuLayout()
        Window.remove_widget(app.root)
        app.root = app.menu
        Window.add_widget(app.root)

    def progress(self, dt=0):
        print('step')
        self.value += 1

    def load(self, *args):
        print('init', args)
        Clock.schedule_once(self.init, 0)
        
        #t = Thread(target=self.init)
        #t.start()
