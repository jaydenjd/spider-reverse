# -*- coding: utf-8 -*-
# @Time   : 2021/4/18 上午10:26
# @Author : wu

""""
淘宝商品 id 重定向
"""
import logging
import requests
import re
from urllib.parse import unquote
from requests.adapters import HTTPAdapter


def get_redirect_url(jump_url):
    headers = {
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "sec-fetch-mode": "navigate",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "sec-fetch-site": "none",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5",
    }
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))  # 重试3次
    s.mount('https://', HTTPAdapter(max_retries=3))
    res = ''
    try:
        res = s.get(url=jump_url, headers=headers, timeout=3).text
    except requests.exceptions.RequestException as e:
        logging.error('淘宝goods_id重试失败', e)
    # 提取原始链接请求响应体中要302重定向的链接
    if re.findall("real_jump_address = \'(.*)\'", res):
        new_url = re.findall("real_jump_address = \'(.*)\'", res)[0].replace('amp;', '')
        # 必须加上referer
        headers['referer'] = jump_url
        # 这里需要禁止重定向
        resp = requests.get(url=new_url, headers=headers, allow_redirects=False)
        redirects_url = resp.headers.get('location')
        redirects_url = unquote(unquote(redirects_url))
        goods_id = re.findall(r".*?id=(.*?)&", redirects_url)[0]
        print(goods_id)
        return goods_id


if __name__ == '__main__':
    # 原始链接
    jump_url = 'https://s.click.taobao.com/t?e=m=2&s=4Muzg0OjQ09w4vFB6t2Z2ueEDrYVVa64XoO8tOebS+dRAdhuF14FMWXNZqRuQ0OjMMgx22UI05YM46janIRl4drSDOxWN+VQrndyhjdyO+Dipm9doYzKtZ8yQnCH6WE98MzIj0VoIzKo5fvksL1XH4we6/tGg2/RSyiL934V8t7C3Lq4DblQ1v7nyHmkoZi71hjz2dNwkcSmj7sfEnWB0UDaBV2nSoxxeP3f80DzCSUmK7JFfPvPXxB2I6vSoRWtp0+xhhDHMH/GDF1NzTQoPw==&union_lens=lensId:0bb0d4fb_0be6_16c40e868c3_6bbd&materialId=qnnsDxsrQlc&materialType=1&ext=default&linkType=1&visitorId=2JQXn97LRG0&authorId=Vz06RbDE92s&carrierId=OTV1ev4a2_8&carrierType=2&itemId=f3sI6c7ZLFE&sourceType=2&clientVersion=6.7.1.10332&clientId=2'
    redirect_url = get_redirect_url(jump_url)
