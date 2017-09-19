# afanti 题库公用库  
## Using afanti_tiku_lib
新建 config 文件，内容格式如下 ，写入所需配置：

```
[mysql]
user = 
password = 
host = 
port = 

[postgresql]
user =
password =
host = 
port = 

[redis]
password = 
host = 
port = 
db = 

[rediscluster]
startup_nodes = 
password = 
```



## 1. Compatibility  

compat.py 中定义了兼容 py2 和 py3 的方法。  



## 2. url  

url 的操作函数定义在 url/ 中  



## 3. utils  

utils/ 中定义实用函数, 如： md5\_string  



## 4. html

用于对 html string 对处理

### 4.1 html.magic



_class_ `HtmlMagic(spider_source, download=True, headers=None, proxy=False, beautify=False, mysql_db=None, config_file=None)`

>    html 魔法

将 html 用 html.image_magic 处理，并用 html.beautify_html 做修正（默认不执行）。

如果 download 为 *True*，`img_url` 将被传递给 image_downloader 服务，headers, proxy 为给 image_dowloader 对参数。

如果 beautify 为 *True*，html_string 将被 html.beautify_html 处理。

mysql_db 为 image_archive 所在的数据库，如果为 *None*，将用默认数据库。

config_file 为配置文件路径，默认用 afanti_tiku_lib.config 为数据库的链接参数。

所以的参数都作为 default 用于 `bewitch`

​          

_method_ `bewitch(html_string, spider_url, spider_source=0, download=None, headers=None, proxy=None, beautify=None, mysql_db＝None)`

bewitch 将 html_string 进行处理，返回处理后的 html_string。

​          

### 4.2 html.image_magic

_class_ `ImageMagic(uri2oss=None, mysql_db=None, config_file=None)`

>    image 魔法

将 html_string 中的 `<img>` 标签做以下处理。

`img_url` 存入 `image_archive` 。

然后将 `img_url` 传入 `image_downloader` 服务。

然后转成 `oss` 上的链接，并将 `img_url` 用其代替。

​          

_method_ `bewitch(html_string, spider_url, spider_source, download=True, headers=None, proxy=False)` 

bewitch 将 html_string 进行处理，返回处理后的 html_string。

​          

### 4.3 html.format_html

_function_ `remove_option_value(raw_options)`

`raw_options` 是一个包含选项的 list，选项一定要包含 `A. B. C. ..`  这样的开始标。

e.g.

```python
>>> options = ['<some>A. test A</some>', 'B. 一般的B.', 'C．特殊的C．', 'D. 特殊的D．']
>>> options = remove_option_value(options)
>>> options
['<some> test A</some>', '一般的B.', '特殊的C．', '特殊的D．']
```

​          

_function_ `format_spans(html_string)`

对于 doc 转出来的 html，其中有很多不合我们标准的 span，这个函数将这些 span 转为规范的格式。

​          

_funtion_ `format_options(html_string)`

有一些题目的选项无法提出，同时它们用 `&nbsp;` 来调整间距，这在手机上展示会有很多样式上的问题。这函数将符合正则 `re.compile(r'(<(?:p|P|div|DIV|td|TD)[^<>]*>(?:\s|&nbsp;)*|)([ABCDEFGHIJKLMNOPQRSTUVWXYZ](\.|．))')` 的 str 前面加 `<br>`

​          

