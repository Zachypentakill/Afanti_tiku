# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os

import afanti_tiku_lib
from afanti_tiku_lib.compat import compat_str
from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.redis_proxy import RedisProxy
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.url.uri2oss import Uri2oss
from afanti_tiku_lib.url.extract_img_from_html import (
    extract_image_info_with_md5,
)

import threading


_lock = threading.Lock()

def _acquireLock():
    if _lock:
        _lock.acquire()

def _releaseLock():
    if _lock:
        _lock.release()


DEFAULT_IMG_EXT = '.png'
MYSQL_DEFAULT_DB = 'question_db_offline'
DEFAULT_CONFIG_FILE = 'config'


class ImageMagic(object):

    IMAGE_TABLE = 'image_archive'

    def __init__(self,
                 uri2oss=None,
                 mysql_db=None,
                 download=True,
                 archive_image=True,
                 proxy=False,
                 img_ext=DEFAULT_IMG_EXT,
                 config_file=None,
                 exclude_md5s=None,
                 priority=False):

        self.download = download
        self.archive_image = archive_image
        self.img_ext = img_ext
        self.exclude_md5s = set()  # md5 in which exclude_md5s will not be downloaded
        self.proxy = proxy
        self.priority = priority

        # Strongly recommand to set uri2oss
        # ignoring reloading oss configure file
        self.uri2oss = (uri2oss or Uri2oss())

        if config_file is None:
            top_dir = os.path.dirname(afanti_tiku_lib.__file__)
            config_file = os.path.join(top_dir, DEFAULT_CONFIG_FILE)
        else:
            config_file = config_file

        self.config_file = config_file

        self.mysql_db = (mysql_db or MYSQL_DEFAULT_DB)

        self.mysql = CommonMysql(self.mysql_db, config_file=config_file)
        self.mysql_conn = None

        self.redis_proxy = RedisProxy('image_downloader.',
                                      config_file=config_file)
        self.image_downloader_item_queue = \
            self.redis_proxy.make_list('item_queue')

        self._check_exclude_md5(exclude_md5s)

    def _check_exclude_md5(self, exclude_md5s):
        if exclude_md5s:
            if hasattr(exclude_md5s, '__iter__'):
                for md5 in exclude_md5s:
                    self.exclude_md5s.add(md5)
            else:
                raise TypeError('exclude_md5s must be iterable')

    def bewitch(self, html_string,
                spider_url,
                spider_source,
                download=None,
                redownload=False,
                archive_image=None,
                headers=None,
                proxy=None,
                exclude_md5s=None,
                img_ext=None,
                priority=None):

        download = (download, self.download)[download is None]
        archive_image = (archive_image, self.archive_image)[archive_image is None]
        proxy = (proxy or self.proxy)
        img_ext = (img_ext or self.img_ext)
        priority = (priority or self.priority)
        self._check_exclude_md5(exclude_md5s)

        html_string, img_infos = ImageMagic.img_ossify(html_string,
                                                       spider_source,
                                                       uri2oss=self.uri2oss)

        for (ori_url, absurl, md5, ext) in img_infos:

            # if isinstance(img_ext, compat_str):
                # image_filename = md5 + img_ext
            # elif img_ext is True:
                # image_filename = md5 + ext
            # elif img_ext is None:
                # image_filename = md5
            # else:
                # image_filename = md5

            if ext.lower() == '.svg':
                image_filename = md5 + '.svg'
            else:
                image_filename = md5 + DEFAULT_IMG_EXT

            # not save to db
            # images which are in image_archive must been downloaded
            # successfully
            # if archive_image:
                # ImageMagic.archive_imgs(absurl, spider_source,
                                        # spider_url=spider_url,
                                        # table=self.IMAGE_TABLE,
                                        # md5=md5,
                                        # image_filename=image_filename,
                                        # mysql=self.mysql,
                                        # ignore=True,
                                        # config_file=self.config_file)

            if md5 in self.exclude_md5s:
                continue

            if redownload:
                if not self.mysql_conn:
                    self.mysql_conn = self.mysql.connection()

                sql = 'delete from {} where `md5` = %s'.format(self.IMAGE_TABLE)
                execute(self.mysql_conn, sql, values=(md5,))

            # send to image_downloader to download
            if download:
                ImageMagic.download_image(absurl, spider_source,
                                          image_filename=image_filename,
                                          spider_url=spider_url,
                                          headers=headers,
                                          proxy=proxy,
                                          priority=priority,
                                          queue=self.image_downloader_item_queue,
                                          config_file=self.config_file)
        return html_string


    @staticmethod
    def img_ossify(html_string, spider_source, uri2oss=None):
        '''
        extracting img urls and converting them to oss format
        '''

        uri2oss = (uri2oss or Uri2oss())
        img_infos = extract_image_info_with_md5(html_string)

        for (ori_url, absurl, md5, ext) in img_infos:
            if ext.lower() == '.svg':
                image_filename = md5 + '.svg'
            else:
                image_filename = md5 + DEFAULT_IMG_EXT

            # calculate oss_img_url
            oss_img_url = uri2oss.convert(
                image_filename, spider_source)
            if oss_img_url is None:
                continue

            # replace original url
            html_string = html_string.replace(ori_url, oss_img_url)

        return html_string, img_infos

    @staticmethod
    def archive_imgs(absurl, spider_source,
                     spider_url='',
                     table=None,
                     md5=None,
                     image_filename=None,
                     mysql=None,
                     ignore=True,
                     config_file=None):

        table = (table or ImageMagic.IMAGE_TABLE)
        md5 = (md5 or md5_string(absurl))
        image_filename = (image_filename or md5 + DEFAULT_IMG_EXT)
        mysql = (mysql or CommonMysql('question_db_offline',
                                      config_file=config_file))

        _acquireLock()
        try:
            # make sure one connect to be runing at one same time
            mysql.insert(
                table,
                dict(
                    url = absurl,
                    source = spider_source,
                    spider_url = spider_url,
                    md5 = md5,
                    image_filename = image_filename), ignore=ignore)
        finally:
            _releaseLock()

    @staticmethod
    def download_image(absurl, spider_source,
                       image_filename=None,
                       spider_url='',
                       headers=None,
                       proxy=False,
                       priority=False,
                       queue=None,
                       config_file=None):
        '''
        send image info to image_downloader
        '''

        if queue is None:
            redis_proxy = RedisProxy('image_downloader.',
                                     config_file=config_file)
            queue = redis_proxy.make_list('item_queue')

        item = dict(
            url = absurl,
            source = spider_source,
            md5_name = image_filename,
            spider_url = spider_url,
            headers = headers,
            proxy = proxy,
            priority = priority
        )
        queue.put(item)
