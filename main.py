# -*- coding: utf-8 -*-
"""
@author: zx013
"""

'''
#打包apk使用，目前可以打包，但运行时会卡住
import sys
import platform
if platform.system().lower() == 'windows':
    from build import build
    build()
    sys.exit(0)
'''

'''
扩展方法
在对应目录下新建文件夹，添加图片和info文件，格式参照之前目录的格式
目前怪物类型可无限扩展

功能点
商店功能（每一段默认加攻或加防），加入商店对蒙特卡洛求解最优路径影响很大
对话功能（剧情任务等）
其他技能
特殊道具（破墙等）
机关门
岩浆（不是很好加）
密室

优化点
长条形区域有时需要分割一下，不然显得太空旷
长条区域可以放置多个怪物

目前剩余的问题
开始菜单
配置页面
怪物手册
楼层跳跃
存档功能
观看广告可以增加生命
增加捐赠二维码

偶尔会出现空格子的情况，出现过两回，会显示上一层的东西，但走过去没有影响
大小很小的时候，容易出现没有上行楼梯的情况，应不论何种情况都设置楼梯
钥匙有时候会多出若干把，应该在计算钥匙分配时加入已有的钥匙
蒙特卡洛模拟结果似乎不大对，需要验证一下
圣水应该显示大小
击败boss应放置些物品
后台计算后续的楼层
'''

#import jnius_config
#jnius_config.add_classpath('jars/javaclass.jar')
#from jnius import autoclass

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.clock import Clock

from setting import Setting, MazeBase
from cache import Config, Texture, Music
from maze import Maze
from hero import Opacity, Hero
from menu import Menu
from state import State


class Layer(GridLayout):
    def __init__(self, **kwargs):
        super(Layer, self).__init__(rows=Setting.row_show, cols=Setting.col_show, size=(Texture.size * Setting.row_show, Texture.size * Setting.col_show), size_hint=(None, None), **kwargs)
        self.image = [[None for j in range(Setting.col_show)] for i in range(Setting.row_show)]
        self.texture = None #默认的texture

    def add(self, i, j, texture=None):
        self.texture = texture
        image = Image(size=(Texture.size, Texture.size), size_hint=(None, None))
        image.texture = texture
        self.image[i][j] = image
        self.add_widget(image)
        return image


