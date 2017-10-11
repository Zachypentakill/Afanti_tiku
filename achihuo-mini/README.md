
# Achihuo Mini

异步吃货 mini，异步吃货的精简版  

-----------

master 分支和 dev 分支已经不一致。

dev 实现了一个任务缓存抽象层，支持 master 和 slave 模式，进程可以优雅的结束，不会在进程结束是丢任务。

--------

下面是 dev 分支的用法

----------

achihuo mini 由 cache, asynchronous loop, task queue 几部分组成。

![sample1.png](http://git.lejent.cn/Spider/achihuo_mini/raw/dev/samle1.png)



下面是一个 demo:

```python
# -*- coding: utf-8 -*-
# filename: some_spider.py

import re

from achihuo_mini.async_loop import AsyncLoop
from achihuo_mini.item import Item

class SomeSpider(AsyncLoop):

    NAME = 'Some_spider'

    def __init__(self):
        super(SomeSpider, self).__init__(concurrency=10, cache_backend='redis')

    async def run(self):
        item = Item(dict(
            method = 'GET',
            url = 'https://www.v2ex.com/',
        ))
        self.add_task('get_articles', item, task_name=item.url)
        
    async def get_articles(self, item):
        resp = await self.async_web_request(item)
        html = resp.text
        titles = re.findall(r'<a href="/t/\d+">(.+?)</a>')
        for title in titles:
            print('title:', title)
        self.task_done(item.url)
    
if __name__ == '__main__':
    loop = SomeSpider()
    loop.start()
```

代码开始运行：

```shell
$ python3 some_spider.py start
```

结束代码运行：

```shell
$ python3 some_spider.py stop m1
```



首先我们创建一个基于 `AsyncLoop` 的类 `SomeSpider` 。

`run` 是初始运行方法，最初步的任务在这里添加，`run` 也不是必须的，使用别的脚步也能添加任务，只要是用 `NAME` 一样的 class 的实例。

`NAME` 是一个任务循环的唯一标示，两个不同的任务循环 `NAME` 不能一样。



### Achihuo Mini API

#### 1. achihuo_mini.async_loop 

这是 achihuo mini 最主要的模块，其中定义了任务获取方法，任务结束方法和命令控制。

_class_ `AsyncLoop(concurrency=10, cache_backend=DEFAULT_CACHE_BACKEND, debug=True, config_file=None)`

`concurrency` 是任务协程数量。

`cache_backend` 是缓存后端类型，目前支持 `'redis'`。

`debug` debug 模式

`config_file` 缓存后端配置文件。

>   日前，任务队列和完成任务hash表是用同一个后端，以后会将它们分开，比如 queue 用 mq，完成任务hash表用 redis

  

_function_ `run()`

初始运行任务，如果启用 master 模式则调用这个方法，如果启用 slave 模式则不调用。

  

_function_ `add_task(generator_name, *args, task_name=None, repeat=True, priority=False)`

任务添加函数。

`generator_name` 任务对应的协程名字(注意不是协程自己，是它的名字的字符串)。

`args` 协程需要的差数，目前不支持 kwargs。

`task_name` 单个任务名字，相当于任务的唯一id，None 是允许的，这时这样的任务可以无限添加。

`repeat` 是否重复，如果为 True，则可以重复添加任务，否则不可以重复添加任务。

`priority` 优先级，如果为 True, 则将任务添加于任务队列开头。

  

_function_ `task_done(task_name)`

任务结束函数。

调用后，将任务名 `task_name` 加入完成任务hash表。如果再调用 add_task(…., task_name=task_name, repeat=False)，则这个任务不再加入任务队列。

  

_function_ `uncache_task(task_name)`

将 `task_name` 任务移除完成任务hash表。



_function_ `stop()`

停止任务循环。





