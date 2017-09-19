# -*- coding:utf8 -*-
import tidylib

# 使用tidy来清洗html，https://www.w3.org/People/Raggett/tidy/
# 现在tidy已经更新到5.2.0，http://www.html-tidy.org/

# 默认的参数
# 参数api见http://api.html-tidy.org/tidy/quickref_5.2.0.html
# 常见的参数：
# alt-text 为没有alt属性的标签添加对应的alt值
# doctype 设置html的版本
# drop-empty-elements 删除空标签
# drop-empty-paras 删除空段落
# preserve-entities 是否保留html entity
# force-output 强制输出结果，忽略出现的错误


options = {
            'doctype': 'html5',
            'drop-empty-paras': True,
            'drop-empty-elements': True,
            'preserve-entities': True,
            'quote-nbsp': True,
            'tidy-mark': False,

        }


def tidy_fragment(html):
    document, errors = tidylib.tidy_fragment(html, options=options)
    return document


def tidy_document(html):
    document, error = tidylib.tidy_document(html, options=options)
    return document
