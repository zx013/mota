# -*- coding: utf-8 -*-
"""
@author: zx013
"""

'''
楼层跳跃
存档功能（地图存档，剧情存档）
'''
#打包apk使用
build_apk = True
if build_apk:
    import platform
    import sys
    if platform.system().lower() == 'windows':
        from build import build
        build()
        sys.exit()

from kivy.app import App
from setting import Setting #必须先加载setting，这样multiple就可以最先初始化
from menu import MenuManager


class MotaApp(App):
    def build(self):
        #javaclass = autoclass('com.test.JavaClass')
        #print(javaclass().show())

        self.menu = MenuManager()
        return self.menu

    def on_start(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    MotaApp().run()
