# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

try:
    import configparser as compat_configparser
except ImportError: # Python 2
    import ConfigParser as compat_configparser

try:
    import pickle as compat_pickle
except ImportError: # Python 2
    import cPickle as compat_pickle

try:
    import html.parser as compat_html_parser
except ImportError: # Python 2
    import HTMLParser as compat_html_parser

try:
    from html import unescape as compat_html_unescape
except ImportError: # Python 2
    from HTMLParser import HTMLParser
    compat_html_unescape = HTMLParser()

try:
    import html.escape as compat_html_escape
except ImportError: # Python 2
    from cgi import escape as compat_html_escape

try:
    import html.entities as compat_html_entities
except ImportError: # Python 2
    import htmlentitydefs as compat_html_entities

try:
    import urllib.parse as compat_urllib_parse
except ImportError:  # Python 2
    import urllib
    import urlparse
    class compat_urllib_parse(object):
        pass

    for attr in dir(urllib):
        if not attr.startswith('_'):
            setattr(compat_urllib_parse, attr, staticmethod(getattr(urllib, attr)))

    for attr in dir(urlparse):
        if not attr.startswith('_'):
            setattr(compat_urllib_parse, attr, staticmethod(getattr(urlparse, attr)))


try:
    from urllib.parse import urlparse as compat_urllib_parse_urlparse
except ImportError:  # Python 2
    from urlparse import urlparse as compat_urllib_parse_urlparse

try:
    import queue as compat_queue
except ImportError:  # Python 2
    import Queue as compat_queue

import base64 as compat_base64
if not hasattr(compat_base64, 'encodebytes'):
    setattr(compat_base64, 'encodebytes', compat_base64.encodestring)

if str == bytes:
    compat_bytes = bytearray
else:
    compat_bytes = bytes

try:
    compat_str = unicode  # Python 2
except NameError:
    compat_str = str

try:
    import MySQLdb as compat_mysql
except ImportError:  # Python 2
    pass

try:
    import cymysql as compat_mysql
except ImportError:  # Python 3, not install cymysql
    pass

try:
    import pymysql as compat_mysql
except ImportError:  # Python 3, not install cymysql
    pass

try:
    from itertools import zip_longest as compat_zip_longest
except ImportError:  # Python 2
    from itertools import izip_longest as compat_zip_longest

try:
    from os import getcwdu as compat_getcwd
except ImportError:  # Python 3
    from os import getcwd as compat_getcwd
