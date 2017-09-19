# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
import oss2

from afanti_tiku_lib.compat import (
    compat_configparser
)


class OssAPI(object):

    def __init__(self, endpoint, bucket_name, config_file=None):
        '''
        config_file: .osscredentials 文件路径
        bucket_name: <你的Bucket>
        endpoint: <你的访问域名>
        '''

        if not config_file:
            config_file = os.path.join(os.path.expanduser('~'),
                                       '.osscredentials')

        assert os.path.exists(config_file), '{} is not existed.'.format(config_file)

        self._config_file = config_file
        self._endpoint = endpoint
        self._bucket_name = bucket_name

        self.set_config()


    @property
    def config_file(self):
        return self._config_file


    @property
    def bucket_name(self):
        return self._bucket_name


    @property
    def endpoint(self):
        return self._endpoint


    @property
    def access_key_id(self):
        return self._access_key_id


    @access_key_id.setter
    def access_key_id(self, value):
        self._access_key_id = value


    @property
    def access_key_secret(self):
        return self._access_key_secret


    @access_key_secret.setter
    def access_key_secret(self, value):
        self._access_key_secret = value


    def set_config(self, config_file=None):
        config_file = config_file or self.config_file

        oss_config = compat_configparser.RawConfigParser(allow_no_value=True)
        oss_config.readfp(open(config_file))

        self._access_key_id = oss_config.get('OSSCredentials', 'accessId')
        self._access_key_secret = oss_config.get('OSSCredentials', 'accessKey')

        self._oss_bucket = oss2.Bucket(
            oss2.Auth(self.access_key_id,
                      self.access_key_secret),
            self.endpoint, self.bucket_name)


    def upload_file(self, localpath, remotepath):
        self._oss_bucket.put_object_from_file(remotepath, localpath)


    def upload_dir(self, localdir, remotedir):
        assert os.path.exists(localdir), '[OssAPI.upload_dir] {} is not existed'.format(localdir)

        for _dir, sub_dirs, files in os.walk(localdir):
            for fl in files:
                localpath = os.path.join(_dir, fl)
                remotepath = os.path.join(remotedir, fl)
                self.upload_file(localpath, remotepath)


    def meta(self, path):
        info = self._oss_bucket.get_object_meta(path)
        return info
