# encoding: utf-8
from __future__ import unicode_literals


from bs4 import BeautifulSoup

def convert_jyeoo_option(option_html):
    '''
    将Jy的选项由原始的静态格式替换为响应式布局的代码
    ps: 原始格式的选项会被包裹在//td[@class="selectoption"]标签中
    '''
    soup = BeautifulSoup(option_html, u'lxml')
    option_lst = soup.find_all(u'td', class_ = u'selectoption')
    for option in option_lst:
        option[u'class'] = u'aft_option'
        del option[u'style']

    html_template = u'<table style="width: 100%;"  class="aft_option_wrapper"><tbody class="measureRoot"></tbody></table>'
    option_table = BeautifulSoup(html_template, u'lxml')
    for option in option_lst:
        option_with_tr = BeautifulSoup(u'<tr></tr>', u'lxml')
        option_with_tr.tr.append(option)
        option_table.table.tbody.append(option_with_tr.tr)

    return unicode(option_table.table)

