#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals, absolute_import
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import unittest
import hashlib

from afanti_tiku_lib.utils import get_pure_text_md5
from afanti_tiku_lib.utils import get_pure_text


class TestMD5(unittest.TestCase):
    def _test_single_parser(self, html='', pure_text='', parser='bs.lxml'):
        pure_text_result = get_pure_text(html, False, filter_symbol_flag=False, parser=parser)
        self.assertEqual(pure_text_result, pure_text)
        md5 = hashlib.md5(pure_text.encode('utf8')).hexdigest()
        self.assertEqual(get_pure_text_md5(html), md5)

    def _get_html_lst(self):
        html_lst = []

        html = '这是一道题目,<img src="a.png" alt="这是一张图片">   &nbsp;&nbsp; &amp;'
        pure_text = '这是一道题目, &'
        html_lst.append((html, pure_text))

        html = 'A'
        pure_text = 'A'
        html_lst.append((html, pure_text))

        html = '.'
        pure_text = '.'
        html_lst.append((html, pure_text))

        html = 'http://www.afanti100.com'
        pure_text = 'http://www.afanti100.com'
        html_lst.append((html, pure_text))

        html = '<table>&nbsp;<tr><td>ABCD</td></tr><tr><td>EFGH</td></tr></table>'
        pure_text = ' ABCD EFGH'
        html_lst.append((html, pure_text))

        html = '''<p>判断题:&nbsp;</p><ol class=" list-paddingleft-2" style="list-style-type: decimal;"><li><p>正负数统称为有理数。</p></li><li><p>非负数就是正数，非正数就是负数。</p></li></ol>'''
        pure_text = '''判断题: 正负数统称为有理数. 非负数就是正数,非正数就是负数.'''
        html_lst.append((html, pure_text))

        html = '''用十二点五六厘米长的铁丝分别围城长方形正方形和圆,面积最小的是正方形判断题'''
        pure_text = '''用十二点五六厘米长的铁丝分别围城长方形正方形和圆,面积最小的是正方形判断题'''
        html_lst.append((html, pure_text))

        html = '''<span class="qseq"></span><p>伊斯兰教是世界上信徒最多和流传最广的宗教．</p><label class="underline"></label>（判断对错）'''
        pure_text = '''伊斯兰教是世界上信徒最多和流传最广的宗教. (判断对错)'''
        html_lst.append((html, pure_text))

        html = '.'
        pure_text = '.'
        html_lst.append((html, pure_text))

        html = '.'
        pure_text = '.'
        html_lst.append((html, pure_text))

        html = '.'
        pure_text = '.'
        html_lst.append((html, pure_text))
        return html_lst

    def test_bs_lxml(self):
        html_lst = self._get_html_lst()
        parser = 'bs.lxml'
        for html, pure_text in html_lst:
            self._test_single_parser(html, pure_text, parser=parser)

    def test_bs_html5lib(self):
        html_lst = self._get_html_lst()
        parser = 'bs.html5lib'
        for html, pure_text in html_lst:
            self._test_single_parser(html, pure_text, parser=parser)


    def test_htmlparser(self):
        html_lst = self._get_html_lst()
        parser = 'htmlparser'
        for html, pure_text in html_lst:
            self._test_single_parser(html, pure_text, parser=parser)


if __name__ == '__main__':
    unittest.main()