下面是 [题库题型规范模板](http://redmine.lejent.cn/projects/tiku/wiki/题库题型规范模板) 中的定义

```python
UNDERLINE = '<span class="aft_underline">{}</span>'
LINE_THROUGH = '<span class="aft_linethrough">{}</span>'
OVERLINE = '<span class="aft_overline">{}</span>'
PUT = '<div class="aft_put">{}</div>'
```

​          

### 4.4 html.beautify_html

_function_ `remove_empty_elements(html_string, filter=None)`

移除 html_string 中的空标签，`filter` 是一个过滤函数决定那些空标签要删除，其接受一个参数，代表本次判断的空标签，如果返回 `True` 则删除这个空标签，返回 `False` 则保留。

如果 `filter` 为 `None` 则用内建的过滤函数处理。



_function_ `limit_nbsp(html_string)`

将 `re.compile(r'(\s*&nbsp;\s*){6,}', flags=re.I)` 匹配到的 str 替换为 `'&nbsp;' * 6`

​               

_function_ `center_image(html_string)`

将 `html_string` 中的图片变为标准剧中样式，如下:

```html
<img src="url" width="..." height="..." style="vertical-align: middle;">
```

​               

_function_ `def remove_tag(tag, html_string, regex=False, flags=re.U, all=False, check=None)`

删除 tag (all=False) 内容 或 整个 tag (`all=True`)，

参数同 `get_html_element`

​               

_function_ `remove_element(tag, html_string, regex=False, flags=re.U, check=None)`

同 `remove_tag(tag, html_string, regex=False, flags=re.U, all=True, check=None)`

​               

_function_ `remove_start_end_br(html_string)`

去出 html 开头结尾的 `<br>`

​               

_function_ `remove_a_tag(html_string, all=False)`

去除包含 `href` 的 `<a>` 

​               

还有其他的一些函数：

_function_ `remove_style_tag(html_string)`

_function_ `remove_span_tag(html_string)`

​               

### 4.5 html.util

_function_ `html_split(html_string, sep, offset=0, regex=False, flags=re.U, with_style=True)`

用 `sep` 切分 html 并保持标签完整。

```python
>>> a = '<p class="pp"><b>gs v sg</b></p>'
>>> html_split(a, ' v ', with_style=True)
['<p class="pp"><b>gs</b></p>', '<p class="pp"><b>sg</b></p>']
```

​               

## 5. latex

用于处理 latex。



### 5.1 latex.latex2png

用 texlive 套件将 latex math 转成 png，用到 `latex` ,`dvipng`

​               

_function_ `to_png(raw_tex, outfile=None, dpi=200, check=True, only_dvi=False)`

返回 `True` 转换成功, `False` 转换出错。

将 raw_tex (latex math) 转为 png，保存到 outfile。

如果 outfile 为 `None` 则用 `latex2png.DEFUALT_OUTFILE` 作为 outfile。

如果 check 为 `None` 则如果 raw_tex 不需要转为 png 也可以很好显示，则不转。

如果 only_dvi 为 `True` 则只转换到 dvi，并将其保存到 outfile。

​               

### 5.2 latex.chinese

处理中文字符

_function_ `safe_chinese(string)`

返回 str

将中文字符放入 `\text{中文}` 可在 png 中显示中文。

​               

### 5.3 latex.util

_function_ `latex_clear(tex)`

返回 str

将 tex 中的不必要的东西做替换，如 `\underline{}` 换成 `'\t' * 5`

​               

_function_ `is_latex(tex)`

返回 `True` 如果 tex 含有需要用 png 显示的东西，反之返回 `False`

​               

_function_ `fix_underline(tex)` 

将 `\t{5,}` 换为 `<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<u/>`

​               

_function_ `fix_latex_underline(tex)`

将 `\t{5,}` 换为 `\underline{\qquad}`

​               

_function_ `fix_latex_table(tex)`

返回 str

形如`\begin{array}{ccc}` 的 tex 有可能会出错，如果少 `c` ，但是 **mathjax** 可以显现，但是 latex 转 dvi 会出错，需要修正。

​               

_function_ ` displaystyle(html_string, latex_tag=None, regex=False, flags=re.U, latex=True, mml=True)`

纠正没有 `\displaystyle` latex 中的 displaystyle 展示。

>   \frac{\frac{1/2}}{\frac{3}{4}} 这个第二级 frac 是不需要 displaystyle 的，因为加上会很难看。

**注意：这步只能用在绘制 latex 时，普通 latex 不需要 \displaystyle**

​               

_function_ `find_latex_subsups(latex)`

找出 latex 中的 `_{}` 或 `^{}` (上下标)

​               

_function_ `find_latexes(html_string, with_delimiter=True)`

找出 html_string 中的 latex, 这些 latex 的格式符合 `$ latex $` 或 `\( latex \)` 。

如果 `with_delimiter=True` 这找出的 latex 带有 `$` 或 `\(\)` ，

如果 `with_delimiter=False` 则不带。

​               

### 5.4 convertor

#### 5.4.1 jyeoo_convertor

将 jyeoo 公式格式转为 latex

-   用法

    ```python
    from afanti_tiku_lib.latex.jyeoo_convertor import to_latex

    html_string = """<em>【解答】</em>解：由题意A∪B=A，即B⊆A，又<span dealflag="1" class="MathJye" mathtag="math" style="whiteSpace:nowrap;wordSpacing:normal;wordWrap:normal">A={1，3，<table cellspacing="-1" cellpadding="-1"><tr><td style="font-size: 0px"><div hassize="7"><div style="width:6px;background: url('http://img.jyeoo.net/images/formula/part/8730U.png') repeat-y; height: 1px;overflow: hidden" muststretch="v"></div><div style="width:6px;background: url('http://img.jyeoo.net/images/formula/part/8730D.png') no-repeat; height: 7px; overflow: hidden"></div></div></td><td style="padding:0;padding-left: 2px; border-top: black 1px solid;line-height:normal">m</td></tr></table>}</span>，B={1，m}，<br />∴m=3或m=<span dealflag="1" class="MathJye" mathtag="math" style="whiteSpace:nowrap;wordSpacing:normal;wordWrap:normal"><table cellspacing="-1" cellpadding="-1"><tr><td style="font-size: 0px"><div hassize="7"><div style="width:6px;background: url('http://img.jyeoo.net/images/formula/part/8730U.png') repeat-y; height: 1px;overflow: hidden" muststretch="v"></div><div style="width:6px;background: url('http://img.jyeoo.net/images/formula/part/8730D.png') no-repeat; height: 7px; overflow: hidden"></div></div></td><td style="padding:0;padding-left: 2px; border-top: black 1px solid;line-height:normal">m</td></tr></table></span>，解得m=3或m=0及m=1，<br />验证知，m=1不满足集合的互异性，故m=0或m=3即为所求，<br />故选：B．<!--E6--></div><div class="pt7"><!--B7-->"""

    latex_html_string, latexes = to_latex(html_string)

    # latex_html_string 是转换后的字符串
    # latexes 是 latex_html_string 中包含的 latex
    ```


​               

*   绘制 latex

    见 git.lejent.cn/Spider/mathjax_render

    ​



## 6. 数据库操作

### 6.1 dbs/mysql_pool

mysql 操作库

用法：

```python
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.sql import update_sql, select_sql, replace_sql
from afanti_tiku_lib.dbs.execute import execute

CONFIG = '/path/to/config'
mysql = CommonMysql('db', config_file=CONFIG)
mysql_conn = mysql.connection()

cols = {'k1': 'v1', 'k2': 'v2'}

# insert
sql, vals = insert_sql('table', cols, ignore=True)
result = execute(mysql_conn, sql, values=vals)

# update
sql, vals = insert_sql('table', cols, where='where query')
result = execute(mysql_conn, sql, values=vals)

# replace
sql, vals = replace_sql('table', cols)
result = execute(mysql_conn, sql, values=vals)
```

>   注意：innodb 的 table， `execute` 执行完后要 `mysql_conn.commit()` 

​               

### 6.2 dbs/redis_proxy

`redis_proxy.py` 实现了对 python 对象的一个包装，让 python 对象序列化存储于 redis。

​               

_class_ `RedisProxy(namespace, host=None, port=None, password=None, db=0, config_file=None, **kwargs))`

RedisProxy class，用它生成 redis_proxy 对象。

`namespace` 是一个 `str` ，提供名字空间。

如果提供 `config_file` 就不需要 `host`, `port`, `password`

​               

>   下面生成的对象，如果有 `raw=False` 除了 key, value 都被 `pickle.dumps` 过。
>
>   如果有 `raw=True` 则 key, value 都不 `pickle.dumps`

​               

_method_ `make_set(name, raw=False)`

生成一个 `RedisSet` 对象，对应 redis 的 set。

在 redis 上，存储这个对象的 `key` 是 `namespace + '.' + name`。

​               

_method_ `make_list(name, maxsize=None, raw=False)`

生成一个 `RedisList` 对象，对应 redis 的 list。

在 redis 上，存储这个对象的 `key` 是 `namespace + '.' + name`。

​               

_method_ `make_hash(name, raw=False)`

生成一个 `RedisHash` 对象，对应 redis 的 hash。

在 redis 上，存储这个对象的 `key` 是 `namespace + '.' + name`。

​               

_method_ `make_string(name, raw=False)`

生成一个 `RedisString` 对象，对应 redis 的 string。

在 redis 上，存储这个对象的 `key` 是 `namespace + '.' + name`。

​               

_class_ `RedisClusterProxy(namespace, startup_nodes=None, password=None, config_file=None, decode_responses=False, **kwargs)`

RedisClusterProxy class，用它生成 redis_cluster_proxy 对象。用于 redis cluster

`namespace` 是一个 `str` ，提供名字空间。

如果提供 `config_file` 就不需要 `startup_nodes`,  `password`

methods 同上。

​               

_class_ `RedisSet(name, connect, redis_proxy=None, raw=False)`

RedisSet 封装一个 python set 对象于 redis。

`connect` 是 redis 的连接对象。

`redis_proxy` 是用于生成 redis_set 对象的 redis_proxy 对象。可以为 `None`，但是当 `connect` 断掉后不能重连。

用法：

```python
redis_set.add(val)
val in redis_set
redis_set.remove(val)
```

​               

_class_ `RedisList(name, connect, maxsize=None, redis_proxy=None, raw=False)`

用法：

```python
redis_list.put(val)   # O(1)
redis_list.get()   # O(1)

redis_list.append(val)   # O(1)
redis_list.appendleft(val)   # O(1)

redis_list.pop(block=False)   # O(1)
redis_list.popleft(block=False)   # O(1)

for val in redis_list:   # O(1) * n
    print(val)
    
val in redis_list  # O(n)
```

​               

_class_ `RedisHash(name, connect, redis_proxy=None, raw=False)`

用法：

```python
redis_hash.set(key, val)
redis_hash.get(key, block=False)

for key in redis_hash:
    val = redis.get(key)
    
key in redis_hash

for k, v in redis_hash.items():
    print(k, v)
    
redis_hash.hincrby(key, num)   # only for raw=True

redis_hash.remove(key)
```

​               

_class_ `RedisString(name, connect, redis_proxy=None, raw=False)`

