# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
import re

def get_image_size(image_path):
    abs_image_path = os.path.abspath(image_path)
    info = os.popen('file "{}"'.format(abs_image_path.replace('"', '\\"'))).read()

    mod = re.search(r'(\d+)\s*(?:x|X)\s*(\d+)', info)
    if mod:
        return int(mod.group(1)), int(mod.group(2))
    else:
        return None
