# -*- coding: utf-8 -*-
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.lang import Builder
with open('challenge.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())

class Challenge(FloatLayout):
    pass

class MenuChallenge(GridLayout):
    def __init__(self, **kwargs):
        super(MenuChallenge, self).__init__(**kwargs)


if __name__ == '__main__':
    from kivy.app import App
    import main

    class TestApp(App):
        def build(self):
            mc = MenuChallenge()
            #mc.add_widget(Challenge())
            return mc

    TestApp().run()