class Map(FocusBehavior, FloatLayout):
    row = Setting.row_show
    col = Setting.col_show

    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)

        self.maze = Maze()
        self.maze.update()

        self.menu = Menu() #菜单
        self.menu.opacity = 0
        self.state = State(self.maze.herostate) #状态显示
        self.state.easy()
        #切换楼层时显示目标楼层数，3和40是经验数据
        self.floorlabel= Label(pos=(0, Setting.size * 3), font_name=Setting.font_path, font_size=str(Setting.size * 40)) #楼层变换时显示层数
        self.floorlabel.canvas.opacity = 0

        self.front = Layer() #英雄移动
        self.middle = Layer() #物品和怪物
        self.back = Layer() #背景，全部用地面填充

        self.add_widget(self.back)
        self.add_widget(self.middle)
        self.add_widget(self.front)
        self.add_widget(self.floorlabel)
        self.add_widget(self.state)
        self.add_widget(self.menu)
        for i in range(Setting.row_show):
            for j in range(Setting.col_show):
                self.front.add(i, j, Texture.next('empty'))
                self.middle.add(i, j)
                self.back.add(i, j, Texture.next('ground'))

        self.hero = Hero(self.maze, self.state)
        Clock.schedule_interval(self.show, Config.step)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key_map = {'w': 'up', 'a': 'left', 's': 'down', 'd': 'right'}
        key = keycode[1]
        if key in key_map:
            key = key_map[key]
        if key in ('up', 'down', 'left', 'right'):
            self.move(key)
        elif key == 'q':
            self.floorlabel.text = str(self.hero.floor_up)
            self.hero.stair = MazeBase.Value.Stair.up
            Music.play('floor')
        elif key == 'e':
            self.floorlabel.text = str(self.hero.floor_down)
            self.hero.stair = MazeBase.Value.Stair.down
            Music.play('floor')
        elif key == 'p': #测试作弊
            self.maze.herostate.health += 1000
        return True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            x = self.row - int(touch.y / Texture.size) - 1
            y = int(touch.x / Texture.size)
            pos = (self.hero.floor, x, y)
            self.hero.move_list = self.maze.find_path(self.hero.pos, pos)
            return True
        return False


    def ismove(self, pos):
        if pos in self.hero.action:
            return False
        pos_type = self.maze.get_type(pos)
        pos_value = self.maze.get_value(pos)
        herobase = self.maze.herobase
        herostate = self.maze.herostate

        if pos_type == MazeBase.Type.Static.wall:
            return False
        elif pos_type == MazeBase.Type.Static.stair:
            if pos_value == MazeBase.Value.Stair.down:
                self.floorlabel.text = str(self.hero.floor_down)
            elif pos_value == MazeBase.Value.Stair.up:
                self.floorlabel.text = str(self.hero.floor_up)
            self.hero.stair = pos_value
            Music.play('floor')
            return True
        elif pos_type == MazeBase.Type.Static.door:
            if herostate.key[pos_value] == 0:
                return False
            herostate.key[pos_value] -= 1
            self.hero.action.add(pos)
            Music.play('opendoor')
            return False
        elif pos_type == MazeBase.Type.Item.key:
            herostate.key[pos_value] += 1
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.attack:
            herostate.attack += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.defence:
            herostate.defence += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.potion:
            herostate.health += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Item.holy:
            herostate.health += herobase.base * pos_value
            Music.play('getitem')
        elif pos_type == MazeBase.Type.Active.monster:
            damage = self.maze.get_damage(herostate.attack, herostate.defence, pos_value)
            if herostate.health <= damage:
                return False
            herostate.health -= damage
            Music.play('blood')
            if pos_value[0] == 'boss':
                self.maze.kill_boss(pos)
        elif pos_type == MazeBase.Type.Active.rpc:
            return False

        self.maze.set_type(pos, MazeBase.Type.Static.ground)
        self.maze.set_value(pos, 0)
        return True

    def move(self, key):
        pos = self.hero.move_pos(key)
        if self.ismove(pos):
            self.hero.move(key)
        else:
            self.hero.move_list = []
        Config.reset(self.hero.name)
        Texture.reset(self.hero.name)
        self.show_hero()


    def get_key(self, pos, pos_style='static'):
        floor, x, y = pos
        pos_type = self.maze.get_type(pos)
        pos_value = self.maze.get_value(pos)

        if pos_type == MazeBase.Type.Static.init:
            pos_key = 'ground'
        elif pos_type == MazeBase.Type.Static.ground:
            pos_key = 'ground'
        elif pos_type == MazeBase.Type.Static.wall:
            if pos_value == MazeBase.Value.Wall.static:
                pos_key = self.hero.wall
            elif pos_value == MazeBase.Value.Wall.dynamic:
                pos_key = self.hero.wall_dynamic
                pos_style = 'dynamic'
        elif pos_type == MazeBase.Type.Static.stair:
            if pos_value == MazeBase.Value.Stair.down:
                pos_key = 'stair-down'
            elif pos_value == MazeBase.Value.Stair.up:
                pos_key = 'stair-up'
        elif pos_type == MazeBase.Type.Static.door:
            if pos_value == MazeBase.Value.Color.yellow:
                pos_key = 'door-yellow'
            elif pos_value == MazeBase.Value.Color.blue:
                pos_key = 'door-blue'
            elif pos_value == MazeBase.Value.Color.red:
                pos_key = 'door-red'
            elif pos_value == MazeBase.Value.Color.green:
                pos_key = 'door-green'
        elif pos_type == MazeBase.Type.Item.key:
            if pos_value == MazeBase.Value.Color.yellow:
                pos_key = 'key-yellow'
            elif pos_value == MazeBase.Value.Color.blue:
                pos_key = 'key-blue'
            elif pos_value == MazeBase.Value.Color.red:
                pos_key = 'key-red'
            elif pos_value == MazeBase.Value.Color.green:
                pos_key = 'key-green'
        elif pos_type == MazeBase.Type.Item.attack:
            if pos_value == MazeBase.Value.Gem.small:
                pos_key = 'gem-attack-small'
            elif pos_value == MazeBase.Value.Gem.big:
                pos_key = 'gem-attack-big'
            elif pos_value == MazeBase.Value.Gem.large:
                pos_key = self.hero.weapon_attack
        elif pos_type == MazeBase.Type.Item.defence:
            if pos_value == MazeBase.Value.Gem.small:
                pos_key = 'gem-defence-small'
            elif pos_value == MazeBase.Value.Gem.big:
                pos_key = 'gem-defence-big'
            elif pos_value == MazeBase.Value.Gem.large:
                pos_key = self.hero.weapon_defence
        elif pos_type == MazeBase.Type.Item.potion:
            if pos_value == MazeBase.Value.Potion.red:
                pos_key = 'potion-red'
            elif pos_value == MazeBase.Value.Potion.blue:
                pos_key = 'potion-blue'
            elif pos_value == MazeBase.Value.Potion.yellow:
                pos_key = 'potion-yellow'
            elif pos_value == MazeBase.Value.Potion.green:
                pos_key = 'potion-green'
        elif pos_type == MazeBase.Type.Item.holy:
            pos_key = 'holy'
        elif pos_type == MazeBase.Type.Active.monster:
            pos_key = '-'.join(pos_value)
            pos_style = 'dynamic'
        elif pos_type == MazeBase.Type.Active.rpc:
            if pos_value == MazeBase.Value.Rpc.wisdom:
                pos_key = 'npc-wisdom'
            elif pos_value == MazeBase.Value.Rpc.trader:
                pos_key = 'npc-trader'
            elif pos_value == MazeBase.Value.Rpc.thief:
                pos_key = 'npc-thief'
            elif pos_value == MazeBase.Value.Rpc.fairy:
                pos_key = 'npc-fairy'
            pos_style = 'dynamic'

        return pos_key, pos_style

    #人物移动
    def show_hero(self):
        _, x, y = self.hero.old_pos
        image = self.front.image[x][y]
        image.texture = Texture.next('empty')

        _, x, y = self.hero.pos
        image = self.front.image[x][y]
        image.texture = Texture.next(self.hero.name, 'action', False)

        pos_key, pos_style = self.get_key(self.hero.pos)
        image = self.middle.image[x][y]
        image.texture = Texture.next(pos_key, pos_style)

    #点击移动
    def show_move(self, dt):
        if not self.hero.move_list:
            return None

        if Config.active('hero-click', dt):
            key = self.hero.move_list.pop(0)
            self.move(key)

    #上下楼切换
    def show_stair(self, dt):
        if not self.hero.stair:
            return None
        state = self.hero.opacity.next(dt)
        if state == Opacity.Turn:
            if self.hero.stair == MazeBase.Value.Stair.down:
                self.hero.floor -= 1
            elif self.hero.stair == MazeBase.Value.Stair.up:
                self.hero.floor += 1
        elif state == Opacity.End:
            self.hero.stair = None

    def show_monster(self):
        floor = self.hero.floor
        health = self.maze.herostate.health
        attack = self.maze.herostate.attack
        defence = self.maze.herostate.defence
        for i in range(self.row):
            for j in range(self.col):
                pos = (floor, i, j)
                pos_type = self.maze.get_type(pos)
                pos_value = self.maze.get_value(pos)
                
                
                if pos_type == MazeBase.Type.Active.monster:
                    damage = self.maze.get_damage(attack, defence, pos_value)
                    info = self.maze.get_monster(pos_value)
                else:
                    damage = -1
                    info = {'health': '', 'attack': '', 'defence': ''}

                if Setting.show_health:
                    self.state.set_health(i, j, info['health'])
                if Setting.show_attack:
                    self.state.set_attack(i, j, info['attack'])
                if Setting.show_defence:
                    self.state.set_defence(i, j, info['defence'])
                if Setting.show_damage:
                    self.state.set_damage(i, j, health, damage)

    def show(self, dt):
        self.focus = True

        self.show_move(dt)
        self.show_stair(dt)

        opacity = self.hero.opacity.opacity
        self.floorlabel.canvas.opacity = 1 - opacity
        self.state.canvas.opacity = opacity
        self.front.canvas.opacity = opacity
        self.middle.canvas.opacity = opacity
        floor = self.hero.floor
        if Config.active(self.hero.name, dt):
            self.show_hero()
        self.show_monster()

        show = {}
        static_texture = {}
        action_texture = {}
        for i in range(self.row):
            for j in range(self.col):
                pos = (floor, i, j)
                if pos in self.hero.action:
                    pos_key, pos_style = self.get_key(pos, 'action')
                else:
                    pos_key, pos_style = self.get_key(pos)

                if pos_key not in show:
                    show[pos_key] = Config.active(pos_key, dt)
                if not show[pos_key]:
                    continue

                if pos in self.hero.action:
                    action_texture[pos_key] = Texture.next(pos_key, pos_style)
                    texture = action_texture[pos_key]
                else:
                    if pos_key not in static_texture:
                        static_texture[pos_key] = Texture.next(pos_key, pos_style)
                    texture = static_texture[pos_key]

                pos_image = self.middle.image[i][j]
                if texture:
                    pos_image.texture = texture
                else:
                    pos_image.texture = Texture.next('empty')
                    self.maze.set_type(pos, MazeBase.Type.Static.ground)
                    self.maze.set_value(pos, 0)
                    self.hero.action.remove(pos)


class Mota(App):
    def build(self):
        #javaclass = autoclass('com.test.JavaClass')
        #print(javaclass().show())

        self.map = Map()
        return self.map

    def on_start(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    mota = Mota()
    mota.run()
    mota.stop()
