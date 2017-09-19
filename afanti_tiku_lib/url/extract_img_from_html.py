# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, print_function

import re
import os
import base64
import urllib

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.compat import (
    compat_urllib_parse,
    compat_str,
)
from afanti_tiku_lib.common import IMAGETYPES


def get_ext(url, default=''):
    '''
    获取文件的扩展名
    参数：path：需要判断文件类型的路径
          default：默认类型
    返回值：ext：文件类型
    '''

    parser = urllib.parse.urlparse(url)
    path = parser.path.rstrip('/')
    _, ext = os.path.splitext(path)

    if ext and ext.lower() in IMAGETYPES:
        return ext.lower()
    else:
        return default


def abs_url(url, base_url=None):
    '''
    获取url的完整路径
    参数：url：需要获取完整路径的url
          base_url：需要拼接的url前缀
    返回值：url：完整的url链接
    '''
    if url[:4] == 'http':
        return url

    if base_url:
        return compat_urllib_parse.urljoin(base_url, url)
    else:
        return url


_re_img_tag        = re.compile(r'<img[^<>]+?>', flags=(re.S | re.I))

# 2017.02.13 添加_re_img_src图片链接对空格的匹配
# 该图片链接是有效链接，但是其中有空格http://www.lewen.com/upload//papers/papers92/MXSM10S-57399 安徽省芜湖市师大附中2012-2013学年高一（上）数学期中考试/images/Word_33.jpg
_re_img_src        = re.compile(r"""\Wsrc\s*=\s*['"\\]\s*([^'"]+)""", flags=re.I)

# 2017.02.13 添加对无引号的图片链接的提取支持
_re_img_src_type_2 = re.compile(r"""\Wsrc\s*=\s*((?:(?:https?:/):?)[^'"\s]+)""", flags=re.I)
# 下面两个图片标签中的匹配 \Wsrc=\s*([^'"\s]+)的部分都被Chrome当作图片链接来处理了，
# 但是第二个图片“链接”是“width=200px”，这个是不合理的，所以我们不提取出不包含http://或者https://或者以'/'开头的链接
# <img src= https://www.baidu.com/img/bd_logo1.png?width=500 width=200px>
# <img src= width=200px>

_re_img_background = re.compile(r"""background(?:-image|):\s*?url\s*[('"\\]+\s*([^'"()\s]+)""", flags=re.I)

def extract_image_infos(string, base_url=None, unique=False):
    '''
    提取一段文本中的所有的url链接
    参数：string: 需要提取url链接的字符串
    返回值：image_ulrs：列表，每个元素为提取出的图片链接
    '''

    if not string or not isinstance(string, compat_str):
        return list()

    match_groups = []
    # for elem in re.findall(r'<img[^<>]+?>', string, flags=(re.S | re.I)):
    for elem in _re_img_tag.findall(string):
        # The expression’s behaviour can be modified by specifying a
        # flags value. Values can be any of the following variables,
        # combined using bitwise OR (the | operator).
        # match_groups += re.findall(
            # r"""\Wsrc\s*=[\s'"\\]*([^'"\s\\]+)""", elem, flags=re.I)
        match_groups += _re_img_src.findall(elem)
        match_groups += _re_img_src_type_2.findall(elem)
    # match_groups += re.findall(
        # r"""background(?:-image|):\s*?url[(\s'"\\]+([^'"()\s\\]+)""",
        # string, flags=re.I)
    match_groups += _re_img_background.findall(string)

    image_urls = list()

    for uri in match_groups:
        image_urls.append(abs_url(uri, base_url=base_url))
    if unique:
        image_urls = list(set(image_urls))
    return image_urls


def extract_image_info_with_md5(
            string, base_url=None,
            repair_incomplete_tag=False):

    # 修复放在业务逻辑去做
    # if repair_incomplete_tag:  # 如果repair_incomplete_tag为真，
                               # # 使用BS来修补不完整的标签
        # soup = BeautifulSoup(string, 'lxml')
        # string = compat_str(soup)

    url_lst = extract_image_infos(string)
    res_lst = set()
    for url in set(url_lst):
        res_lst.add(convert_url_into_md5(url, base_url))
    return list(res_lst)


def convert_url_into_md5(url, base_url):
    absurl = abs_url(url, base_url)
    md5 = md5_string(absurl)
    ext = get_ext(absurl)
    return (url, absurl, md5, ext)


def extract_image_info_with_md5_after_del_backslash(
            string, base_url=None,
            repair_incomplete_tag=False):
    string = string.replace('\\', '')
    return extract_image_info_with_md5(
        string, base_url=base_url,
        repair_incomplete_tag=repair_incomplete_tag)


_re_img_base64 = re.compile(r'^data:image/(?P<img_type>(png)|(jpg)|(jpeg)|(gif)|(bmp)|(svg));base64,(?P<base64_string>.*?)$', re.I)

def extract_image_info_from_base64_image(src):
    '''
    从<img src="data:image.....">的src值中将图片的二进制内容提取出来
    '''

    # pattern = re.compile(r'^data:image/(?P<img_type>(png)|(jpg)|(jpeg)|(gif)|(bmp)|(svg));base64,(?P<base64_string>.*?)$', re.I)
    match = _re_img_base64.match(src)
    if match:
        base64_string = match.group('base64_string')
        img_type = match.group('img_type')
        ext = '.' + img_type if img_type else ''
        md5 = md5_string(base64_string)
        img_content = base64.b64decode(base64_string)
        return {'url':src, 'md5':md5, 'img_content':img_content, 'ext':ext}
    else:
        raise Exception('cannot extract image from src')


def extract_base64_image_info_with_md5(string, base_url=None):
    '''
    从html中提取出正常url链接的图片链接列表与base64格式的图片列表
    '''
    base64_lst = set()
    normal_res = set()
    img_lst = extract_image_infos(string)
    for img in img_lst:
        if re.match(r'^data.*?$', img):
            base64_lst.add(img)
        else:
            img_tuple = convert_url_into_md5(img, base_url)
            normal_res.add(img_tuple)
    base64_res = []
    for img in base64_lst:
        img_dict = extract_image_info_from_base64_image(img)
        base64_res.append(img_dict)
    return list(normal_res), base64_res


_re_img_aft = re.compile('^http://img.afanti100.com/data/image/question_image/(?P<source>\d+)/(?P<md5>[a-fA-F0-9]{32})(?P<ext>\.[a-zA-Z]{3,4})?\?OSSAccessKeyId=(?P<accessKeyId>[^&]*?)&Expires=(?P<expires>\d+)&Signature=(?P<signature>.*?)$')

def extract_oss_info(oss_url):
    '''
    从一个oss链接中提取出oss信息信息
    '''

    # pattern = re.compile('^http://img.afanti100.com/data/image/question_image/(?P<source>\d+)/(?P<md5>[a-fA-F0-9]{32})(?P<ext>\.[a-zA-Z]{3,4})?\?OSSAccessKeyId=(?P<accessKeyId>[^&]*?)&Expires=(?P<expires>\d+)&Signature=(?P<signature>.*?)$')
    res = _re_img_aft.findall(oss_url)
    if not res:
        return None
    else:
        res_dict = {
                'source': res[0][0],
                'md5': res[0][1],
                'ext': res[0][2],
                'accessKeyId': res[0][3],
                'expire': res[0][4],
                'signature': res[0][5]
                }
        return res_dict


