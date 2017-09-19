#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals, absolute_import
import unittest

from afanti_tiku_lib.utils import get_question_meta_data


class TestQuestionMetaData(unittest.TestCase):
    def test_del_nouse_text(self):
        html = '<p>(满分15分)观察下图，回答下列问题'
        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html.replace('(满分15分)', ''))

        html = '<p>(共15分)观察下图，回答下列问题'
        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html.replace('(共15分)', ''))

        html = '<p>(本题共15分)观察下图，回答下列问题'
        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html.replace('(本题共15分)', ''))

        html = '<p>（本小题15分）观察下图，回答下列问题'

        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html.replace('（本小题15分）', ''))

        html = '<p>(2015-安徽-13分)观察下图，回答下列问题'
        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html.replace('13分', ''))

        html = '<p>2015-安徽-13分 观察下图，回答下列问题'
        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html)

        html = '<p>（☆☆☆★）观察下图，回答下列问题'
        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html.replace('（☆☆☆★）', ''))

        html = '已知1分钟等于６０秒钟，回答下列问题'
        cleaned_html = get_question_meta_data.del_nouse_text(html)
        self.assertEqual(cleaned_html, html)

    def test_meta_data_valid(self):
        text = '（山东）'
        valid = get_question_meta_data.test_meta_valid(text)
        self.assertFalse(valid)

        text = '（北京时间）'
        valid = get_question_meta_data.test_meta_valid(text)
        self.assertFalse(valid)

        text = '(2016-安徽)'
        valid = get_question_meta_data.test_meta_valid(text)
        self.assertTrue(valid)

        text = '(2015黑龙江鹤岗一中联考,★★☆)'
        valid = get_question_meta_data.test_meta_valid(text)
        self.assertTrue(valid)

        text = '(2014浙江金华十校联考,7)'
        valid = get_question_meta_data.test_meta_valid(text)
        self.assertTrue(valid)

        text = '孙中山孙中山（1866年—1925年）'
        valid = get_question_meta_data.test_meta_valid(text)
        self.assertFalse(valid)

    def test_get_city_from_text(self):
        text = '2015北京'
        status, province = get_question_meta_data.get_city_from_text(text)
        self.assertEqual(province, '北京')

        text = '2016山东青岛'
        status, province = get_question_meta_data.get_city_from_text(text)
        self.assertEqual(province, '山东')

        text = '山东省青岛市'
        status, province = get_question_meta_data.get_city_from_text(text)
        self.assertEqual(province, '山东')

        text = '孙中山'
        # 孙中山不是地名，但是出现了中山，所以会被当做地名,
        status, province = get_question_meta_data.get_city_from_text(text)
        self.assertTrue(status)

    def test_get_year_from_text(self):
        text = '2016山东'
        status, year = get_question_meta_data.get_year_from_text(text)
        self.assertEqual(year, '2016')

        text = '2015山西,7,2分'
        status, year = get_question_meta_data.get_year_from_text(text)
        self.assertEqual(year, '2015')

        text = '山西-19分'
        status, year = get_question_meta_data.get_year_from_text(text)
        self.assertFalse(status)

    def test_get_question_meta_from_text(self):
        old_html = '<p>(2011广东理综,35,18分)如图(a)所示,在'
        html, meta_data = get_question_meta_data.get_question_meta_info(old_html)
        self.assertEqual(html, old_html.replace('(2011广东理综,35,18分)', ''))
        self.assertNotEqual(meta_data['province'], None)
        self.assertEqual(meta_data['year'], '2011')
        self.assertEqual(meta_data['province'], '广东理综')

        old_html = '<p>(2011广东理综T15,35,18分, 多选，★★☆)如图(a)所示,在'
        html, meta_data = get_question_meta_data.get_question_meta_info(old_html)
        self.assertEqual(html, old_html.replace('(2011广东理综T15,35,18分, 多选，★★☆)', ''))
        self.assertNotEqual(meta_data['province'], None)
        self.assertEqual(meta_data['year'], '2011')
        self.assertEqual(meta_data['province'], '广东理综')

        old_html = '<p>(2013河北秦皇岛一模,43)—______were you'
        html, meta_data = get_question_meta_data.get_question_meta_info(old_html)
        self.assertEqual(html, old_html.replace('(2013河北秦皇岛一模,43)', ''))
        self.assertNotEqual(meta_data['province'], None)
        self.assertEqual(meta_data['year'], '2013')
        self.assertEqual(meta_data['province'], '河北秦皇岛一模')

        old_html = '<p>[2014广州海珠一模,41(2)(3)]阅读图文'
        html, meta_data = get_question_meta_data.get_question_meta_info(old_html)
        self.assertEqual(html, old_html.replace('[2014广州海珠一模,41(2)(3)]', ''))
        self.assertNotEqual(meta_data['province'], None)
        self.assertEqual(meta_data['year'], '2014')
        self.assertEqual(meta_data['province'], '广州海珠一模')

        old_html = '<p>(2015江苏宿迁剑桥国际学校月考,8,2分)对水稻→鼠→蛇→鹰这条食物链的错误描述是(　　)</p>p><p>A.水稻是生产者　　B.鼠是初级消费者　　C.蛇是次级消费者　　D.鹰属于第三营养级</p>p>'
        html, meta_data = get_question_meta_data.get_question_meta_info(old_html)
        self.assertEqual(html, old_html.replace('(2015江苏宿迁剑桥国际学校月考,8,2分)', ''))
        self.assertNotEqual(meta_data['province'], None)
        self.assertEqual(meta_data['year'], '2015')
        self.assertEqual(meta_data['province'], '江苏宿迁剑桥国际学校月考')

        old_html = ' <p>(2015山东聊城文轩中学月考,7,★★☆)如图6-4-7,在△ABC中,D、E分别是BC、AC的中点,'
        html, meta_data = get_question_meta_data.get_question_meta_info(old_html)
        self.assertEqual(html, old_html.replace('(2015山东聊城文轩中学月考,7,★★☆)', ''))
        self.assertNotEqual(meta_data['province'], None)
        self.assertEqual(meta_data['year'], '2015')
        self.assertEqual(meta_data['province'], '山东聊城文轩中学月考')

        old_html = '<p>关于电影的说法与事实吻合的是(　　)</p>p><p>A.电影诞生于20世纪初</p>p><p>B.它与新古典主义美术产生的背景相同</p>p><p>C.它是一种全新的艺术和流行很广的娱乐形式</p>p><p>D.它被称为“第八艺术”</p>p>'
        html, meta_data = get_question_meta_data.get_question_meta_info(old_html)
        self.assertEqual(html, old_html)
        self.assertEqual(meta_data['province'], None)



if __name__ == '__main__':
    unittest.main()
