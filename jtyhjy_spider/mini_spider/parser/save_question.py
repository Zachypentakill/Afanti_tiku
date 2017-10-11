# -*- coding:utf8 -*-
from __future__ import unicode_literals

import os
import logging
import configparser
import multiprocessing
import traceback
#from cloghandler import ConcurrentRotatingFileHandler
try:
    from cloghandler import ConcurrentRotatingFileHandler as RFHandler
except ImportError:
    from warnings import warn
    warn("ConcurrentLogHandler package not installed.  Using builtin log handler")
    from logging.handlers import RotatingFileHandler as RFHandler

from afanti_tiku_lib.dbs.MySQLClient import MySQLClient


MAX_ERROR_TIME = 10

_LOCK = multiprocessing.Lock()
_QUIT_FLAG = multiprocessing.Value('i', 0)
_ERROR_COUNT = multiprocessing.Value('i', 0)
_ID = multiprocessing.Value('i', 0)


PRIMARY_KEY = ''

db_config_file = os.path.join(
        os.path.expanduser('~'), '.dbinfo')
config = configparser.RawConfigParser(allow_no_value=True)
config.readfp(open(db_config_file))
QUESTION_DICT = dict(
    user=config.get('question', 'username'),
    passwd=config.get('question', 'passwd'),
    host=config.get('question', 'host'),
    port=int(config.get('question', 'port')),
    db=config.get('question', 'db')
)


class IterTableException(Exception):
    pass


class BaseProcess(multiprocessing.Process):
    def __init__(self, **kwargs):
        defaults = dict(
            logger=logging.getLogger(__name__),
            quit_flag=_QUIT_FLAG,
            error_count=_ERROR_COUNT,
            lock=_LOCK,
            max_error_count=MAX_ERROR_TIME,
            primary_key_id=_ID
        )
        # for k, v in kwargs.items():
        #     if k in defaults:
        #         defaults[k] = v
        #         kwargs.pop(k)
        #         del kwargs[k]

        # kwarg = {}
        # for k in kwargs.keys():
        #     if k in defaults:
        #         defaults[k] = kwargs[k]
        #     else:
        #         kwarg[k] = kwargs[k]

        for k in list(kwargs):
            if k in defaults:
                defaults[k] = kwargs[k]
                kwargs.pop(k)
        multiprocessing.Process.__init__(self, **kwargs)
        self.__dict__.update(defaults)

    @property
    def _need_quit(self):
        with self.lock:
            if self.quit_flag.value == 1:
                self.logger.info(
                    '[process:%s] quit_flag=1, ', self.pid
                )
                return True
            elif self.error_count.value > self.max_error_count:
                self.logger.warning(
                    '[process:%s] error_count:%s > max_error_count:%s.',
                    self.pid, self.error_count.value, self.max_error_count
                )
                return True
            else:
                return False

    @_need_quit.setter
    def _need_quit(self, value):
        with self.lock:
            if value:
                self.quit_flag.value = 1

    def inc_error_count(self):
        with self.lock:
            self.error_count.value += 1

    def get_primary_key_range(self):
        self.step = 2000
        with self.lock:
            min_id = self.primary_key_id.value
            self.primary_key_id.value += self.step
            max_id = self.primary_key_id.value
            return min_id, max_id


class _Parser(object):
    def __init__(self, init):
        self.__init = init

    def init(self):
        return self._init()


class Worker(BaseProcess):
    def __init__(self, src_table, parser, primary_key='question_id',
                 reuse_MySQL=True, **kwargs):
        BaseProcess.__init__(self, **kwargs)
        self.src_table = src_table
        self.primary_key = primary_key
        if not hasattr(parser, '__call__'):
            raise IterTableException(
                'parser passed to consumer must be a lambda function'
            )
        self.parser = parser()
        if not hasattr(self.parser, 'deal_one_item'):
            raise IterTableException(
                'parser passed to consumer must implement deal_one_item func'
            )
        if not reuse_MySQL:
            if 'question_dict' in kwargs:
                question_dict = kwargs['question_dict']
                self.sql_client = MySQLClient(**question_dict)
            else:
                self.sql_client = MySQLClient(**QUESTION_DICT)
        else:
            self.sql_client = self.parser.sql_client


    def _select_res(self):
        min_id, max_id = self.get_primary_key_range()
        try:
            sql = 'select * from {src_table} where {primary_key} > ? and '\
                '{primary_key} < ? limit {step}'.format(
                    src_table=self.src_table,
                    primary_key=self.primary_key,
                    step=self.step
                )
            question_lst = self.sql_client.select(sql, min_id, max_id)
            no_question_flag = False
            if not question_lst:
                sql = 'select * from {src_table} where {primary_key} > ? '\
                    'limit 1'.format(
                        src_table=self.src_table,
                        primary_key=self.primary_key)
                res = self.sql_client.select(sql, min_id)
                if res:
                    no_question_flag = False
                else:
                    no_question_flag = True
            return question_lst, no_question_flag
        except Exception as err:
            self.inc_error_count()
            self.logger.warning(
                '[process:%s] an error happend in get_question_lst. err:%s, '\
                'min_qid, max_qid is (%s, %s)',
                self.pid, err, min_id, max_id
            )
            return -1, False

    def run(self):
        primary_key_id = 0
        while not self._need_quit:
            question_lst, no_question_flag = self._select_res()
            if no_question_flag:
                self.logger.info(
                    '[process:%s][primary_key_id:%s] empty question_lst, quit '\
                    'the process ', self.pid, primary_key_id
                )
                return
            for question in question_lst:
                if self._need_quit:
                    self.logger.warning(
                        '[process:%s] quit the process because of quit_flag.',
                        self.pid
                    )
                    return
                try:
                    primary_key_id = question.get(self.primary_key, '-1')
                    self.parser.deal_one_item(question)
                except Exception as err:
                    self.logger.warning(
                        '[process:%s] an error happend in deal_one_item. '\
                        'err:%s, primary_key_id:%s, trackback:%s',
                        self.pid, err, primary_key_id, traceback.format_exc()
                    )
                    self.inc_error_count()


def run(src_table, parser, primary_key='question_id', p_number=2, reuse_MySQL=True, **kwargs):
    process_lst = []
    for i in range(p_number):
        p = Worker(src_table, parser, primary_key, reuse_MySQL=reuse_MySQL, **kwargs)
        p.daemon = True
        process_lst.append(p)
        p.start()
    for p in process_lst:
        p.join()


if __name__ == '__main__':
    log_file = 'save_question.log'
    # 日志配置
    logger = logging.getLogger('iter')
    # 单份日志60M， 保留500份
    rotateHandler = RFHandler(
        log_file, 'a', 1024 * 1024 * 60, 500
    )
    format_string = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s'\
        ' %(message)s'
    formatter = logging.Formatter(format_string)
    rotateHandler.setFormatter(formatter)
    logger.addHandler(rotateHandler)
    logger.setLevel(logging.DEBUG)


    from jtyhjy_spider.mini_spider.parser.parser import Parser
    parser = lambda: Parser()
    primary_key = 'html_id'
    src_table = '`html_archive2`.`jtyhjy_spider_html_archive_table`'
    run(src_table, parser, primary_key, p_number=5, logger=logger, reuse_MySQL=True)
