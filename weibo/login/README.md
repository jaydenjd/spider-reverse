在开始进行模拟登陆前，先了解下 **Chrome 是如何 删除 cookie 以及禁用缓存**

#### 1. 删除 cookie

![cookie](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/imgs/weibo/Snipaste_2020-03-21_22-22-31.png)



![cookie2](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/imgs/weibo/Snipaste_2020-03-21_22-23-11.png)

#### 2. 禁用指定页面缓存

有时候某些 js 文件会先加载在本地，后面再发起请求时，会直接从本地浏览器的缓存中读取 js文件，导致有时候抓包会漏掉这个 js 文件。

##### 1. 打开需清缓存的页面，右键`检查` 或者按下`F12`，勾选 `Network`标签下 `Disable cache`选项

![cache](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/imgs/weibo/cache.png)



##### 2. 按 `F5 `或右键 `重新加载` 刷新页面内容

这时候就已经是禁用缓存了



## 微博模拟登陆

正式开始进行模拟登陆。

在这里，需要借助抓包工具，我推荐的是 charles，简单好用。

先访问 https://weibo.com/

（1）开启 Charles 抓包代理，Proxy -> macOS Proxy。

（2）当然网页也要打开调试工具，右键`检查` 或者按下`F12`。在最开始分析一个页面时，最好先删掉所有 cookie以及 js 缓存，否则会影响我们的分析。js 缓存在微博这里是一个大坑，因为我就是一开始没有禁用，导致请求时用了本地缓存的 js，而抓不到加密的 js 包。

（3）在输入账号后，把光标移动到输密码框时（此时还未输入密码），在 web 的 network 页面和 charles 上都可以看到出现了一条请求，从接口名字看来，这是一条预登陆的接口，比较有经验的人可能就知道，这应该跟后面登陆的接口有关系。

![prelogin](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/imgs/weibo/prelogin.png)

（4）接着输入密码，就完成登陆了。这时候我们通过 charles ，按时间顺序来分析整个登陆的过程。

直接按请求顺序看下来，或者通过搜索关键词` login`，我们可以发现一个接口，`https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)`，很明显这个就是我们登陆请求的接口。但是这参数中没有找到关于我们的账号密码的参数，而且看起来有些是加密过的参数。而且这里有几个参数跟上面`prelogin`的接口返回的数据中是一样的，很明显就是从那里获取的值。先分析下请求的参数

![weibo_login](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/imgs/weibo/login.png)

以下可能固定参数用 '/' 表示。其他特殊的另做说明。将 `prelogin`返回的参数赋值给变量 `json_data`

| 字段        | 类型 | 说明                           |
| ----------- | ---- | ------------------------------ |
| entry       | str  | /                              |
| gateway     | str  | /                              |
| savestate   | str  | 经多次抓包发现，这个值是固定的 |
| qrcode_flag | str  | /                              |
| useticket   | str  | /                              |
| pagerefer   | str  | /                              |
| vsnf        | str  | /                              |
| su          | str  | 未知，=`json_data`['su']       |
| service     | str  | /                              |
| servertime  | str  | 未知，看起来像时间戳           |
| nonce       | str  | 未知，=`json_data`['nonce']    |
| pwencode    | str  | 加密方式                       |
| rsakv       | str  | 未知，=`json_data`['rsakv']    |
| sp          | str  | 未知                           |
| sr          | str  | 分辨率？                       |
| encoding    | str  | 编码                           |
| prelt       | str  | 未知                           |
| url         | str  | /                              |
| returntype  | str  | /                              |

那么上述的参数中，还未知道的就是 `login`接口的 `sp` 和 `prelt`，以及 `prelogin` 中的 `su`了。

通过搜索关键词，`su\s?=` 或者 `sp\s?=` (这是正则语法，\s?表示0或1个空格，怕有些中间会多了个空格) ，这时候找到了一个 js 文件，`https://i.sso.sina.com.cn/js/ssologin.js`。复制出来看，进行分析。找到一个关键的函数。从函数的内容很明显看出，`su`就是 username 的加密，`sp`就是 password 的加密。那看来其他参数的加密也会在这个 js 文件中了。

![makereq](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/imgs/weibo/makereq.png)

然后顺着这个，最后也找到了参数 `prelt`的生成方法。

总结下上述整个流程，

- 根据用户名 `username` 得到加密后的用户名 `su`
- 根据 `su` 请求 `prelogin` 接口，得到一个 json 串，里边包含加密密码用到的各种参数，`servertime`、`nonce`等
- 根据 json 串和部分加密，包括`sp`以及`prelt`参数组成 `login`的参数，完成登陆请求

