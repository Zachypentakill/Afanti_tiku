# -*- coding:utf8 -*-
from __future__ import unicode_literals, absolute_import
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re

import unittest

from afanti_tiku_lib.html.cleaner import Cleaner


class TestHTMLCleaner(unittest.TestCase):
    def test_del_tag(self):

        bad_html = '''
            <div class="wifi-auto-answer-2">
                <div class="main-body">
                    <div class="special-style">
                        <p>已知，如图，在<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/87e69dcd60154930b225f824f92b3d27.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=szg86VvgGPzM%2BllIW3KWGnBNc%2BU%3D"
                        />中，<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/65a95228f84895f965c5c0f75a88abf9.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=RuCs6XAfvg%2BINaLhln0UJUKW7qI%3D"
                        />，边AC的垂直平分线DE与AC、AB分别交于点D和点E。<br/></p>
                        <p><img alt="blob.png" src="http://img.afanti100.com/data/image/question_image/64/8b2fbe66dc0b9aea16e0b40ab666ce99.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=7AN5NbmM5up7Bc5oKH6JAtFo%2B44%3D"
                        title=".jpg" /></p>
                        <p>（1）作出边AC的垂直平分线DE；</p>
                        <p>（2）当<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/a6c3a6fb8695fb96b325f8aa4de6cead.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=HhLszvduXbpohL8CvTeiFSBHJV0%3D"
                        />时，求<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/d8c140b7e562e7a3be8cd9f8655315a7.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=CgmNtnfeMqkZJio6pJ7mdpMNrWg%3D"
                        />的度数。</p>
                    <div class="guoyuan-container share"><span>广告文本</span><a href="baidu.com"></a>广告文本</div>
                    <div class="share knowledge">无用文本</div>
                </div>
            </div>
        </div>
        '''

        correct_html = '''
            <div class="wifi-auto-answer-2">
                <div class="main-body">
                    <div class="special-style">
                        <p>已知，如图，在<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/87e69dcd60154930b225f824f92b3d27.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=szg86VvgGPzM%2BllIW3KWGnBNc%2BU%3D"
                        />中，<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/65a95228f84895f965c5c0f75a88abf9.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=RuCs6XAfvg%2BINaLhln0UJUKW7qI%3D"
                       />，边AC的垂直平分线DE与AC、AB分别交于点D和点E。<br/></p>
                        <p><img alt="blob.png" src="http://img.afanti100.com/data/image/question_image/64/8b2fbe66dc0b9aea16e0b40ab666ce99.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=7AN5NbmM5up7Bc5oKH6JAtFo%2B44%3D"
                        title=".jpg" /></p>
                        <p>（1）作出边AC的垂直平分线DE；</p>
                        <p>（2）当<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/a6c3a6fb8695fb96b325f8aa4de6cead.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=HhLszvduXbpohL8CvTeiFSBHJV0%3D"
                            />时，求<img class="kfformula" src="http://img.afanti100.com/data/image/question_image/64/d8c140b7e562e7a3be8cd9f8655315a7.png?OSSAccessKeyId=kI0OZGuxBI7ZmFAX&Expires=1792723341&Signature=CgmNtnfeMqkZJio6pJ7mdpMNrWg%3D"
                        />的度数。</p>
                    </div>
                </div>
            </div>
        '''

        invalid_tag_lst = [
            {'tag': 'div', 'attrs': {'class': ['guoyuan-container', 'share']}, 'remain_content': False},
        ]

        cleaner = Cleaner(invalid_tag_lst=invalid_tag_lst)
        cleaner.feed(bad_html)
        self.assertEqual(
            re.sub('\s', '', correct_html),
            re.sub('\s', '', cleaner.get_html())
        )


if __name__ == '__main__':
    unittest.main()
