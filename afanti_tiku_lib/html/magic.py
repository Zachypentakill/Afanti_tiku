# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os

import afanti_tiku_lib
from afanti_tiku_lib.url.uri2oss import Uri2oss
from afanti_tiku_lib.html.beautify_html import beautify_html
from afanti_tiku_lib.html.image_magic import ImageMagic

DEFAULT_IMG_EXT = '.png'
MYSQL_DEFAULT_DB = 'question_db_offline'
DEFAULT_CONFIG_FILE = 'config'


class HtmlMagic(object):

    def __init__(self, spider_source,
                 download=True,
                 archive_image=True,
                 headers=None,
                 proxy=False,
                 beautify=False,
                 img_ext=DEFAULT_IMG_EXT,
                 mysql_db=None,
                 config_file=None,
                 exclude_md5s=None,
                 priority=False):

        self.img_ext = img_ext
        self.spider_source = spider_source
        self.beautify = beautify
        self.download = download
        self.archive_image = archive_image
        self.proxy = proxy
        self.headers = headers
        self.priority = priority
        self.mysql_db = (mysql_db or MYSQL_DEFAULT_DB)

        if config_file is None:
            top_dir = os.path.dirname(afanti_tiku_lib.__file__)
            config_file = os.path.join(top_dir, DEFAULT_CONFIG_FILE)
        else:
            config_file = config_file
        self.image_magic = ImageMagic(Uri2oss(),
                                      download=self.download,
                                      archive_image=self.archive_image,
                                      proxy=self.proxy,
                                      mysql_db=self.mysql_db,
                                      img_ext=self.img_ext,
                                      config_file=config_file,
                                      exclude_md5s=exclude_md5s,
                                      priority=self.priority)

    def bewitch(self, html_string,
                spider_url,
                spider_source=0,
                download=None,
                redownload=False,
                archive_image=None,
                headers=None,
                proxy=None,
                img_ext=None,
                beautify=None,
                mysql_db=None,
                priority=None):

        img_ext = (img_ext or self.img_ext)
        spider_source = (spider_source or self.spider_source)
        beautify = (beautify, self.beautify)[beautify is None]
        download = (download, self.download)[download is None]
        archive_image = (archive_image, self.archive_image)[archive_image is None]
        proxy = (proxy or self.proxy)
        headers = (headers or self.headers)
        mysql_db = (mysql_db or self.mysql_db)
        priority = (priority or self.priority)

        html_string = self.image_magic.bewitch(html_string,
                                               spider_url,
                                               spider_source=spider_source,
                                               download=download,
                                               redownload=redownload,
                                               archive_image=archive_image,
                                               headers=headers,
                                               proxy=proxy,
                                               img_ext=img_ext,
                                               priority=priority)

        if beautify:
            html_string = beautify_html(html_string)
        return html_string

