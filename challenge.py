# -*- coding: utf-8 -*-
from zxlib.pageview import PageView

from kivy.lang import Builder
with open('challenge.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())

class ChallengeMenu(PageView):
    pass

if __name__ == '__main__':
    from kivy.app import App
    import main

    class TestApp(App):
        def build(self):
            mc = ChallengeMenu()
            for i in range(30):
                mc.data.append({'level': int(i / 8), 'mlevel': 3, 'achieve': 3 * i, 'goal': 100})
            #mc.add_widget(Challenge())
            return mc

    TestApp().run()
