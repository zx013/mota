# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 18:17:43 2018

@author: zx013
"""

'''
import sys
import platform
if platform.system().lower() == 'windows':
    from build import build
    build()
    sys.exit(0)
'''


from jnius import autoclass #, cast
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from maze import Maze

'''
静态
路径，行，列

动态，动作（移动/消除）
路径，行，列，方向（按行还是按列）
'''
class ShowBase:
    size = 32

class BaseImage(Image):
    def __init__(self, path, pos, **kwargs):
        super(BaseImage, self).__init__(source=path, size_hint=(None, None), **kwargs)

        self.static = self.get_texture(path, pos)
        self.action = []
        self.index = 0
        self.texture = self.static[self.index]

    def real_pos(self, pos):
        row, col = pos
        weight, height = self.texture.size
        return col * ShowBase.size, height - (row + 1) * ShowBase.size

    def get_texture(self, path, pos):
        texture = []
        try:
            row, col = pos
            if isinstance(row, int):
                if isinstance(col, int):
                    pos_list = [(row, col)]
                else:
                    pos_list = [(row, c) for c in col]
            else:
                if isinstance(col, int):
                    pos_list = [(r, col) for r in row]
                else:
                    pos_list = []
    
            for pos in pos_list:
                row, col = self.real_pos(pos)
                texture.append(self.texture.get_region(row, col, ShowBase.size, ShowBase.size))
        except Exception as ex:
            print(ex)                
        
        return texture

    def add_action(self, path, pos):
        self.action = self.get_texture(path, pos)


    def next(self, dt):
        self.index += 1
        self.index %= len(self.static)
        self.texture = self.static[self.index]


class Mota(App):
    def build(self):
        self.maze = Maze()
        self.maze.update()
        try:
            #self.PythonActivity = autoclass('org.renpy.android.PythonActivity')
            #self.CurrentActivity = cast('android.app.Activity', self.PythonActivity.mActivity)
            #self.IndependentVideoManager = autoclass('com.pad.android_independent_video_sdk.IndependentVideoManager')
            #self.IndependentVideoListener = autoclass('com.pad.android_independent_video_sdk.IndependentVideoListener')
            #self.IndependentVideoAvailableState = autoclass('com.pad.android_independent_video_sdk.IndependentVideoAvailableState')
            javaclass = autoclass('com.test.JavaClass')
            text = javaclass().show()
        except Exception as ex:
            text = str(ex)
        self.image = BaseImage('data/other/door.png', (0, 2))
        self.button = Button(text=text, on_press=self.show)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.image)
        #self.layout.add_widget(self.button)
        
        Clock.schedule_interval(self.image.next, 1)
        return self.layout

    def on_start(self):
        try:
            #self.IndependentVideoManager.newInstance().init(False)
            text = 'start success'
        except Exception as ex:
            text = str(ex)
        self.button.text = text
        #self.IndependentVideoManager.newInstance().updateUserID('zx')

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def show(self, *args):
        try:
            #self.IndependentVideoManager.newInstance().checkVideoAvailable(self.CurrentActivity)
            text = 'show success'
        except Exception as ex:
            text = str(ex)
        self.button.text = text

if __name__ == '__main__':
    mota = Mota()
    mota.run()
    mota.stop()
