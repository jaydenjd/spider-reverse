# -*- coding: utf-8 -*-
# @Time   : 2021/4/11 下午9:11
# @Author : wu
"""
题目链接：http://match.yuanrenxue.com/match/7

相关库：
pip install fonttools
"""
import base64
import requests
from fontTools.ttLib import TTFont
import re
import os

cipher_map = {
    '10100100100101010010010010': 0,
    '1001101111': 1,
    '100110101001010101011110101000': 2,
    '10101100101000111100010101011010100101010100': 3,
    '111111111111111': 4,
    '1110101001001010110101010100101011111': 5,
    '10101010100001010111010101101010010101000': 6,
    '1111111': 7,
    '101010101101010001010101101010101010010010010101001000010': 8,
    '10010101001110101011010101010101000100100': 9
}


def gen_num_map():
    """
    生成上述的 cipher_map，只需要生成一次即可
    :return:
    """
    font_obj = TTFont('font.ttf')  # 注意文件名
    # 注意，这个顺序是与在线字体库上的看到的顺序是一致的，而每次这个顺序都是变化的，以看到的顺序为准
    nums = [6, 7, 1, 8, 0, 3, 9, 4, 5, 2]
    on_maps = []
    # 直接解析出的 font_obj['glyf'].glyphs，里面每个 key 是与 nums 的顺序关系是一致的，所以可以映射起来
    for key, value in font_obj['glyf'].glyphs.items():
        # 有一个开头的 .notdef，我们过滤掉即可
        _str = re.findall(r'\d+', key)
        if not _str:
            continue
        y = ''.join([str(i) for i in list(value.flags)])
        on_maps.append(y)
    res = zip(on_maps, nums)
    res = dict(sorted(res, key=lambda x: x[1]))  # 排个序
    print(res)


def save_woff(font_str, file='tmp'):
    b = base64.b64decode(font_str)
    with open(file + '.ttf', 'wb') as f:
        f.write(b)

    _font = TTFont(file + '.ttf')
    _font.saveXML(f'{file}.xml')
    font_mapping = {}
    glyphs = _font['glyf'].glyphs
    for key, value in glyphs.items():
        y = ''.join([str(i) for i in list(value.flags)])
        _str = re.findall(r'\d+', key)
        if not _str:
            continue
        font_mapping[_str[0]] = cipher_map[y]
    # 删除临时文件
    if os.path.exists(file + '.ttf'):
        os.remove(file + '.ttf')
    if os.path.exists(file + '.xml'):
        os.remove(file + '.xml')
    return font_mapping


def make_request(page=1):
    url = f'http://match.yuanrenxue.com/api/match/7?page={page}'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'match.yuanrenxue.com',
        'Pragma': 'no-cache',
        'Referer': 'http://match.yuanrenxue.com/match/7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    res = requests.get(url=url, headers=headers)
    font_mapping = save_woff(res.json()['woff'])
    cipher_nums = []
    for i in res.json().get('data', []):
        num = ''
        for n in i['value'].strip().split(' '):
            key = re.findall(r'\d+', n)[0]
            num += str(font_mapping[key])
        cipher_nums.append(num)
    print(cipher_nums)


if __name__ == '__main__':
    make_request()
