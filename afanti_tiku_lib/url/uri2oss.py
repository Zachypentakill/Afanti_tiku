# -*- coding: utf-8 -*-

'''
this py is used for convert img_path from origin to aliyun_oss with md5 format
just call convert(image_uri)
'''

from __future__ import unicode_literals, absolute_import

import re
import os
import time
import hmac
import hashlib

from afanti_tiku_lib.compat import (
    compat_configparser,
    compat_urllib_parse,
    compat_base64,
    compat_bytes,
)


class Uri2oss(object):
    '''
    将传入的md5格式的图片uri为OSS格式
    '''

    def __init__(self, oss_config_file=None):
        '''
        oss_config_file: .osscredentials 文件路径
        '''
        if not oss_config_file:
            oss_config_file = os.path.join(
                os.path.expanduser('~'), '.osscredentials')

        if os.path.exists(oss_config_file):
            self.oss_config = compat_configparser.RawConfigParser(allow_no_value=True)
            self.oss_config.readfp(open(oss_config_file))
            self.accessKeyId = self.oss_config.get('OSSCredentials', 'accessId')
            self.accessKeySecret = self.oss_config.get('OSSCredentials', 'accessKey')
        else:
            self.accessKeyId = None
            self.accessKeySecret = None


    # --- aliyun_oss function start ---

    def get_oss_url(self, uri, img_bucket=None, img_host=None):
        expire_time = int(time.time()) + 60 * 60 * 24 * 365 * 10
        sign_str = compat_bytes(
            'GET\n\n\n{}\n/{}/{}'.format(expire_time, img_bucket, uri),
            'utf-8')
        h = hmac.new(compat_bytes(self.accessKeySecret, 'utf-8'),
                    sign_str,
                    hashlib.sha1)
        sign = compat_urllib_parse.quote_plus(
            compat_base64.encodebytes(h.digest()).strip())
        image_url = '{}/{}?OSSAccessKeyId={}&Expires={}&Signature={}'.format(
            img_host, uri, self.accessKeyId, expire_time, sign)
        return image_url

    def get_oss_url2(self, uri, img_bucket=None, img_host=None):
        image_url = '{}/{}'.format(img_host, uri)
        return image_url

    # --- aliyun_oss function end ---


    def check_md5(self, string):
        if re.match(r'^([a-fA-F0-9]{32}(\.[a-zA-Z]{3,4})?)$', string):
            return True
        else:
            return False

    def convert(self, image_uri, spider_source,
                img_host='http://qimg.afanti100.com',
                img_bucket='afanti-question-images'):
        '''
        参数:   image_url: md5图片uri，
                spider_source: 图片的源
        返回值: url
                OSS格式的图片链接, 如果image_url不是md5的图片uri
                返回 None
        '''
        if self.check_md5(image_uri):
            oss_image_url = self.get_oss_url2(
                'data/image/question_image/{}/{}'.format(spider_source, image_uri),
                img_bucket=img_bucket,
                img_host=img_host,
            )
            return oss_image_url
        return None


class GeneralUri2oss(object):
    def __init__(self, oss_config_file=None):
        if not oss_config_file:
            oss_config_file = os.path.join(
                os.path.expanduser('~'), '.luti_osscredentials')

        if os.path.exists(oss_config_file):
            self.oss_config = compat_configparser.RawConfigParser(allow_no_value=True)
            self.oss_config.readfp(open(oss_config_file))
            self.accessKeyId = self.oss_config.get('OSSCredentials', 'accessId')
            self.accessKeySecret = self.oss_config.get('OSSCredentials', 'accessKey')
            self.endpoint = self.oss_config.get('OSSCredentials', 'endpoint')
        else:
            self.accessKeyId = None
            self.accessKeySecret = None
            self.endpoint = None

    def generate_sign(self, uri, img_bucket):
        expire_time = int(time.time()) + 60 * 60 * 24
        sign_str = compat_bytes(
            'GET\n\n\n{}\n/{}/{}'.format(expire_time, img_bucket, uri),
            'utf-8')
        h = hmac.new(compat_bytes(self.accessKeySecret, 'utf-8'),
                    sign_str,
                    hashlib.sha1)
        sign = compat_urllib_parse.quote_plus(
            compat_base64.encodebytes(h.digest()).strip())
        return sign, expire_time

    def get_oss_url(self, uri, img_bucket=None, img_host=None):
        if not (uri and img_bucket):
            raise Exception('uri and img_bucket should be given')
        sign, expire_time = self.generate_sign(uri, img_bucket)
        if not img_host:
            img_host = 'http://%s.%s' % (img_bucket, self.endpoint)
        image_url = '{}/{}?OSSAccessKeyId={}&Expires={}&Signature={}'.format(
            img_host, uri, self.accessKeyId, expire_time, sign)
        return image_url


def test():
    image_uri = '''2dad6f29ef14962788d9c35192b1766e.png'''
    uri2oss = Uri2oss()
    print(image_uri)
    print(uri2oss.convert(image_uri, 23))

    afanti_image_uri = 'data/image7/user_upload_image/20161209/14/1474354930835816_178526262_6e2267d0-bddc-11e6-ac90-00163e007c1d.jpg'
    uri2oss = GeneralUri2oss()
    print(afanti_image_uri)
    print(uri2oss.get_oss_url(afanti_image_uri, 'afanti-image'))

    luti_uri = 'jf/books/DFCB-01-2016A-01-71-1-00/070_09.jpg'
    print(luti_uri)
    print(uri2oss.get_oss_url(luti_uri, 'afanti-luti'))


if __name__ == '__main__':
    test()
