#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals, absolute_import
import sys
from bs4 import BeautifulSoup
from pkg_resources import require

'''
某些环境下bs与lxml不能正常工作(如'A'会变为‘’)，这个脚本可以检测是否能正常工作
'''

print '#' * 60
print '> python version: ', sys.version.replace('\n', '')
print '> BeautifulSoup version: ', require('beautifulsoup4')[0].version
print '> lxml version: ', require('lxml')[0].version
print '> html5lib version: ', require('html5lib')[0].version
print '#' * 60

bad_flag = False

print '>' * 30
print '>>lxml'
for html in ['A', '啊']:
    print 'source_html:', html
    soup = BeautifulSoup(html, 'lxml')
    print 'soup:', soup
    print 'result is True:\t', soup.text == html
    if soup.text != html:
        bad_flag = True
    print '-' * 20

print '>' * 30
print '>>html5lib'
for html in ['A', '啊']:
    print 'source_html:', html
    soup = BeautifulSoup(html, 'html5lib')
    print 'soup:', soup
    print 'result is True:\t', soup.text == html
    if soup.text != html:
        bad_flag = True
    print '-' * 20


if bad_flag:
    print '>>> result: canot work correctly'
else:
    print '>>> result: ok'
