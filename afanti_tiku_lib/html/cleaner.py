# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from collections import deque

import re

from afanti_tiku_lib.compat import compat_html_parser
from afanti_tiku_lib.compat import compat_html_entities

HTMLParser = compat_html_parser.HTMLParser

'''
从一段HTML文本中筛选出符合规则的内容。
使用方法：


In [1]: from afanti_tiku_lib.html.cleaner import Cleaner

In [2]: invalid_tag_lst = [
   ...:     {'tag': 'div', 'attrs': {'class': 'guoyuan-container'}, 'remain_content': False},
   ...: ]

In [3]: # 或者
   ...: invalid_tag_lst = [
   ...:     {'tag': 'div', 'attrs': {'class': ['guoyuan-container', 'share']}, 'remain_content': False},
   ...: ]

In [4]: html = '<div class="answer">This is answer<div class="guoyuan-container share"><span>This is some unuseful text</span></div></div>'

In [8]: cleaner.feed(html)

In [9]: cleaner.get_html()
Out[9]: u'<div class="answer">This is answer</div>'

'''


NOEND_TAG_LST = (
    'br', 'hr', 'img', 'input', 'base', 'link', 'meta', 'area'
)

BANNED_TAG_LST = (
    {'tag': 'a', 'remain_content': False},
    {'tag': 'scipt', 'remain_content': False},
    {'tag': 'style', 'remain_content': False},
    {'tag': 'iframe', 'remain_content': False},
    {'tag': 'input', 'remain_content': False},
    {'tag': 'button', 'remain_content': False},
    {'tag': 'head', 'remain_content': False},
    {'tag': 'meta', 'remain_content': False},
    {'tag': 'input', 'remain_content': False},
    {'tag': 'base', 'remain_content': False},
)

ALLOWED_ATTRS_LST = (
    {
        'tag': '*',
        'attrs': {
            'style': '*',
            'hidden': '*',
            'class': '*',
            'id': '*'
        }
    }, {
        'tag': 'img',
        'attrs': {
            'style': '*',
            'class': '*',
            'id': '*',
            'width': '*',
            'height': '*',
            'align': '*',
            'src': '*',
            'alt': '阿凡题'
        }
    }
)

allowed_attr_dict = {
    'img': ['class', 'id', 'width', 'height', 'align', 'src', 'style']
}

allowed_attr_lst = ['style', 'hidden', 'class', 'id']


class TagDict(object):
    def __init__(self, tag=None, attrs=None, remain_contents=True):
        self._tag = tag
        self._attrs = attrs
        self._remain_contents = remain_contents

    @property
    def tag(self):
        return self._tag

    @property
    def remain_contents(self):
        return self._remain_contents

    @property
    def attrs(self):
        return self._attrs


class TagHandler(object):
    def __init__(self, attrs_lst=ALLOWED_ATTRS_LST,
                 invalid_tag_lst=None,
                 unallowed_tag_attr_lst=BANNED_TAG_LST):
        self.attrs_dict = self.__format_tag_dict(attrs_lst)
        self.invalid_tag_dict = self.__format_tag_dict(invalid_tag_lst)
        self.unallowed_tag_attr_dict = self.__format_tag_dict(
            unallowed_tag_attr_lst)

    def __format_tag_dict(self, lst):
        res_dict = {}
        if not lst:
            return res_dict
        for item in lst:
            tag = item.get('tag')
            if not tag:
                raise Exception('invalid tag name %s for TagHandler!' % tag)
            attrs = item.get('attrs', [])
            remain_contents = item.get('remain_content', False)
            tag_dict = TagDict(tag, attrs, remain_contents)
            res_dict[tag] = tag_dict
        return res_dict

    def need_decompose(self, tag, attrs):
        for tag_dict in [self.invalid_tag_dict, self.unallowed_tag_attr_dict]:
            if tag in tag_dict:
                target_tag = tag_dict[tag]
                if not target_tag.attrs:
                    return True, target_tag.remain_contents
                for key, value in attrs:
                    if key in target_tag.attrs:
                        invalid_attr_value = target_tag.attrs[key]
                        if not isinstance(invalid_attr_value, list):
                            invalid_attr_value = [target_tag.attrs[key]]
                        for invalid_value in invalid_attr_value:
                            if invalid_value in value:
                                return True, target_tag.remain_contents
        return False, True

    def filter_attrs(self, tag, attrs):
        if not attrs:
            return attrs
        if tag in self.attrs_dict:
            target_tag = self.attrs_dict[tag]
        elif '*' in self.attrs_dict:
            target_tag = self.attrs_dict['*']
        else:
            return attrs
        res_lst = []
        for key, value in attrs:
            if key in target_tag.attrs:
                if target_tag.attrs[key] != '*':
                    value = target_tag.attrs[key]
                if tag == 'img' and key == 'alt':
                    value = '阿凡题'
                res_lst.append((key, value))
        return res_lst

    def generate_html(self, tag, attrs):
        if attrs:
            attrs = self.filter_attrs(tag, attrs)
            html = '<{tag} {attrs} >'.format(
                tag=tag,
                attrs=' '.join(
                    ['%s="%s"' % (key, value) for key, value in attrs]
                )
            )
        else:
            html = '<{tag} >'.format(tag=tag)
        if tag in NOEND_TAG_LST:
            html = re.sub(' >$', '/>', html)
        else:
            html = re.sub(' >$', '>', html)
        return html


