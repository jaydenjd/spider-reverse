# -*- coding: utf-8 -*-
# @Time   : 2021/4/11 下午2:47
# @Author : wu
"""
题目链接：http://match.yuanrenxue.com/match/2

相关教程：
https://syjun.vip/archives/279.html
https://www.bilibili.com/video/BV1yz4y1o7Ex?p=2
"""
import requests
from yuanrenxue import get_value
import time
from loguru import logger


def make_request(page=1):
    url = f'http://match.yuanrenxue.com/api/match/2?page={page}'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Host': 'match.yuanrenxue.com',
        'Pragma': 'no-cache',
        'Proxy-Connection': 'keep-alive',
        'User-Agent': 'yuanrenxue.project',
        'X-Requested-With': 'XMLHttpRequest',
    }
    m_cookie = get_value('m_cookie', '1-cookies', int(time.time()) * 1000)
    logger.info(m_cookie)
    cookies = m_cookie
    headers['cookie'] = cookies
    res = requests.get(url=url, headers=headers)
    logger.info(res.json())


if __name__ == '__main__':
    make_request(5)
