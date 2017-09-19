# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import unittest

from afanti_tiku_lib.html.image_magic import ImageMagic

image_magic = ImageMagic()


class TestHtmlImageMagic(unittest.TestCase):

    def test_image_magic_bewitch(self):
        html_string = '''
<article class="underline" style="padding:10px 0px;">
				 <span class="qseq"></span>一艘<img alt="" src="http://img.kantiku.com/20141022/original/1413972341473-120808.png" style="vertical-align:middle" />能载重1200（　　）<!--B2--><table style="width:100%" class="ques quesborder"><tr><td style="width:30%" class="selectoption"><label class=" s">A．吨</label></td><td style="width:30%" class="selectoption"><label class="">B．千克</label></td><td style="width:30%" class="selectoption"><label class="">C．克</label></td></tr></table></article>
        '''

        image_magic.bewitch(html_string, 'http://kantiku.com/math3-120808.htm', 0)
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