class Cleaner(HTMLParser):
    '''
    delete tag like a, input, link
    delete attrs like alt
    '''
    def __init__(self, attr_lst=ALLOWED_ATTRS_LST,
                 invalid_tag_lst=None,
                 unallowed_tag_attr_lst=BANNED_TAG_LST):
        HTMLParser.__init__(self)
        self.tag_handler = TagHandler(
            attr_lst, invalid_tag_lst, unallowed_tag_attr_lst)
        self.tmp_html = ''
        self.pure_text = ''
        self.tag_stack = deque()
        self.remain_contents_stack = deque()

    @property
    def remain_data_flag(self):
        return self.remain_contents_stack.count(False) < 1

    def handle_starttag(self, tag, attrs):
        if tag in NOEND_TAG_LST:
            self.handle_startendtag(tag, attrs)
            return
        need_decompose, remain_tag_contents = \
            self.tag_handler.need_decompose(tag, attrs)
        self.remain_contents_stack.append(remain_tag_contents)
        if need_decompose:
            self.tag_stack.append((tag, 'bad'))
            return
        else:
            self.tag_stack.append((tag, 'ok'))
        if not self.remain_data_flag:
            return
        tmp_html = self.tag_handler.generate_html(tag, attrs)
        self.tmp_html += tmp_html

    def handle_data(self, data):
        if not self.remain_data_flag:
            return
        self.tmp_html += data
        self.pure_text += data

    def handle_endtag(self, tag):
        tag_popped = self.tag_stack.pop()
        if tag != tag_popped[0]:
            raise Exception('unclosed tag: %s' % tag_popped[0])
        if not self.remain_data_flag:
            self.remain_contents_stack.pop()
            return
        if tag_popped[1] == 'bad':
            return
        self.remain_contents_stack.pop()
        tmp_html = '</%s>' % tag
        self.tmp_html += tmp_html

    def handle_entityref(self, data):
        if not self.remain_data_flag:
            return
        if self.remain_contents_stack:
            if self.remain_contents_stack.count(False) % 2 == 1:
                return
        self.tmp_html += '&%s;' % data
        data = unescape('&%s;' % data)
        self.pure_text += data

    def handle_charref(self, data):
        if not self.remain_data_flag:
            return
        if self.remain_contents_stack:
            if self.remain_contents_stack.count(False) % 2 == 1:
                return
        self.tmp_html += '&#%s;' % data
        data = unescape('&#%s;' % data)
        self.pure_text += data

    def handle_startendtag(self, tag, attrs):
        need_decompose, remain_tag_contents = \
            self.tag_handler.need_decompose(tag, attrs)
        if need_decompose:
            return
        if not self.remain_data_flag:
            return
        tmp_html = self.tag_handler.generate_html(tag, attrs)
        self.tmp_html += tmp_html

    def get_html(self):
        tmp_html, self.tmp_html = self.tmp_html, ''
        return tmp_html

    def get_pure_text(self):
        pure_text, self.pure_text = self.pure_text, ''
        return pure_text

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(compat_html_entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)

