### 需求：需要从淘宝的商品链接中找出淘宝的商品id

#### 技术点：网页重定向

**接口**：https://s.click.taobao.com/t?e=m=2&s=7twJwd1K+OMcQipKwQzePOeEDrYVVa64XoO8tOebS+dRAdhuF14FMYCkwtphGcVmMMgx22UI05Z5N4lqm5BMvkDnixKzzoxED5cBZZV5l76t11g9a51vAItgwMO1YqTJ4q+RXokHRqt22bWK6RCIqBihUpzFc4OPQ7oq9ZQR1UM3xI+OKOZ3SJUVabPIj28BB0820MVrrOAHDFzVWjIuEhFf1GB1Osr/&union_lens=lensId:0b1aeb4a_0b79_16b68e3f62e_5d51&materialId=KdHZ5RGphF0&materialType=1&ext=default&linkType=1&visitorId=2JQXn97LRG0&authorId=5DLue222owc&carrierId=034iBf2YBog&carrierType=2&itemId=cuUXzsM5Wcg&sourceType=2&clientVersion=6.7.5.1078&clientId=1


**说明**：
淘宝的商品id不在链接中，在浏览器中打开该链接，会重定向到一个网页上，此时该网页的链接中包含商品的id。


**步骤**

* 抓包分析
    * 想看一个URL的请求的过程，最好的方式就是抓包。在这里，我用的是Charles抓包。结果如下：
    ![charles抓包淘宝请求过程](https://note.youdao.com/yws/api/personal/file/WEB4df81f98048c4aa925abd8f667983ee6?method=download&shareKey=6c0edc2ac3b8ede92afef648bf034a9f)

     可以发现，第一个是我们的原始url，第二个请求是一个302的重定向，第三个是最终重定向后的url。
    * 
    先看原始url的请求：
    ![click.taobao](https://note.youdao.com/yws/api/personal/file/WEBdfde506fa99dc975629e67c76e568b1f?method=download&shareKey=57a98971a5802f3d90d2a7fb1902b359)
    可以看出它的response是一堆JS，这说明，原始url不是直接重定向到最终网页的，而是先通过返回的响应体中的JS,做了一层跳转
    
    ，即跳到第二个url那里，再由第二个url经过重定向到最终链接。
    ![taobao_js](https://note.youdao.com/yws/api/personal/file/WEBa1a1659e70f3d6e87250cb89894c28d7?method=download&shareKey=b73eca6c997f86a014a0ec5fc9387956)
    因为我们只是想要拿到最终重定向的链接，而一个url的重定向链接就在它的response的header里的location这个参数里。因此可以在302的这个链接进行请求处理。注意，请求头中有一个referer，她是用来表示页面或资源的请求来源，该值就是初始的那个url。
    
    

代码如下：
```python
    # -*- coding:utf8 -*-
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
```