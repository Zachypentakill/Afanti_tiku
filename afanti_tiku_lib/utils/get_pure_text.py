# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re

from afanti_tiku_lib.compat import compat_html_parser
from afanti_tiku_lib.compat import compat_html_entities
from afanti_tiku_lib.utils.punctuation import punctuation_dict

from bs4 import BeautifulSoup

HTMLParser = compat_html_parser.HTMLParser


def get_pure_text(html, del_stopwords_flag=False,
                  filter_symbol_flag=False, parser='htmlparser'):
    '''获取一段html的纯文本
    !!!目前僅有htmlparser可以完成去重功能，lxml與html5lib不能通過測試用例
    '''
    def filter_symbol(text):
        '''删除特殊符号'''
       ## text = text.lower()

        # 原有的代码出于检索切词等原因，不能完全去除文本中的符号，所以改写如下。
        # u'-'  u'－' 中英文减号，不能按照标点处理
        english_str = u':;.,?!_()[]\'"\/{}'
        # chinese_str = u'：；，．。？！（）【】‘’“”、╗╚┐└…《》〈 〉·﹕｛｝'
        chinese_str = u'【】‘’“”、╗╚┐└…《》〈 〉·﹕｛｝'
        symbol_str = chinese_str + english_str
        for symbol in symbol_str:
            text = text.replace(symbol, '')
        text = text.replace(u'——', '')
        text = re.sub(r'\u200B', '', text, flags=re.U)
        text = re.sub(r'\uFEFF', '', text, flags=re.U)
        text = re.sub(r'\uE004', '', text, flags=re.U)
        text = re.sub(r'\uE003', '', text, flags=re.U)
#        text = re.sub(r'\u127539', '', text, flags=re.U)

        #英文的文本去掉所有 -  字符
#        pattern = re.compile(r'[-a-z]')
#        _text=re.sub(pattern, '', text)
#        if _text == '':
#            text=re.sub(r'-','',text)
        return text

    def unified_punctuation(text):
        for k, v in punctuation_dict.items():
            text = text.replace(k, v)
        return text

    def del_stopwords(text):
        '''删除一些停用词'''
        cn_stopword = ["的", "了", "在", "是", "我", "有", "和", "就",
                       "不", "人", "都", "一", "一个", "上", "也", "很",
                       "到", "说", "要", "去", "你", "会", "着", "没有",
                       "看", "好", "自己", "这"]
        for word in cn_stopword:
            text = text.replace(word, '')
        return text

    def get_pure_text(html, parser):
        '''提取html中的纯文本'''
        if len(html) == 1:  # 需要处理特殊的html，如'.', 'A'
            return html
        if parser.startswith('bs.'):
            if parser == 'bs.lxml':
                soup = BeautifulSoup(html, 'lxml')  # 将解析器换为html5lib
                # 解析器lxml在某些环境下(缺少 libxml2 and libxslt.)不能正常
                # 处理'A'这样的字符串, 而html5lib可以正常工作
                # 更新：20160414 html5lib不能正确处理<table>&nbsp;<tr><td>
                # asdsa</td></td></table> 这种字符串
                return ' '.join(soup.stripped_strings)
            elif parser == 'bs.html5lib':

                soup = BeautifulSoup(html, 'html5lib')
                return ' '.join(soup.stripped_strings)
            else:
                raise Execption('undefine parser')
        elif parser == 'htmlparser':
            my_parser = MyHTMLParser()
            # incomplete data is buffered until more data is fed or close() is called
            my_parser.feed(html)
            my_parser.close()
            word_lst = my_parser.get_data()
            return ' '.join(word_lst)
        else:
            raise Exception('undefine parser')

    if parser is not None:
        pure_text = get_pure_text(html, parser)

    else:
        pure_text = html

#    pure_text = re.sub(r'&#127539;', '', pure_text, flags=re.U)
    pure_text = re.sub(r'\s+', ' ', pure_text, flags=re.U)
    pure_text = re.sub(r'_+', '_', pure_text, flags=re.U)
    pure_text = unified_punctuation(pure_text)

    if filter_symbol_flag:
        pure_text = filter_symbol(pure_text)
    if del_stopwords_flag:
        pure_text = del_stopwords(pure_text)
    return pure_text


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data_lst = []
        self.tmp_data = ''

    def handle_starttag(self, tag, attrs):
        if self.tmp_data:
            self.data_lst.append(self.tmp_data)
            self.tmp_data = ''

    def handle_data(self, data):
        self.data_lst.append(data)

    def handleendtag(self, tag):
        if self.tmp_data:
            self.data_lst.append(self.tmp_data)
            self.tmp_data = ''

    def handle_entityref(self, data):
        data = unescape('&%s;' % data)
        self.tmp_data += data

    def handle_charref(self, data):
        data = unescape('&#%s;' % data)
        self.tmp_data += data

    def handle_startendtag(self, tag, attrs):
        if self.tmp_data:
            self.data_lst.append(self.tmp_data)
            self.tmp_data = ''

    def get_data(self):
        if self.tmp_data:
            self.data_lst.append(self.tmp_data)
        data_lst = self.data_lst
        self.tmp_data = ''
        return data_lst


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


# 使用html5lib的一些问题
'''
In [38]: data = '<table>&nbsp;<tr><td>asda</td>td></tr>tr></table>table>'

In [39]: soup = BeautifulSoup(data, 'html5lib')

In [40]: soup
Out[40]: <html><head></head>head><body><table><tbody><tr><td>asda</td>td></tr>
tr></tbody>tbody></table>table>\xa0</body>body></html>html>

In [41]: soup.text
Out[41]: u'\xa0'

In [42]: soup.td

In [43]: soup = BeautifulSoup('<html><head></head>head><body><table><tbody><tr>
<td>asda</td>td></tr>tr></tbody>tbody></table>table>\xa0</body>body></html>
html>', 'html5lib')

In [44]: soup
Out[44]: <html><head></head>head><body><table><tbody><tr><td>asda</td>td></tr>
tr></tbody>tbody></table>table>\xa0</body>body></html>html>

In [45]: soup.text
Out[45]: u'asda\xa0'

In [46]: soup.td
Out[46]: <td>asda</td>td>
'''
