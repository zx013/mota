# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 18:17:43 2018

@author: zx013
"""

import sys
import platform
if platform.system().lower() == 'windows':
    from build import build
    build()
    sys.exit(0)


from jnius import autoclass, cast
from kivy.app import App
from kivy.uix.button import Button


class Mota(App):
    def build(self):
        try:
            self.PythonActivity = autoclass('org.renpy.android.PythonActivity')
            self.CurrentActivity = cast('android.app.Activity', self.PythonActivity.mActivity)
            self.IndependentVideoManager = autoclass('com.pad.android_independent_video_sdk.IndependentVideoManager')
            #self.IndependentVideoListener = autoclass('com.pad.android_independent_video_sdk.IndependentVideoListener')
            #self.IndependentVideoAvailableState = autoclass('com.pad.android_independent_video_sdk.IndependentVideoAvailableState')
            javaclass = autoclass('com.test.JavaClass')
            text = 'Show Ads {}'.format(javaclass().show())
        except Exception as ex:
            text = str(ex)
        self.button = Button(text=text, on_press=self.show_ads)
        return self.button

    def on_start(self):
        try:
            self.IndependentVideoManager.newInstance().init(False)
            text = 'start success'
        except Exception as ex:
            text = str(ex)
        self.button.text = text
        #self.IndependentVideoManager.newInstance().updateUserID('zx')

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def show_ads(self, *args):
        try:
            #self.IndependentVideoManager.newInstance().addIndependentVideoListener(self.IndependentVideoListener)
            self.IndependentVideoManager.newInstance().checkVideoAvailable(self.CurrentActivity)
            text = 'show success'
        except Exception as ex:
            text = str(ex)
        self.button.text = text

if __name__ == '__main__':
    test = Mota()
    test.run()
    test.stop()