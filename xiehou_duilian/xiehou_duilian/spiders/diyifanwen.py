# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from urllib import parse
from xiehou_duilian.ultil.command import get_md5,extract_num
from xiehou_duilian.items import XiehouItem

class DiyifanwenSpider(scrapy.Spider):
    name = 'diyifanwen'
    allowed_domains = ['diyifanwen.com']
    start_urls = ['http://www.diyifanwen.com/tool/xiehouyu/']
    headers = {
        "GET ": "/1/ HTTP/1.1",
        "Host": "www.diyifanwen.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }
    # title_pool = [{"日常歇后语": ["谐音歇后语","历史故事","幽默搞笑","骂人","比喻/喻事","成语","粤语","歇后语","歇后语大全及答案"]},
    #               {"人物" : ["老太太","光棍","矮子","夫妻","和尚","寡妇","瞎子","光头","哑巴","人称"]},
    #               {"常用" : ["眼睛","鼻子","嘴巴","豆腐","太阳","月亮","飞机","包子","馒头","桥","蚊子","鱼","鸟","竹"]},
    #               {"品质" : ["是非不分","挑剔惹事","投机取巧","骄傲自大","谦虚谨慎","勤劳俭朴","清楚明白","热情大方","任人摆布","认真负责","小气刻薄","无私无畏","团结一致","外好内差","稳当落实","枉费心机","无动于衷","无关要紧","贪图"]},
    #             {"更多分类" : ["容易","艰难","妄想","揭露","进步","决心","亲密","清闲","热闹","失败","希望","威胁","危险","外行","完蛋","香甜","浪费","理睬","欺软","奇巧","起作用","损失","少慢差费","特别突出","施展不开"]}
    #             ]
    title_pool = [{"日常歇后语": "谐音歇后语 历史故事 幽默搞笑 骂人 比喻/喻事 成语 粤语 歇后语 歇后语大全及答案"},
                  {"人物": "老太太 光棍 矮子 夫妻 和尚 寡妇 瞎子 光头 哑巴 人称"},
                  {"常用": "眼睛 鼻子 嘴巴 豆腐 太阳 月亮 飞机 包子 馒头 桥 蚊子 鱼 鸟 竹"},
                  {"品质": "是非不分 挑剔惹事 投机取巧 骄傲自大 谦虚谨慎 勤劳俭朴 清楚明白 热情大方 任人摆布 认真负责 小气刻薄 无私无畏 团结一致 外好内差 稳当落实 枉费心机 无动于衷 无关要紧 贪图"},
                  {"更多分类": "容易 艰难 妄想 揭露 进步 决心 亲密 清闲 热闹 失败 希望 威胁 危险 外行 完蛋 香甜 浪费 理睬 欺软 奇巧 起作用 损失 少慢差费 特别突出 施展不开"}
                  ]

    def parse(self, response):
        a = response.url
        items = {}
        urls_list = response.xpath("//dl[@class='IndexDl']/dd/a/@href").extract()
        second_title = response.xpath("//dl[@class='IndexDl']/dd/a/text()").extract()
        new_list = zip(urls_list, second_title)
        for nodes in new_list:
            a = nodes[0]
            b = nodes[1]
            yield scrapy.Request(url=nodes[0], dont_filter=True, meta={"second_title": nodes[1]}, headers=self.headers, callback=self.parse_url)


    #html_url, first_title, second_title, option, answer, md5
    def parse_detail(self,response):
        xiehouyu = XiehouItem()
        xiehouyu["html_url"] = response.url
        second_title = response.meta.get("second_title", "")
        xiehouyu["second_title"] = second_title

        try:
            first_title = response.xpath("//div[@id='ArtLeft']/div[@class='list_info']/p/a[1]/text()").extract()
            if len(first_title) == 0:
                for i in range(len(self.title_pool)):
                    for keys, values in self.title_pool[i].items():
                        if second_title in values:
                            xiehouyu["first_title"] = keys
            else:
                xiehouyu["first_title"] = first_title[0]
        except Exception as e:
            print("这是提取first_title时候出错：" ,  e)


        try:
            option = response.xpath("//div[@id='ArtLeft']/dl/dt/a/text()").extract()
            if len(option) == 0:
                xiehouyu["option"] = 0
            else:
                xiehouyu["option"] = option
        except:
            print("这是提取option时候出错：" , e)

        try:
            answer = response.xpath('//*[@id="ArtLeft"]/dl/dt/span[@class="answer off"]/text()').extract()
            if len(answer) == 0:
                xiehouyu["answer"] = 0
            else:
                xiehouyu["answer"] = answer
        except:
            print("这是提取answer时候出错：" , e)

        md_string = zip(option, answer)
        md5 = []
        for node in md_string:
            md5_string = second_title + node[0] + node[1].replace(" —— ", "")
            md5_nodes = get_md5(str(md_string).encode("utf-8"))
            md5.append(md5_nodes)
        xiehouyu["md5"] = md5
        yield xiehouyu


    def parse_url(self,response):
        url_list = []
        url_list.append(response.url)
        second_title = response.meta.get("second_title", "")
        try:
            next_url = response.xpath('//div[@id="CutPage"]/a[last()]/@href').extract()
            try:
                new_number = re.findall(".+index_(.+?).ht", next_url[0])
                a = int(new_number[0]) + 1
                if a >= 3:
                    for i in range(2,a):
                        new_url = response.url + "index_" + str(i) + ".htm"
                        url_list.append(new_url)
                for node_url in url_list:
                    yield scrapy.Request(url=node_url, dont_filter=True, meta={"second_title": second_title},headers=self.headers, callback=self.parse_detail)
            except:
                pass
        except Exception as e:
            print(e)