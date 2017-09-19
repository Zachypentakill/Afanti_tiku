# -*- coding: utf-8 -*-

from afanti_tiku_lib.oss.oss_api import OssAPI

endpoint = 'http://oss-cn-beijing-internal.aliyuncs.com'
bucket_name = 'afanti-question-images'

path = 'data/image/question_image/3/cd6d1a7f6d32a1c07af3e0fb165b69b9.png'

oss_api = OssAPI(endpoint, bucket_name)

info = oss_api.meta(path)

print(dir(info))
