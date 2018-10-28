# -*- coding: utf-8 -*-
"""
@author: zx013
"""
import random

#限制随机，防止S/L，S/L时需存取__staticrandom
__random = random._inst.random
__staticrandom = []
def staticrandom(number=0):
    for i in range(number):
        __staticrandom.append(__random())
    def new_random():
        r = __random()
        __staticrandom.append(r)
        return __staticrandom.pop(0)
    random.random = random._inst.random = new_random


#异常时返回默认值
def except_default(default=None):
    def run_func(func):
        def run(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print(func.__name__, ex)
                return default
        run.__name__ = func.__name__
        return run
    return run_func


#死循环的处理
class LoopException(Exception):
    retry = 1000

def loop_retry(func):
    def run(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except LoopException:
                print('retry :', func.__name__)
    run.__name__ = func.__name__
    return run


class Tools:
    #从目录中选出一个值
    @staticmethod
    def dict_choice(dictionary):
        total = sum(dictionary.values())
        if total < 1:
            return
        rand = random.randint(1, total)
        for key, val in dictionary.items():
            rand -= val
            if rand <= 0:
                return key

    #迭代当前值和上一个值
    @staticmethod
    def iter_previous(iterator):
        previous = None
        for number, element in enumerate(iterator):
            if number > 0:
                yield previous, element
            previous = element

    #计算字符串长度
    @staticmethod
    def text_length(text):
        dp = {':': 0.25, ' ': 0.25, '1': 0.25}
        if text:
            return max([sum([0.2 if s in [':', ' ', '1'] else (0.5 * len(s.encode('gbk'))) for s in line]) for line in text.split('\n')])
        else:
            return 0
