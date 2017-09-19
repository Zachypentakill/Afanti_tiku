# -*- coding: utf-8 -*-

import json
import logging

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import insert_sql, select_sql

from wln100_spider.questions.mini_spider.parser import Wln100QuestionParser

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/record_questions.log', filemode='a')

mysql = CommonMysql('html_archive')
mysql_conn = mysql.connection()

parser = Wln100QuestionParser(archive_image=True, download=True)


def record_questions(rows):
    for row in rows:
        html_string = row[1]
        spider_url = row[2]
        subject = row[3]

        try:
            qs_json = json.loads(html_string)
        except Exception as e:
            print(html_string)
        as_json = get_answer_json(spider_url[10:])
        if as_json is False:
            continue

        cols = parser.parse(spider_url, qs_json, as_json, subject)
        save_question(cols)

        # print(json.dumps(cols, indent=4, ensure_ascii=False))


def get_answer_json(wln_qid):
    sql = select_sql('wln100_spider_html_archive_table',
                     ('html',),
                     condition='where `key` = "wln100_as_{}"'.format(wln_qid))
    row = execute(mysql_conn, sql)
    if not row:
        logging.warn('[not answer]:{}'.format(wln_qid))
        return False
    else:
        return json.loads(row[0][0])


def get_mysql_connection():
    global mysql
    global mysql_conn

    try:
        if mysql_conn.ping() is False:
            mysql_conn = mysql.connection()
        #修改db
        else:
            mysql_conn = mysql.connection()
        return mysql_conn
    except Exception:
        mysql_conn = mysql.connection()
        return mysql_conn

def save_question(cols):
    mysql_conn = get_mysql_connection()

    sql, vals = insert_sql('question_db_offline.wln100_question_20160602',
                           cols, ignore=True)
    execute(mysql_conn, sql, values=vals)


def main():
    mysql_conn = get_mysql_connection()
    #html_id = 30692943
    max_id = 0
    while True:
        sql = select_sql('wln100_spider_html_archive_table',
                         ('html_id', 'html', 'key', 'subject'),
                         condition='where html_id > {} and `key` like "wln100_qs%" limit 1000'.format(max_id))
        rows = execute(mysql_conn, sql)
        if not rows:
            break

        record_questions(rows)
        max_id = rows[-1][0]

if __name__ == '__main__':
    main()
