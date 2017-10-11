# -*- coding: utf-8 -*-

import logging
import json

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import insert_sql, select_sql

from parser import VkoParser


LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/record_questions.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

parser = VkoParser(download=True)


def record_questions(rows):
    mysql_conn = get_mysql_connection()

    for row in rows:
        try:
            js = json.loads(row[1])
            spider_url = row[2]
            cols = parser.parse(js, spider_url)
        except Exception as err:
            logging.error('[parser.parse] {}, {}'.format(err, spider_url))
            continue

        if not cols:
            continue

        # print(json.dumps(cols, indent=4, ensure_ascii=False))

        logging.info(spider_url)

        sql, vals = insert_sql('question_db_offline.vko_question_20161116',
                               cols, ignore=True)
        execute(mysql_conn, sql, values=vals)


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


def main():
    mysql_conn = get_mysql_connection()

    max_id = 0
    while True:
        sql = select_sql('vko_spider_html_archive_table',
                         ('html_id', 'html', 'key'),
                         condition='where html_id > {} order by html_id limit 10'.format(max_id))

        rows = execute(mysql_conn, sql)
        if not rows:
            break

        record_questions(rows)

        max_id = rows[-1][0]

    logging.info('# over')


if __name__ == '__main__':
    main()
