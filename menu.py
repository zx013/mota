#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zx013
"""
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder

from setting import Setting, MazeBase
from cache import Config
from g import gmota, gmaze, ginfo, gstatusbar, gprogress, glayout

from random import random

with open('menu.kv', 'r', encoding='utf-8') as fp:
    Builder.load_string(fp.read())

class MenuLabel(ToggleButtonBehavior, Label): pass
class MenuImage(ToggleButtonBehavior, FloatLayout):
    def use_item(self):
        herostate = gmaze.herostate
        used = True
        for key, data in self.attribute.items():
            if key == 'key':
                for k, v in data.items():
                    if herostate.key[k] + v < 0:
                        used = False
            else:
                if getattr(herostate, key) + data < 0:
                    used = False
        if used:
            for key, data in self.attribute.items():
                if key == 'key':
                    for k, v in data.items():
                        herostate.key[k] += v
                else:
                    setattr(herostate, key, getattr(herostate, key) + data)
            self.number -= 1
            if self.number <= 0:
                self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if not touch.is_double_tap:
            for image in self.parent.children:
                image.selected = False
            self.selected = True

            key = self.name
            name = Config.config[key].get('name', '未知')
            help = Config.config[key].get('help', '未知')
            text = ':  '.join((name, help))
            gstatusbar.update(text)
        else:
            opened = self.opened
            for image in self.parent.children:
                image.opened = False
                image.exit += 1
            if not opened:
                self.enter += 1
                if self.used:
                    self.use_item()
        return True

class MenuWelcomeLabel(MenuLabel):
    def __init__(self, **kwargs):
        super(MenuWelcomeLabel, self).__init__(**kwargs)
        self.pos = (Setting.row_size, 0)
        self.text = Setting.status_text

        offset = Setting.row_size + self.texture_size[0]
        anim = Animation(x=Setting.row_size) + Animation(x=-offset, duration=offset / Setting.status_speed) + Animation(x=Setting.row_size, duration=0)
        anim.repeat = True
        anim.start(self)


class MenuStatusLabel(MenuLabel):
    def __init__(self, **kwargs):
        super(MenuStatusLabel, self).__init__(**kwargs)
        self.anim = None

        gstatusbar.instance = self

    def update(self, text):
        self.pos = (0, 0)
        self.pos_hint = {}
        self.text = text
        self.color = (0.5 + random() / 2, 0.5 + random() / 2, 0.5 + random() / 2, 1)
        self.texture_update()
        offset = self.texture_size[0] - Setting.col_size + Setting.pos_real
        if offset < 0:
            offset = 0
        if self.anim:
            self.anim.cancel(self)
        self.anim = Animation(x=0) + Animation(x=-offset, duration=offset / Setting.status_speed) + Animation(x=-offset) + Animation(x=0, duration=0)
        self.anim.repeat = True
        self.anim.start(self)


class MenuShop(FloatLayout):
    window = None

    def update(self):
        self.add('gem-attack-small', 10, 20)
        self.add('gem-attack-big', 3, 50)
        self.add('gem-defence-small', 8, 15)
        self.add('gem-defence-big', 5, 40)
        self.add('sword-silver', 1, 150)
        self.add('potion-red', 5, 10)
        self.add('key-yellow', 3, 20)

    def add(self, name, number, price):
        image = MenuImage()
        image.name = name
        image.number = number
        image.price = price
        image.used = True
        image.attribute = MazeBase.get_attribute(name)
        image.attribute['gold'] = -price
        self.board.add_widget(image)

    def on_touch_up(self, touch):
        return True

    def open(self):
        if not self.window:
            self.window = self.parent
        self.window.add_widget(self)

    def close(self):
        if not self.window:
            self.window = self.parent
            self.parent.shop = self
        self.window.remove_widget(self)



class MenuTaskBoard(RecycleView):
    def insert(self, text):
        pass

    def delete(self, text):
        pass


class MenuInfoBoard(RecycleView):
    def __init__(self, **kwargs):
        super(MenuInfoBoard, self).__init__(**kwargs)
        ginfo.instance = self

    def update(self, text, type='info'):
        head_pool = {
            'hint': '提示',
            'warn': '警告',
            'secret': '传闻'
        }
        head = head_pool.get(type)
        if head:
            text = '[{}] {}'.format(head, text)
        default_color = (1, 1, 1, 1)
        color_pool = {
            'info': (1, 1, 1, 1),
            'hint': (1, 1, 0, 1),
            'warn': (1, 0, 0, 1),
            'secret': (1, 0, 1, 1)
        }
        color = color_pool.get(type, default_color)
        self.data.append({'text': text, 'color': color})
        self.scroll_y = 0


import time
class MenuInit:
    def __init__(self, **kwargs):
        tm1 = time.time()
        super(MenuInit, self).__init__(**kwargs)
        tm2 = time.time()
        print('init', self.__class__.__name__, tm2 - tm1)


class MenuScreen(MenuInit, Screen): pass

class MenuManagerMain(MenuScreen): pass
class MenuManagerStart(MenuScreen): pass
class MenuManagerMota(MenuScreen): pass
class MenuManagerSettingBase(MenuScreen): pass
class MenuManagerSettingOperate(MenuScreen): pass
class MenuManagerSettingSound(MenuScreen): pass
class MenuManagerSettingOther(MenuScreen): pass
class MenuManagerMonsterManual(MenuScreen): pass


class MenuScreenManager(MenuInit, ScreenManager): pass

class MenuHero(MenuScreenManager): pass #英雄属性
class MenuItem(MenuScreenManager): pass #物品栏
class MenuManager(MenuScreenManager): pass #主界面
class MenuStatus(MenuScreenManager): pass #状态栏
class MenuStory(MenuScreenManager): pass #任务栏
class MenuMessage(MenuScreenManager): pass #消息栏
class MenuProgress(MenuScreenManager): #进度条
    def __init__(self, **kwargs):
        super(MenuProgress, self).__init__(**kwargs)
        gprogress.instance = self

    def init(self):
        self.ready = False
        self.opacity = 1

    def finish(self):
        self.ready = True
        Clock.schedule_once(self.fade, 0.1)

    def fade(self, dt):
        self.opacity -= 0.05
        if self.opacity > 0:
            Clock.schedule_once(self.fade, 0.1)
        else:
            self.value = -1
            self.opacity = 0


class MenuLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MenuLayout, self).__init__(**kwargs)
        glayout.instance = self

        self.height = (1 + Setting.status_size) * Setting.col_size
        self.init_menu()
        self.init_manager()

    def init_menu(self):
        hero = MenuHero(pos=(0, self.height / 2), size=(Setting.offset, self.height / 2))
        self.add_widget(hero)
        self.hero = hero

        item = MenuItem(pos=(0, 0), size=(Setting.offset, self.height / 2))
        self.add_widget(item)
        self.item = item

        manager = MenuManager(pos=(Setting.offset, Setting.status_size * Setting.col_size), size=(Setting.row_size, Setting.col_size))
        self.add_widget(manager)
        self.manager = manager

        status = MenuStatus(pos=(Setting.offset, 0), size=(Setting.row_size, Setting.status_size * Setting.col_size))
        self.add_widget(status)
        self.status = status

        story = MenuStory(pos=(Setting.offset + Setting.row_size, self.height / 2), size=(Setting.offset, self.height / 2))
        self.add_widget(story)
        self.story = story

        message = MenuMessage(pos=(Setting.offset + Setting.row_size, 0), size=(Setting.offset, self.height / 2))
        self.add_widget(message)
        self.message = message

        progress = MenuProgress(pos=(Setting.offset, Setting.status_size * Setting.col_size), size=(Setting.row_size, Setting.col_size))
        self.add_widget(progress)
        self.progress = progress

    def init_manager(self):
        self.manager.add_widget(MenuManagerMain())
        self.manager.add_widget(MenuManagerStart())
        self.manager.add_widget(MenuManagerMota())
        self.manager.add_widget(MenuManagerSettingBase())
        self.manager.add_widget(MenuManagerSettingOperate())
        self.manager.add_widget(MenuManagerSettingSound())
        self.manager.add_widget(MenuManagerSettingOther())
        self.manager.add_widget(MenuManagerMonsterManual())


#三行分别为7, 10, 10个中文字符
class MenuDialog(FloatLayout):
    l = 1.5 * Setting.multiple #线条宽度
    w = 0.4 * Setting.row_size + 2 * l #宽度
    h = 0.25 * Setting.col_size + 2 * l #高度

    dialog = []
    person = {}
    window = None

    def on_touch_up(self, touch):
        super(MenuDialog, self).on_touch_down(touch)

        if self.page < len(self.pages) - 1:
            self.page += 1
            self.show()
        elif not self.update():
            self.close()
        return True

    def open(self):
        if not self.window:
            self.window = self.parent
        self.window.add_widget(self)

    def close(self):
        if not self.window:
            self.window = self.parent
            self.parent.dialog = self
        self.window.remove_widget(self)

    def start(self, pos1, pos2, scene):
        self.dialog = list(scene.dialog)
        self.person = {1: (pos1[0], pos1[1] - 3 * (pos2[1] - pos1[1]), pos1[2] - 3 * (pos2[2] - pos1[2])), 2: pos2}
        self.update()

    def update(self):
        if len(self.dialog) == 0:
            return False

        posd, text = self.dialog.pop(0)
        pos = self.person[posd]
        if posd == 1:
            self.role_label.text = '勇 者'
            self.role_image.name = gmota.hero.name_show #texture = Texture.next(self.name)
        else:
            key = gmota.get_key(pos)
            self.role_label.text = ' '.join(Config.config[key].get('name', '未知'))
            self.role_image.name = key
        z, x, y = pos
        self.idx = (y - Setting.size / 2) - 0.75
        self.idy = -(x - Setting.size / 2) + 0.75
        self.text = text
        self.page = 0
        self.split()
        self.show()
        return True

    def split(self):
        text = self.text
        pages = []

        while text:
            lines = []
            for w in (14, 20, 20):
                line = ''
                length = 0
                while len(text) > 1:
                    ps = text[0]
                    ns = text[1]
                    pslen = len(ps.encode('gbk'))
                    nslen = len(ns.encode('gbk'))
                    if length + pslen <= w and length + pslen + nslen > w and ns in ('，', '。', '？', '！', '：', '、', '；'):
                        break
                    if length <= w and length + pslen > w:
                        break
                    line += ps
                    length += pslen
                    text = text[1:]
                else:
                    line += text
                    length += sum([len(s.encode('gbk')) for s in text])
                    text = ''
                line += 2 * (w - length) * ' '
                lines.append(line)
            pages.append(lines)

        if not pages:
            pages = [['', '', '']]
        self.pages = pages

    def show(self):
        self.page_prev.color = self.page_prev.disabled_color if self.page_prev.disabled else self.page_prev.default_color
        self.page_next.color = self.page_next.disabled_color if self.page_next.disabled else self.page_next.default_color
        self.page_enter.color = self.page_enter.disabled_color if self.page_enter.disabled else self.page_enter.default_color
        self.page_exit.color = self.page_exit.default_color
