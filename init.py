# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.clock import Clock

from menu import MenuLayout
from maze import Maze
from g import gmaze
gmaze.instance = Maze()

from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ToggleButtonBehavior
#from kivy.uix.progressbar import ProgressBar

from kivy.lang import Builder
Builder.load_string('''
#:import Setting setting.Setting
<Init1>:
    text: '测试init'
    font_size: 50
    multiple: 1
    Label:
        text: root.text
        font_size: root.font_size
        font_name: Setting.font_path
        color: (1, 1, 1, 1)
        outline_width: Setting.multiple
        outline_color: (0.25, 0.25, 0.25)
    Label:
        text: root.text
        font_size: root.font_size * root.multiple
        color: (1, 1, 0, 0.5)
        font_name: Setting.font_path
    #on_texture_size:
    #    print(self.text)
    #    self.load() if self.text == 'init' else None
''')

class Init1(FloatLayout, ToggleButtonBehavior):
    def __init__(self, app=None, **kwargs):
        super(Init, self).__init__(**kwargs)
        self.app = app
        self.size = Window.size
        Clock.schedule_once(self.disperse, 0.05)

    def disperse(self, dt):
        self.multiple += 0.01
        if self.multiple > 1.1:
            self.multiple = 1
        Clock.schedule_once(self.disperse, 0.05)

#android不生效，原因不明
class Init(Image):
    def __init__(self, app=None, **kwargs):
        super(Init, self).__init__(**kwargs)
        self.app = app
        self.size = Window.size
        self.load()

    def init(self, dt=0):
        app = self.app
        app.menu = MenuLayout()
        Window.remove_widget(app.root)
        app.root = app.menu
        Window.add_widget(app.root)

    def load(self, *args):
        Clock.schedule_once(self.init, 0)
