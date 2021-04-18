# -*- coding: utf-8 -*-
# @Time   : 2021/4/11 下午2:45
# @Author : wu
"""
pip install PyExecJS==1.5.1
"""
import os
import execjs

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_js_str(file):
    with open(file) as f:
        js_str = "".join(f.readlines())
    return js_str


def get_value(func, file, *args):
    ctx = execjs.compile(get_js_str(f"{file}"))
    value = ctx.call(func, *args)
    return value


def get_path(file):
    return os.path.dirname(os.path.abspath(file))