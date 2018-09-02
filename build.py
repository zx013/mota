# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 18:19:24 2018

@author: zx013
"""

import os
import sys
import platform

#获取在wsl中的路径
def wsl_path(path):
    path = path.replace(os.path.sep, '/')
    drive, path = path.split('/', 1)
    path = '/mnt/{}/{}'.format(drive.replace(':', '').lower(), path)
    return path

def build(path='.'):
    path = os.getcwd()
    if os.path.isfile(os.path.join(path, 'main.py')):
        path = wsl_path(path)
        cmd = "powershell debian run 'source /root/.bashrc; cd {}; rm -rf /root/.buildozer/android/platform/build/dists/zx013/build; cp -rf /root/buildozer.spec .; buildozer android release'".format(path)
        print(cmd)
        os.system(cmd)
    else:
        print('Can not find main.py in {}, please check it.'.format(path))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            os.chdir(path)
        else:
            print('Path {} is not exist, use base dir.'.format(path))
    else:
        path = '.'
    build(path)