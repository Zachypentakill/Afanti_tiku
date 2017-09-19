# -*- coding: utf-8 -*-

import os
import re

from afanti_tiku_lib.utils import md5_string
from afanti_tiku_lib.compat import compat_base64
from afanti_tiku_lib.html.extract import get_html_element
from afanti_tiku_lib.url.uri2oss import Uri2oss

_re_src = re.compile(r'src\s*=\s*(\'|")(.+?)(\'|")')
DEFAULT_IMG_EXT = '.png'
uri2oss = Uri2oss()


def save_base64_img_to_local(html_string, local_dir, source):
    source = str(source)
    base64_imgs = find_base64_imgs(html_string)

    for img in base64_imgs:
        src, url = get_src(img)
        if src is None:
            raise NotFindSrc(img)

        encode_base64 = get_encode_base64_str(url)
        decode_base64 = compat_base64.b64decode(encode_base64.encode('utf-8'))

        md5_name = md5_string(encode_base64) + DEFAULT_IMG_EXT
        img_path = os.path.join(local_dir, source, md5_name)
        oss_url = uri2oss.convert(md5_name, source)

        _dir = os.path.dirname(img_path)
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        with open(img_path, 'wb') as fd:
            fd.write(decode_base64)

        html_string = html_string.replace(src, 'src-base64="{}"'.format(oss_url), 1)

    return html_string


def find_base64_imgs(html_string):
    imgs = get_html_element('<img [^<>]+;base64,', html_string,
                            regex=True, only_tag=True)
    return imgs


class NotFindSrc(Exception): pass


def get_src(img):
    mod = _re_src.search(img)
    if not mod:
        return None, None

    return mod.group(0), mod.group(2)


def get_encode_base64_str(src):
    index = src.find('base64,') + 7
    encode_str = src[index:]
    return encode_str


def restore_src(html_string):
    imgs = get_html_element('<img [^<>]*src-base64=', html_string,
                            regex=True, only_tag=True)
    for img in imgs:
        img_t = img.replace('src-base64=', 'src=', 1)
        html_string = html_string.replace(img, img_t, 1)
    return html_string
