# -*- coding: utf-8 -*-

import os
import random as random_lib


USER_AGENT_FILE = os.path.join(os.path.dirname(__file__), 'working/user_agent_file')

class UserAgent(object):

    def __init__(self, user_agent_file=USER_AGENT_FILE, random=False):
        if not os.path.exists(user_agent_file):
            raise IOError('[Errno 2] No such file or directory: {}'.format(user_agent_file))

        self.index = 0
        self.random = random
        self.user_agent_file = user_agent_file
        self.user_agent_list = [line.strip() for line in open(user_agent_file) if line.strip()]


    def get(self):
        assert self.user_agent_list

        if self.random is True:
            user_agent = random_lib.choice(self.user_agent_list)
        else:
            user_agent = self.user_agent_list[self.index]
            self.index = (self.index + 1) % len(self.user_agent_list)
        return user_agent


    def shuffle(self):
        random_lib.shuffle(self.user_agent_list)
