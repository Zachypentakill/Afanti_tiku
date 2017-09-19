# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from afanti_tiku_lib.compat import compat_html_parser
from collections import deque

#上线前测试
#1.标签的测试
#2.图片的检测
#3.pure_text的检测


#自定义异常
class QuestionError(Exception):
    pass

#标签错误
class QuestionTagError(Exception):
    pass

#图片问题
class QuestionImgError(Exception):
    pass

#题目文本错误
class QuestionTextError(Exception):
    pass


class BadHTMLDetecor(compat_html_parser.HTMLParser):

    allow_tags = [
        'div', 'span', 'br', 'p', 'hr', 'u', 'section'
        'table', 'tbody', 'caption', 'tr', 'th', 'thead', 'td',
        'ul', 'ol', 'li',
        'img', 'br', 'i', 'u',
        'p', 'div', 'em',
        'u', 'embed',
        'big', 'small'
        'sup', 'sub'
    ]
    not_allowed_tags = [
        'html', 'body', 'head',
        'a', 'b', 'strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'applet', 'script', 'style',
        'audio', 'blockquote', 'button',
        'iframe', 'input', 'video', 'wbr'
    ]
    common_attrs = ['style', 'class', 'name', 'id']
    not_allowed_attrs = ['']
    noend_tags = [
        'area', 'base', 'col', 'command', 'embed', 'keygen',
        'param', 'source', 'track', 'wbr',
        'br', 'hr', 'img', 'input', 'link', 'meta'
    ]

    def __init__(self):
        super(BadHTMLDetecor, self).__init__()
        self.warning_lst = []
        self.tag = None
        self.tag_stack = deque()
        self.bad_tag_lst = []

    def __add_warning(self, err_info):
        self.warning_lst.append(err_info)

    def result(self):
        if len(self.tag_stack) > 0:
            self.bad_tag_lst += list(self.tag_stack)
        return self.bad_tag_lst

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_starttag(self, tag, attrs):
        if tag in self.noend_tags:
            return
        self.tag_stack.append(tag)
        attr_dict = {}
        for attr in attrs:
            attr_dict[attr[0]] = attr[1]
        self._detect_attr(tag, attr_dict)

    def handle_endtag(self, tag):
        try:
            self.tag_stack.pop()
        except IndexError:
            # end tag without begin tag
            self.bad_tag_lst.append(tag)

    def handle_data(self, data):
        self.tag = None

    def _detect_attr(self, tag, attr_dict):
        # if 'style' in attr_dict:
            # pass

        if 'bgcolor' in attr_dict:
            self.__add_warning('unexpected attritebute found: bgcolor')

        if tag == 'table':
            if 'width' in attr_dict:
                width_value = attr_dict['width']
                if not (width_value and re.match('\d+%', width_value)):
                    self.__add_warning('bad width value:%s found in table attribute' % width_value)
        elif tag == 'img':
            if  'alt' in attr_dict:
                alt_value = attr_dict['alt']
                if alt_value != '阿凡题':
                    self.__add_warning('bad img alt value:%s found in img tag' % alt_value)

    # not need to instantiate new instance
    def clear(self):
        self.warning_lst.clear()
        self.tag = None
        self.tag_stack.clear()
        self.bad_tag_lst.clear()



def get_inline_css_dict(text):
    css_dict = {}
    text = text.strip()
    css_find = re.compile(r'([a-zA-Z-][^\t\n\r\x0c />\x00]*?[^;]*)(?=;|$)')
    for item in css_find.findall(text):
        if ':' in item:
            index = item.find(':')
            key = item[:index]
            value = item[index+1:]
            css_dict[key] = value
    return css_dict



if __name__ == '__main__':
    html = '</p><p><p></p><br/>'
    detector = BadHTMLDetecor()
    detector.feed(html)
    print('source html:', html)
    print('result:', detector.result())

    detector.clear()
    html = '''<span><div>有四种物质①金刚石　②白磷　③甲烷　④四氯化碳，其中分子具有正四面体构型的是（　　）    A．①②③<table> <tbody> <tr> <td> <span> </span> 有四种物质①金刚石　②白磷　③甲烷　④四氯化碳，其中分子具有正四面体构型的是（　　）<table style="width:100%"> <tbody> <tr> <td> A．①②③</td> <td> B．①③④</td> <td> C．②③④</td> <td> D．①②③④</td> </tr> </tbody> </table> </td> </tr> </tbody> </table></div>'''
    detector.feed(html)
    print('source html:', html)
    print('result:', detector.result())

