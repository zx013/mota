# -*- coding: utf-8 -*-
"""
@author: zx013
"""

'''
楼层跳跃
存档功能（地图存档，剧情存档）
'''
from kivy.utils import platform

#打包apk使用
build_apk = False
if build_apk:
    import sys
    if platform == 'win':
        from build import build
        build()
        sys.exit()

from kivy.app import App
from setting import Setting #必须先加载setting，这样multiple就可以最先初始化
from kivy.config import Config

if platform == 'android':
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.renpy.android.PythonActivity')
    CurrentActivity = cast('android.app.Activity', PythonActivity.mActivity)
    #CurrentActivity.removeLoadingScreen()
    display = CurrentActivity.getWindowManager().getDefaultDisplay()
    height = display.getHeight()
    width = display.getWidth()
    Setting.multiple = width / (Setting.row_show * Setting.pos_size) / (1 + Setting.status_size)
    Setting.rotation = 270

height = int((1 + Setting.status_size) * Setting.row_show * Setting.pos_real)
width = int(Setting.col_show * Setting.pos_real)

if Setting.rotation in (90, 270):
    height, width = width, height

#默认字体没有生效，很奇怪
Config.set('graphics', 'height', height)
Config.set('graphics', 'width', width)
Config.set('graphics', 'default_font', Setting.font_path)
Config.set('graphics', 'resizable', 0)

from kivy.core.window import Window
Window.rotation = Setting.rotation
if platform in ('win', 'linux'):
    Window.set_title(Setting.title)
    Window.set_icon(Setting.icon_path)
    Setting.status_speed = 20
else:
    Setting.status_speed = 100
#Window.fullscreen = True


from menu import MenuLayout

class MotaApp(App):
    def build(self):
        #javaclass = autoclass('com.test.JavaClass')
        #print(javaclass().show())

        self.menu = MenuLayout() #MenuManager()
        return self.menu

    def on_start(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    MotaApp().run()