（5）如何通过 python 加密。上述我们已经得知了几个加密参数的方法了，但却是 js 写的。我们可以做的方式有两种，一是将每个参数的加密方法翻译成 python；二是将 js 保存下来，或者用 js 另外写出参数的加密，然后用 python 去调 js，返回其加密后的值，具体是用到 python 的 `execjs`库，`pip install PyExecJS`。在这里先给出转成 python 的加密方法。

```python
  """
  从 js 中看出，password是有两种方法，一种是 rsa.PublicKey，一种是 hash。默认是选择前者
  应该是选择哪种都可以，只要参数 pwencode 设置成对应值便可，如果是rsa.PublicKey，pwencode="rsa2"，后者则是pwencode = "wsse"，在这里我只试了第一种，第二种没成功，不知道什么原因，后面有时间再看看
  """

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
```

（6）但到这里还是未完全登陆的，通过抓包可看到，`login` 接口返回的响应体中，有一段数据

```js
<script type="text/javascript" language="javascript">
		location.replace("https://login.sina.com.cn/crossdomain2.php?action=login&entry=weibo&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogin%3Fssosavestate%3D1616337031%26url%3Dhttps%253A%252F%252Fweibo.com%252Fajaxlogin.php%253Fframelogin%253D1%2526callback%253Dparent.sinaSSOController.feedBackUrlCallBack%2526sudaref%253Dweibo.com%26display%3D0%26ticket%3DST-NjEzNTI5NTk3MA%3D%3D-1584801031-gz-2D4D97C9BDDC99490C4F0C3DA9C586C0-1%26retcode%3D0&login_time=1584801030&sign=01227d23219dacc0&sr=1920%2A1080");
		</script>
```

而在 js 中，Location 对象的 replace() 方法用于重新加载当前文档（页面），语法如下：

```js
location.replace(new_URL)
```

即在登陆后，会自动加载 replace 中的 url 以替换当前页面。

但由于我们是模拟登陆，并不会自动触发，因此我们需要请求这个 url。接着，这个页面返回的响应体中，仍然是有一段 location.replace。继续请求这个url 。

![login](https://img-1257127044.cos.ap-guangzhou.myqcloud.com/imgs/weibo/login1.png)

最后返回的响应体是

```json
sinaSSOController.doCrossDomainCallBack({
	'retcode': 0,
	'scriptId': 'ssoscript0'
});
```

到这里算是结束了。此时便是登陆成功了。

（7）验证是否登陆成功。在浏览器中，如果我们人工登陆了一个账号，而且 cookie 还没过期，这时候访问 https://weibo.com/ 就会自动重定向到个人主页。因此为了验证是否登陆成功，我们需要再最后请求一次 https://weibo.com/， 如果自动重定向到我们登陆账号的个人主页，便证明是登陆成功了。

（8）其实微博登陆加密的这个 js 中，除了一些参数的加密，还有其他一些设置在里面，例如 cookie 的过期时间。我觉得有时间的研究下的话，肯定还是大有收获的。



#### 最后总结

微博登陆确实比较麻烦，如果上述有一个步骤没做好，那都是前功尽弃。完整的请求过程是，

- 先请求预登陆`prelogin`
- 再请求 `login`接口
- 从 `login`接口返回的响应体中，提取出新加载的 url，发起请求。然后得到响应体后，再新加载的 url，发起请求。
- 最后为了验证是否登陆成功，我们可以请求 https://weibo.com/ 接口。

上述就是微博的

开始分析一个新的网页，一般我自己的步骤是：

1. 打开需要分析的网页，删除 cookie。然后 F2 打开开发者工具，先禁用缓存，然后再清除之前的日志记录。如果觉得还不妥，可以直接开启浏览器无痕模式。
2. 结合 Charles。为什么需要使用 Charles？因为我觉得 Charles 真的很强大，但用起来又很简单。首先 app 抓包肯定离不开它，虽然浏览器有自己的 network 调试工具，但是全部请求的记录看起来不是很清晰，而且分析的过程中，如果点击了某个 url，自动打开到另一个窗口的，这时候这个窗口就没记录了。而 charles 能帮我们记录完整的过程，更重要的是，它能选择以时间顺序查看，可以帮我们分析全部请求的完整加载顺序以及逻辑。
3. 先完整地完成整个点击动作，再 charles 中看看都有哪些请求。然后觉得可疑的再逐个分析。