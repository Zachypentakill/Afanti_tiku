# -*- coding: utf-8 -*-

import logging
import asyncio
import json
import os

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import update_sql, select_sql
from afanti_tiku_lib.latex.util import displaystyle

from .render import RenderProxy

LOGGING_FILE = 'working/rendering.log'
LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logger = None

mysql = None
mysql_conn = None

COLS_HEADERS = ['question_id', 'spider_url']
DEFAULT_COLS = [('question_html_origin', 'question_html'),
                ('option_html_origin', 'option_html'),
                ('answer_all_html_origin', 'answer_all_html'),
                ('jieda_origin', 'jieda'),
                ('fenxi_origin', 'fenxi'),
                ('dianping_origin', 'dianping')]
UPDATE_COLS = {'is_rendered': 1, 'flag': 0}
CTRL_QUEUE_SIZE = 20
DEFAULT_CONDITION = 'is_rendered = 0'
DEFAULT_DB = 'question_db_offline'
LATEX_TAG = '<span class="afanti-latex">\\('
MAX_RETRY = 10

render_proxy = RenderProxy()


class RenderError(Exception): pass


async def request_render(html_string, max_retry=MAX_RETRY):
    for _ in range(max_retry):
        try:
            info_js = await render_proxy.render(html_string)
            if info_js['code'] == 0:
                return info_js
        except Exception as err:
            continue

    return {'code': 100}


async def render_questions(table, rows, ctrl_queue, args):
    max_retry = args.max_retry
    for row in rows:
        spider_url = row[1]
        logger.info('[rendering]: {}, {}'.format(table, spider_url))

        rs = list()

        success = True
        for col in row[2:]:

            # set null or '' to ''
            if not col:
                rs.append('')
                continue

            if args.latex_tag in col:
                if args.displaystyle:
                    col = displaystyle(col, latex_tag=args.latex_tag,
                                       latex=args.is_latex, mml=args.is_mml)
                try:
                    info_js = await request_render(col, max_retry=max_retry)
                    if info_js['code'] != 0:
                        raise RenderError(
                            'render_proxy code is {}'.format(info_js['code']))
                    col_r = info_js['data']
                except Exception as err:
                    logger.error(
                        '[render_proxy.render] [error]: {}, {} | {}, {}'.format(
                            table, spider_url, err, col))
                    success = False
                    break
                rs.append(col_r)
            else:
                rs.append(col)

        if not success:
            continue

        cols = dict([(k[1], rs[i]) for i, k in enumerate(args.cols)])
        cols.update(args.update_cols)

        if args.test:
            print(json.dumps(cols, indent=4, ensure_ascii=False))

        if not args.update:
            continue

        result = update_db(table, cols, spider_url)
        if result is False:
            logger.error('[update_db]: {}, {}'.format(table, spider_url))
            with open('working/fail_update_qs', 'a') as fd:
                fd.write('{}: {}\n'.format(table, spider_url))

    await ctrl_queue.get()


def get_mysql_connection():
    global mysql
    global mysql_conn

    try:
        if mysql_conn.ping() is False:
            mysql_conn = mysql.connection()
        return mysql_conn
    except Exception:
        mysql_conn = mysql.connection()
        return mysql_conn


def is_rendered(table, spider_url):
    mysql_conn = get_mysql_connection()

    sql = select_sql(table,
                     ('is_rendered',),
                     condition='where spider_url = "{}"'.format(spider_url))

    rows = execute(mysql_conn, sql)
    if rows[0][0] == 0:
        return False
    else:
        return True


def update_db(table, cols, spider_url):
    mysql_conn = get_mysql_connection()

    sql, vals = update_sql(table, cols,
                           where='where spider_url = %s')
    vals.append(spider_url)
    try:
        execute(mysql_conn, sql, values=vals)
        mysql_conn.commit()
        return True
    except Exception:
        return False


async def run(args):
    global mysql
    global mysql_conn

    mysql = CommonMysql(args.db, config_file=args.config_file)
    mysql_conn = mysql.connection()

    ctrl_queue = asyncio.queues.Queue(maxsize=args.ctrl_queue_size)

    max_id = 0
    while True:
        sql = select_sql(args.table,
                         COLS_HEADERS + [cs[0] for cs in args.cols],
                         condition=args.condition.format(max_id))
        rows = execute(mysql_conn, sql)
        if not rows:
            break

        await ctrl_queue.put(None)
        asyncio.ensure_future(render_questions(args.table, rows, ctrl_queue, args))

        if args.test:
            break

        max_id = rows[-1][0]
        logger.info('{} [max_id]:{}'.format(args.table, max_id))

    while True:
        logger.info('[ctrl_queue.qsize]: {}'.format(ctrl_queue.qsize()))
        if ctrl_queue.qsize() != 0:
            await asyncio.sleep(1 * 60)
        else:
            # over
            break

    logger.info('# over')


class Args(object):

    def __init__(self, arguments):

        #
        # arguments = dict(
        #     db = 'question_db_offline',          # default
        #     table = 'table',                     # needed
        #     cols = DEFAULT_COLS,                 # default
        #     _condition = 'is_rendered = 0',      # default
        #     update_cols = {'flag': 0, 'is_rendered': 1},  # default
        #     latex_tag = LATEX_TAG,               # default
        #     is_latex = True,                     # needed
        #     is_mml = False,                      # needed
        #     displaystyle = True,                 # default
        #     ctrl_queue_size = CTRL_QUEUE_SIZE,   # default
        #     logging_file = LOGGING_FILE,         # default
        #     test = False,                        # default
        #     update = True,                       # default
        # )
        #

        self.db = arguments.get('db') or DEFAULT_DB
        self.config_file = arguments.get('config_file')
        self.table = arguments['table']
        self.cols = arguments.get('cols') or DEFAULT_COLS
        self._condition = arguments.get('condition', DEFAULT_CONDITION)
        self.update_cols = arguments.get('update_cols', UPDATE_COLS)
        self.latex_tag = arguments.get('latex_tag', LATEX_TAG)
        self.is_latex = arguments['is_latex']
        self.is_mml = arguments['is_mml']
        self.displaystyle = arguments.get('displaystyle', True)
        self.ctrl_queue_size = arguments.get('ctrl_queue_size') or CTRL_QUEUE_SIZE
        self.logging_file = arguments.get('logging_file') or LOGGING_FILE
        self.test = arguments.get('test', False)
        self.update = arguments.get('update', True)
        self.max_retry = arguments.get('max_retry', MAX_RETRY)

        self.set_logging()

    def set_logging(self):

        global logger

        logger = logging.getLogger('rendering_log')
        logger.setLevel(logging.INFO)

        fh = logging.FileHandler(self.logging_file)
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter(LOGGING_FORMAT)
        fh.setFormatter(formatter)

        logger.addHandler(fh)


    @property
    def condition(self):
        _condition = (' and ' + self._condition) if self._condition else ''
        return 'where question_id > {{}} {} order by question_id limit {}'.format(
            _condition, (1000, 10)[self.test])


def start(arguments, close=True):
    args = Args(arguments)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(args))
    if close:
        loop.close()
