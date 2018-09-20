# -*- coding: utf-8 -*-
"""
@author: zx013
"""

#打包apk使用
build_apk = True
if build_apk:
    import sys
    import platform
    if platform.system().lower() == 'windows':
        from build import build
        build()
        sys.exit(0)


from kivy.app import App
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
    mota = MotaApp()
    mota.run()
    #mota.stop()
