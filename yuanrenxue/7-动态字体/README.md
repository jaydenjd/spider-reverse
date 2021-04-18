链接：[动态字体](http://match.yuanrenxue.com/match/7)

正常流程走，打开开发者选项。发现接口返回的数据都是乱码的，这种其实就是字体加密了。

![yrx-ajax](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/reverse/font/yrx-ajax.png)

在 Elements 这边就直接可以看得出来字体是加密了

![ajax](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/reverse/font/font-messy.png)

对于字体加密，正常的处理流程应该是：

1. 找出并下载字体文件 - 难点
2. 用工具将字体识别出来
3. 利用 `fontTools` 把字体转换成xml 文件
4. 观察 xml 文件，找出字体与`乱码` 的对应关系 - 难点

### 1. 找出并下载字体文件

这道题还是比较简单的，在上面那张图明显可以看到响应体有一个 `woff` 的关键词，一般字体文件就是 `.woff` 或者 `.ttf`，所以我们应该第一时间想到，这可能就是跟字体有关的。而且很明显就是 base64 编码。这种就是将这串 base64 解码后，直接用字节流的方式写入一个空的字体文件即可。但其实一般正常的网站都不太可能直接给出的。

但我们也需要验证下，是否在响应体得到的 woff ，就是对应的字体文件

![ajax](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/reverse/font/ajax.png)

![ajax-font](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/reverse/font/ajax-font.png)

我们可以看到有这么一段 JS 的逻辑

```js
ttf = data.woff;
$('.font').text('').append('<style type="text/css">@font-face { font-family:"fonteditor";src: url(data:font/truetype;charset=utf-8;base64,' + ttf + '); }</style>');
data = data.data;
```

其实这里比较明显了，大概的意思就是用返回响应体的 woff 字段来解析 data 里的值。

既然这样，以最上面我们见到的第一张图为例，将 woff 复制下来，然后写入到 `.tff` 或者 `.woff` 文件中

```python
def write_woff(font_str, file='test'):
    b = base64.b64decode(font_str)
    with open(file + '.ttf', 'wb') as f:
        f.write(b)

    _font = TTFont(file + '.ttf')
    _font.saveXML(f'{file}.xml')
    
 font = 'AAEAAAAKAIAAAwAgT1MvMv4EYyIAAAEoAAAAYGNtYXARmVT7AAABpAAAAYpnbHlmNa/4EQAAA0gAAAP8aGVhZBfqMSQAAACsAAAANmhoZWEG7AEXAAAA5AAAACRobXR4ArwAAAAAAYgAAAAabG9jYQT/BgIAAAMwAAAAGG1heHABGABFAAABCAAAACBuYW1lUGhGMAAAB0QAAAJzcG9zdCvWcl8AAAm4AAAAiAABAAAAAQAA0y1CwF8PPPUACQPoAAAAANnIUd8AAAAA3KCbgwAO/+wCVgLxAAAACAACAAAAAAAAAAEAAAQk/qwAfgJYAAAAEAJIAAEAAAAAAAAAAAAAAAAAAAACAAEAAAALADkAAwAAAAAAAgAAAAoACgAAAP8AAAAAAAAABAIqAZAABQAIAtED0wAAAMQC0QPTAAACoABEAWkAAAIABQMAAAAAAAAAAAAAEAAAAAAAAAAAAAAAUGZFZABAonjylAQk/qwAfgQkAVQAAAABAAAAAAAAAAAAAAAgAAAAZAAAAlgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAMAAAAcAAEAAAAAAIQAAwABAAAAHAAEAGgAAAAWABAAAwAGonijJKNopUalk7WGw1jhOeNk8pT//wAAonijJKNopUalk7WGw1jhOeNk8pT//12QXN1cn1q+WnZKgDyrHskcpg1xAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwBMAF8AdQDLAPkBOwF4AZQBzQH+AAEAIv/sADMADQACAAA3MxUiEQ0hAAACAED/8gJQAvEAGwAoAAABIgcGFRQXFhc2NjQmIyIHJgcjJzQ3Nhc2FzMmAxYXFhQHBgciJyY0NgEvgTg2JVB7bYF5bSdDNRYCASU6UXQgjFq4PSoxNy4zXyozcALYd2iylmJcAQGKzYkrCVUReHg3CwuC3/6kEx4woTkmBS1oc14AAQBAAAACJALGAAYAABMVIQEzATVAAZL+410BEgLGP/15AnlNAAABAGwAAAF2AsYACQAAAQYGJxU2NxEzEQEfF2g0YjttAsYjPwxvLTj9mgLGAAMAQP/yAkAC2AAfACwAOAAAASIHBhUUFxYXFQYHBhUUFjI3NjU0JyYnNTY3NjU0JyYHMhcWFAcGIicmNDc2EzIXFhQHBiImNDc2ATN+Px0BFEdGHBNq/ENXMTwyMRoeI0FzQyI1JyunLyMsNVBFTg0NSLFeOCYC2EkuM1QeLQEhATcpR0uIOk5LRyk3ASEBLR5UMy5JPhM6cx0jIx1zOhP+yjgzdycrUnczOAACADP/8gIeAvEADAAZAAABJgcGEBcWMjc2ECcmBzIXFhQHBiInJjQ3NgEzkyFMTCH/QD8/QGxNPhgYPsIlGholAtgZjmL+w3BiYnABPWKOaWw+60SFhUTrPmwAAAEAQP/yAiQC2AArAAABIgcGBzM2Nhc2FxYUBiMjFTMyFhQHBiMGJyYnIxYXFhcyNjU0JyYnNjU0JgE+cE48BFEJUktELRpRM0w9TFIoND5HLjsMNxklZVB1dhwsMH6ZAthJK3RLTQEBATqBG0taighGCjEsbHtXLgFybzcrIh4okTpwAAIAOP/yAh4C2AAcACgAAAEiBhUUFxYzMjY3MxcUBwYjIicjFjM2NzY1NCcmBzIXFhQGIyImNTQ2ASV3biU8fTVrDAgNQClRgCNKF891TD9BPIJPOhxaS0BgbQLYi29tOkQ6OyF0TVeSzwFte5KuVWhPKgbJWXotUFsAAgAOAAACVgLGAAoADgAAAQEVIRUzNTM1IxEHMREjAXT+mgFtSZKSSfwCxv4tXpWVXgHTVv6DAAABAD7/8gIXAsYAJAAAEwMzNjc2MxYWFRQGIyInJicjBhcWMzI3NjU0JiMmByYHMzchNWcOMR0lJkFIUmVFPzIyAT8COkZhiShHemgkLTUgCgUBYgLG/n8hDj0XZStsaiIwNF8vOjpFZ4x6ByEaT/BHAAABADIAAAJQAtgAHQAAASIGFzMmNzYXMhYVFAcGBwYHBhUhNSE2NzY3NjQmAS9miQdOBjIeXzpGFkNOdilGAh7+Vxd1ixRGcALYe5aSBioBQ0QjXBoxXBphYEZIUVYveohyAAAAEgDeAAEAAAAAAAAAFwAAAAEAAAAAAAEADAAXAAEAAAAAAAIABwAjAAEAAAAAAAMAFAAqAAEAAAAAAAQAFAAqAAEAAAAAAAUACwA+AAEAAAAAAAYAFAAqAAEAAAAAAAoAKwBJAAEAAAAAAAsAEwB0AAMAAQQJAAAALgCHAAMAAQQJAAEAGAC1AAMAAQQJAAIADgDNAAMAAQQJAAMAKADbAAMAAQQJAAQAKADbAAMAAQQJAAUAFgEDAAMAAQQJAAYAKADbAAMAAQQJAAoAVgEZAAMAAQQJAAsAJgFvQ3JlYXRlZCBieSBmb250LWNhcnJpZXIuUGluZ0ZhbmcgU0NSZWd1bGFyLlBpbmdGYW5nLVNDLVJlZ3VsYXJWZXJzaW9uIDEuMEdlbmVyYXRlZCBieSBzdmcydHRmIGZyb20gRm9udGVsbG8gcHJvamVjdC5odHRwOi8vZm9udGVsbG8uY29tAEMAcgBlAGEAdABlAGQAIABiAHkAIABmAG8AbgB0AC0AYwBhAHIAcgBpAGUAcgAuAFAAaQBuAGcARgBhAG4AZwAgAFMAQwBSAGUAZwB1AGwAYQByAC4AUABpAG4AZwBGAGEAbgBnAC0AUwBDAC0AUgBlAGcAdQBsAGEAcgBWAGUAcgBzAGkAbwBuACAAMQAuADAARwBlAG4AZQByAGEAdABlAGQAIABiAHkAIABzAHYAZwAyAHQAdABmACAAZgByAG8AbQAgAEYAbwBuAHQAZQBsAGwAbwAgAHAAcgBvAGoAZQBjAHQALgBoAHQAdABwADoALwAvAGYAbwBuAHQAZQBsAGwAbwAuAGMAbwBtAAACAAAAAAAAAA4AAAAAAAAAAAAAAAAAAAAAAAAAAAALAAsAAAEDAQQBCwECAQYBBwEKAQgBBQEJB3VuaWE1NDYHdW5pYTMyNAd1bmllMTM5B3VuaWE1OTMHdW5pZjI5NAd1bmliNTg2B3VuaWEyNzgHdW5pZTM2NAd1bmlhMzY4B3VuaWMzNTg='


write_woff(font, 'font')
```

这样就在本地生成了两个文件，分别是 `font.ttf`（至于是 .tff 还是 .woff 格式，具体看识别字体的工具支持哪种格式） 和 `font.xml`

然后我们将 `font.tff`拉入一个在线识别字体的网站，https://kekee000.github.io/fonteditor/index-en.html

![font-editor](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/reverse/font/font-editor.png)

结合最上面那张图，这样就很明显发现了对应关系了，字体库与响应体返回的字符码，前面的内容是不一致的，但是后面的数字是对得上

| 字体库识别 | 实际对应数字 | 返回响应体中对应内容 |
| ---------- | ------------ | -------------------- |
| unif294    | 0            | &#xc294              |
| unic358    | 1            | &#xc358              |
| unie364    | 2            | &#xe364              |
| unib586    | 3            | &#xb586              |
| unia278    | 4            | &#xb278              |
| unia593    | 5            | &#xb593              |
| unia324    | 6            | &#xb324              |
| unie139    | 7            | &#xb139              |
| unia546    | 8            | &#xb546              |
| unia368    | 9            | &#xb368              |



以此类推，就可以得到 0-9 这10个数字的对应关系了。那是不是我们就可以直接用这个关系来解析了呢？

并不是，因为我们发现，每次刷新之后，每一个数字对应的字符码都是在变化的。这就是动态字体。

一般这种解法，都是要去字体的 `xml` 文件找到其对应关系。这种对应关系其实挺难找的，需要细心，一层一层往下找。

以 <GlyphOrder> 标签为例，我们先看看这里有无规律

```xml
<GlyphOrder>
    <!-- The 'id' attribute is only for humans; it is ignored when parsed. -->
    <GlyphID id="0" name=".notdef"/>
    <GlyphID id="1" name="unia324"/>
    <GlyphID id="2" name="unie139"/>
    <GlyphID id="3" name="unic358"/>
    <GlyphID id="4" name="unia546"/>
    <GlyphID id="5" name="unif294"/>
    <GlyphID id="6" name="unib586"/>
    <GlyphID id="7" name="unia368"/>
    <GlyphID id="8" name="unia278"/>
    <GlyphID id="9" name="unia593"/>
    <GlyphID id="10" name="unie364"/>
</GlyphOrder>
```

但这一串好像没什么规律，`id` 并不是字符码对应的数字，只是一个排序。

一圈找下来，好像都没发现规律。看网上之前有人解这道题，规律在 <extraNames> 标签下，是按照 0 - 9 的顺序排下去的，但我在做这道题的时候发现已经不是了。最后也是在 [Python反反爬之动态字体---随风漂移](https://syjun.vip/archives/283.html) 这篇博客上找到了解题思路。

我们以数字 `1` 为例

```xml
<glyf>
<TTGlyph name="unic358" xMin="108" yMin="0" xMax="374" yMax="710">
   <contour>
     <pt x="287" y="710" on="1"/>
     <pt x="264" y="675" on="0"/>
     <pt x="160" y="612" on="0"/>
     <pt x="108" y="624" on="1"/>
     <pt x="108" y="513" on="1"/>
     <pt x="206" y="558" on="0"/>
     <pt x="265" y="614" on="1"/>
     <pt x="265" y="0" on="1"/>
     <pt x="374" y="0" on="1"/>
     <pt x="374" y="710" on="1"/>
   </contour>
   <instructions/>
</TTGlyph>
</glyf>
```

发现动态字体每次生成的 `xml` 中，在这个标签里的 `on` 的值有一定的规律。`on` 本身的值就只有 0 和 1 两种。而不管 `xml` 怎么变，其按上到下的顺序都是 `1 0  0 1 1 0 1 1 1 1`，而其他数字也是如此。

那我们就可以知道了，如果某个字符码在 <TTGlyph> 标签里的 on 的顺序是 `1 0  0 1 1 0 1 1 1 1`，那么它就代表是数字 `1`。

既然如此的话，我们先把这层映射关系保存下来，然后后面就利用这层关系找出对应的数字即可。

那如何把这层映射关系记录下来呢，总不能一个个去扣下来，这样太耗费时间了。

我们可以使用 

```python
def gen_num_map():
    font_obj = TTFont('font.ttf') # 注意文件名
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
    res = dict(sorted(res, key=lambda x: x[1])) # 排个序
    print(res)
```

然后生成的映射关系如下

```python
{'10100100100101010010010010': 0, '1001101111': 1, '100110101001010101011110101000': 2, '10101100101000111100010101011010100101010100': 3, '111111111111111': 4, '1110101001001010110101010100101011111': 5, '10101010100001010111010101101010010101000': 6, '1111111': 7, '101010101101010001010101101010101010010010010101001000010': 8, '10010101001110101011010101010101000100100': 9}
```

后面我们就直接用这层映射关系去解析即可



```python
# -*- coding: utf-8 -*-
# @Time   : 2021/4/11 下午9:11
# @Author : wu
"""
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

```

