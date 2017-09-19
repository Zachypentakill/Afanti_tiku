# -*- coding: utf-8 -*-

import os

def makedirs(*dirs):
    for _dir in dirs:
        if not os.path.exists(_dir):
            os.makedirs(_dir)
