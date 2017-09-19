# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import hashlib
import unittest
import re

import requests

from afanti_tiku_lib.url.extract_img_from_html import extract_image_info_with_md5 as extract
from afanti_tiku_lib.url import extract_img_from_html
from afanti_tiku_lib.url.extract_img_from_html import extract_oss_info
from afanti_tiku_lib.url.uri2oss import Uri2oss


class TestExtract(unittest.TestCase):

    def test_extract_with_slash(self):
        html = '''这是一道题目<img src=\\'b3c27ac1ebeda4cfa37d6a84e87991b9.png\\'>。'''
        img_urls_lst = extract_img_from_html.extract_image_info_with_md5_after_del_backslash(html)
        self.assertEqual(len(img_urls_lst), 1)
        self.assertEqual(img_urls_lst[0][0], 'b3c27ac1ebeda4cfa37d6a84e87991b9.png')

    def test_extract_image_infos(self):
        html = '''已知图中A的位置是（3，1 ），请在图中打出B（1，2），C（6，2），D（7，1），并顺次连接点A、B、C、D、A，如果图中每小格是边条为1厘米的正方形，求出这个图形的面积．<br /><img src="b3c27ac 1ebeda4cfa37d6a84e87991b9.png" style="vertical-align:middle;" />．'''
        img_url_lst = extract_img_from_html.extract_image_infos(html)
        self.assertEqual(img_url_lst, ['b3c27ac 1ebeda4cfa37d6a84e87991b9.png'])

        html = '''test img <img _src="http://baod.con/test.png" src=http://csdn.com/index/_test/this_is-img?key=123213/ width="20"> img ends'''
        img_url_lst = extract_img_from_html.extract_image_infos(html)
        self.assertEqual(img_url_lst, ['http://csdn.com/index/_test/this_is-img?key=123213/'])

        html = '''test img<img src=     width="10px"> asdadasda'''
        img_url_lst = extract_img_from_html.extract_image_infos(html)
        self.assertEqual(img_url_lst, [])

        html = '''test img<img src=http://www.sdfdsf?width=49 width=59>'''
        img_url_lst = extract_img_from_html.extract_image_infos(html)
        self.assertEqual(img_url_lst, ['http://www.sdfdsf?width=49'])


    def test_extract_normal(self):
        # 检测是否是能够不重复提取img_url， 及md5和扩展名是否正确
        html = '''<hr class="divider"><section><h4 class="section-header">答案</h4>h4><img src="/question_bank/18/fe7/902ee48af3f57d101b16806711820" width="359" height="17" >
                <p style="margin:0pt; orphans:0; text-align:justify; widows:0"><span style=" "></span>span></p>p></img>section><br> '''
        img_url_lst = extract(html)
        self.assertEqual(len(img_url_lst), 1)

        img_url = '/question_bank/18/fe7/902ee48af3f57d101b16806711820'
        img_md5 = hashlib.new('md5', img_url.encode('utf-8')).hexdigest()
        self.assertEqual(
            img_url_lst[0],
            (img_url, img_url, img_md5, '')
        )

        # 检测换行对提取的影响
        html = '''<hr class="divider"><section><h4 class="section-header">答案</h4>h4><img src="/question_bank/18/fe7/902ee48af3f57d101b16806711820" width="359" height="17"
                  ><p style="margin:0pt; orphans:0; text-align:justify; widows:0"><span style=" "></span>span></p>p></img>section><br> '''
        img_url_lst = extract(html)
        self.assertEqual(len(img_url_lst), 1)
        self.assertEqual(
            img_url_lst[0],
            (img_url, img_url, img_md5, '')
        )

    def test_extract_back(self):
        # 检测对background_url的提取
        html = '''<hr class="divider"><section><h4 class="section-header">解析</h4>h4><div class="wb_math"><div>
                 用最高温度减去最低温度,然后根据有理数的减法运算法则,减去一个数等于加上这个数的相反数进行计算即可得解.
                  <br />
                  </div>div></div>div></section>section><section><h4 class="section-header">答案</h4>h4><div class="wb_math"><div>
                   解:
                <span class="img bgimg_b" style="width:174px;height:19px;background:url(/question_bank/13/662/02dcf562e9eae1e6becfa9afa3421.jpg) no-repeat -0px -0px;"></span>span>.
                 <br />故选
                  <span class="img bgimg_b" style="width:13px;height:11px;background:url(/question_bank/13/662/02dcf562e9eae1e6becfa9afa3421.jpg) no-repeat -174px -0px;"></span>span>.
                   <br />
               </div>div></div>div></section>section><section><h4 class="section-header">点评</h4>h4><div class="wb_math"><div>
                本题考查了有理数的减法运算法则,熟记减去一个数等于加上这个数的相反数是解题的关键.
                 <br />
                 </div>div></div>div></section>section><br>'''
        img_url_lst = extract(html, base_url='http://qbimg3.xueba100.com')
        self.assertEqual(len(img_url_lst), 1)

        img_url = '/question_bank/13/662/02dcf562e9eae1e6becfa9afa3421.jpg'
        abs_url = 'http://qbimg3.xueba100.com/question_bank/13/662/02dcf562e9eae1e6becfa9afa3421.jpg'
        img_md5 = hashlib.new('md5', abs_url.encode('utf-8')).hexdigest()
        self.assertEqual(
            img_url_lst[-1],
            (img_url, abs_url, img_md5, '.jpg')
        )

    def test_extract_b64_img(self):
        html = '''<p>这是一段答案。 这是一个图片<img class="kfformula" src="data:image/png;base64,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" data-latex="\dfrac {5} {7}，\dfrac {2} {3}，\dfrac {5} {7}，\dfrac {1} {3}，"/></p>
            <p>这是另一张图片<img src="http://www.afanti100.com/1234567.png"></p>'''
        img_url_lst = extract_img_from_html.extract_base64_image_info_with_md5(html)
        self.assertEqual(len(img_url_lst), 2)
        self.assertEqual(len(img_url_lst[0]), 1)
        self.assertEqual(img_url_lst[0][0][0], "http://www.afanti100.com/1234567.png")
        self.assertEqual(len(img_url_lst[1]), 1)
        url = re.findall(r'src="(.*?)"', html)[0]
        md5=hashlib.new('md5', url.replace('data:image/png;base64,', '').encode('utf8')).hexdigest()
        self.assertEqual(img_url_lst[1][0]['md5'], md5)

    def test_extract_oss_info(self):
        oss_url = 'http://img.afanti100.com/data/image/question_image/23/04388533b6aa96fa9fee3c51420d1bf5.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1773048100&Signature=du5SxFitzxkb7uh7invCuSSSQiU%3D'
        info_dict = {}
        info_dict['source'] = '23'
        info_dict['md5'] = '04388533b6aa96fa9fee3c51420d1bf5'
        info_dict['ext'] = '.png'
        info_dict['accessKeyId'] = 'kI0OZGuxBI7ZmFAX'
        info_dict['expire'] = '1773048100'
        info_dict['signature'] = 'du5SxFitzxkb7uh7invCuSSSQiU%3D'
        info = extract_oss_info(oss_url)
        self.assertEqual(info, info_dict)



class TestOri2oss(unittest.TestCase):
    def test_oss(self):
        md5 = '2dad6f29ef14962788d9c35192b1766e.png'
        source = 23
        uri2oss = Uri2oss()
        oss_url = uri2oss.convert(md5, source)
        self.assertEqual(requests.get(oss_url).status_code, 200)

if __name__ == '__main__':
    unittest.main()
