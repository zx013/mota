# -*- coding: utf-8 -*-
"""
@author: zx013
"""
import os
from kivy.config import Config

#需要放到单独的模块
#是否展示伤害数字
#是否开启背景音乐
#是否开启音效
#难度
#是否开启楼层飞行器
#默认移动动画间隔
#默认开门动画间隔
#默认怪物动画间隔

#全局设置
class Setting:
    #标题
    title = '无尽的魔塔'

    #标题宽度
    title_width = 28

    #标题所在的圆的半径，越小越突出
    title_radius = 28

    #版本号
    version = '2.0'

    #图标路径
    icon_path = os.path.join('data', 'icon.ico')

    #字体路径
    font_path = os.path.join('data', 'font.ttf')

    #每个单元多少层
    base = 2

    #迷宫的大小，最小为5，最大不限，正常11，太大影响性能，最好为奇数
    size = 4

    #每个点的大小（像素）
    pos_size = 32

    #行数，从左上开始往下
    rows = size

    #显示的行数，包括外面一圈墙
    row_show = rows + 2

    #列数，从左上开始往右
    cols = size

    #显示的列数，包括外面一圈墙
    col_show = cols + 2

    #蒙特卡洛模拟的次数
    montecarlo = 100

    #是否显示怪物血量
    show_health = False

    #是否显示怪物攻击
    show_attack = False

    #是否显示怪物防御
    show_defence = False

    #是否在怪物上显示对应伤害
    show_damage = True


#默认字体没有生效，很奇怪
Config.set('kivy', 'window_icon', Setting.icon_path)
Config.set('graphics', 'default_font', Setting.font_path)
Config.set('graphics', 'height', (Setting.rows + 2) * Setting.pos_size)
Config.set('graphics', 'width', (Setting.cols + 2) * Setting.pos_size)
Config.set('graphics', 'resizable', 0)


#注意，出现random的属性，每次获取时值将不同
#迷宫设置
class MazeSetting:
    #行
    rows = Setting.rows
    #列
    cols = Setting.cols
    #保存的目录
    save_dir = 'save'
    #保存的文件后缀
    save_ext = 'save'

    @staticmethod
    def save_file(num):
        return '{save_dir}/{num}.{save_ext}'.format(save_dir=MazeSetting.save_dir, num=num, save_ext=MazeSetting.save_ext)

    #保存的层数，10时占用20M左右内存，100时占用50M左右内存
    save_floor = Setting.base
    #每几层一个单元
    base_floor = Setting.base

    #每个宝石增加的属性值（总属性百分比）
    attribute_value = 0.01

    #第一个怪物造成的最低伤害
    damage_min = 200

    #第一个怪物造成的最高伤害
    damage_max = 1000

    #精英怪物造成的最低伤害
    elite_min = 1000

    #精英怪物造成的最高伤害
    elite_max = 2000

    #boss造成的最低伤害
    boss_min = 2000

    #boss造成的最高伤害
    boss_max = 5000

    #某一类怪物不超过damage_total_num的数量低于damage_total_min
    damage_total_num = 3

    damage_total_min = 100

    #蒙特卡洛模拟的次数，该值越大，越接近最优解，同时增加运行时间，10000时基本为最优解
    montecarlo_time = Setting.montecarlo

    #使用近似最优解通关后至少剩余的额外的血量，可以用该参数调节难度
    extra_potion = 100


#迷宫的基础属性
class MazeBase:
    class Type:
        class Static:
            init = 11
            ground = 12
            wall = 13
            shop = 14
            stair = 15
            door = 16

        class Active:
            monster = 21
            rpc = 22

        class Item:
            key = 31
            potion = 32

            attack = 33
            defence = 34

            holy = 35

        unknown = 99

    class Value:
        class Special:
            boss = 1
            trigger = 2
            item = 3
            shop = 4
            branch = 5

        class Wall:
            static = 1
            dynamic = 2

        class Shop:
            gold = 1
            experience = 2

        class Stair:
            up = 1
            down = 2

        #key和door的颜色
        class Color:
            none = 0
            yellow = 1
            blue = 2
            red = 3
            green = 4

            prison = 5
            trap = 6

            total = (yellow, blue, red, green)

        #起始时对应攻防平均属性的1%
        class Gem:
            small = 1
            big = 3
            large = 10

            total = (small, big, large)

        #起始时对应攻防平均属性的1%，设置太低会导致空间不够的情况，按初始默认的配置，总需求在30000左右
        class Potion:
            red = 50
            blue = 200
            yellow = 600
            green = 1200

            total = (red, blue, yellow, green)

        class Rpc:
            wisdom = 1
            trader = 2
            thief = 3
            fairy = 4

    class NodeType:
        none = 0
        area_normal = 1
        area_corner = 2
        Area = (area_normal, area_corner)
        road_normal = 3
        road_corner = 4
        Road = (road_normal, road_corner)
