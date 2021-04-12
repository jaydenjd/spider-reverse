# -*- coding:utf8 -*-
# @Time : 2020-03-22 18:46
# @Author : wu


import base64
import binascii
import json
import random
import re
from urllib import parse
import rsa
import time

import requests


class WeiboLogin(object):

    def __init__(self, username, password):
        self.session = requests.session()
        self.username = username
        self.password = password
        self.prelogin_url = 'https://login.sina.com.cn/sso/prelogin.php'
        self.login_url = 'https://login.sina.com.cn/sso/login.php'
        self.weibo_url = 'https://weibo.com/'
        self.su = self.encrypt_user(username=self.username)

    def prelogin(self):
        """预登陆接口"""
        params = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': self.su,
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
            '_': str(int(time.time())),
        }
        prelogin_resp = self.session.get(self.prelogin_url, params=params)
        res = re.findall(r'sinaSSOController.preloginCallBack\((.*?)\)', prelogin_resp.text)[0]
        return json.loads(res)

    def login(self):
        """登陆接口"""
        pre_res = self.prelogin()
        servertime = str(int(time.time()))
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': '',
            'vsnf': '1',
            'su': self.su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': pre_res['nonce'],
            'pwencode': 'rsa2',  # 默认加密方式
            'rsakv': pre_res['rsakv'],
            'sp': self.encrypt_pwd(self.password, servertime, pre_res['nonce'], pre_res['pubkey']),
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            # 这个算法其实是不正确的，但似乎对它的校验不大，所以我这里选择了简单的随机生成。当然也可以选择翻译原来的加密方法
            'prelt': random.randint(1, 100),
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
        }
        # 登陆
        resp = self.session.post(self.login_url, data=data)
        # 获取正确的网站编码，这是 requests 自带的设置
        resp.encoding = resp.apparent_encoding

        location = re.findall(r'replace\("(.*?)"\);', resp.text)[0]
        # 加载 replace 中的 url 以替换当前页面
        resp = self.session.get(location)

        location = re.findall(r'replace\(\'(.*?)\'\);', resp.text)[0]
        #  加载 replace 中的 url 以替换当前页面
        self.session.get(location)
        # 如果已经登陆成功的状态下，访问官网链接可自动重定向到个人主页
        resp = self.session.get(self.weibo_url)
        print(resp.text)  # 如果打印出来的是自己的个人主页信息，便证明是成功了
        print(resp.url)  # 个人主页 url

    @staticmethod
    def encrypt_user(username: str) -> str:
        """
        加密用户名
        :param username: 用户名
        """
        # 转成 url 编码格式
        _username = parse.quote(username)
        # Python3中的base64参数必须是字节类型
        u_name = base64.b64encode(_username.encode())
        return u_name

    @staticmethod
    def encrypt_pwd(password, servertime, nonce, pubkey) -> str:
        """
        加密密码，rsa 加密
        :param password: 密码
        :param servertime: 时间戳
        :param nonce:
        :param pubkey: 公钥
        """
        message = (str(servertime) + "\t" + str(nonce) + "\n" + str(password)).encode("utf-8")
        # 生成公钥
        public_key = rsa.PublicKey(int(pubkey, 16), int("10001", 16))
        # 加密信息
        pwd_ = rsa.encrypt(message, public_key)
        # 转16进制
        pwd = binascii.hexlify(pwd_).decode()
        return pwd


if __name__ == '__main__':
    w = WeiboLogin(username='xxx', password='xxx')
    w.login()
