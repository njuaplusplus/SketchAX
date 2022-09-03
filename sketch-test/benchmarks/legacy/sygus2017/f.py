#!/usr/bin/env python
# coding=utf-8
import shutil
import os

if __name__ == '__main__':
    servers = ['fg_max%d' % i for i in range(4,16)]
    for sname in servers:
        shutil.copyfile('./fg_max3/test_config.py', os.path.join(sname, 'test_config.py'))

