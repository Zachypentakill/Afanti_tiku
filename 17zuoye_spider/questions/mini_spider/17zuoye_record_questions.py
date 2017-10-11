# -*- coding: utf-8 -*-

import logging
import json

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import insert_sql, select_sql

from parser import Zuoye17QuestionParser


LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/record_questions.log', filemode='a')

mysql = CommonMysql('html_archive')
mysql_conn = mysql.connection()

parser = Zuoye17QuestionParser(archive_image=True, download=True)


def record_questions(rows):
    mysql_conn = get_mysql_connection()

    for row in rows:
        js = json.loads(row[1])
        spider_url = row[2]
        aft_subj_id = row[3]

        try:
            cols = parser.parse(spider_url, js, aft_subj_id)
        except Exception as err:
            logging.error('[parser.parse] {}, {}'.format(err, spider_url))
            continue

        # print(json.dumps(cols, indent=4, ensure_ascii=False))

        sql, vals = insert_sql('question_db_offline.17zuoye_question_20160719',
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
        sql = select_sql('17zuoye_spider_html_archive_table',
                         ('html_id', 'html', 'key', 'subject'),
                         condition='where html_id > {} order by html_id limit 1000'.format(max_id))
                         # condition='where `key` = "17zuoye_qs_Q_20300538822231"'.format(max_id))

        rows = execute(mysql_conn, sql)
        if not rows:
            break

        record_questions(rows)

        max_id = rows[-1][0]


if __name__ == '__main__':
    main()
