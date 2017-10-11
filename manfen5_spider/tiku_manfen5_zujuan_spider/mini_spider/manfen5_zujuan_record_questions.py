# -*- coding: utf-8 -*-

import logging
import json

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import insert_sql, select_sql

from manfen5_spider.tiku_manfen5_zujuan_spider.mini_spider.parser import Manfen5ZujuanParser


LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/record_questions.log', filemode='a')

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()

parser = Manfen5ZujuanParser(download=False)


def record_questions(rows):
    mysql_conn = get_mysql_connection()

    for row in rows:
        html_string = row[1]
        spider_url = row[2]
        info = json.loads(row[3])

        # if is_archived(spider_url):
            # continue

        logging.info(spider_url)

        try:
            cols = parser.parse(html_string, spider_url, info)
        except Exception as err:
            logging.error('[parser.parse] {}, {}'.format(err, spider_url))
            continue

        if not cols:
            continue

        # print(json.dumps(cols, indent=4, ensure_ascii=False))

        sql, vals = insert_sql('question_db_offline.manfen5_zujuan_question_20161205',
                               cols, ignore=True)
        execute(mysql_conn, sql, values=vals)
        mysql_conn.commit()


def get_mysql_connection():
    global mysql
    global mysql_conn

    try:
        if mysql_conn.ping() is False:
            mysql_conn = mysql.connection(db= 'html_archive2')
        #修改db
        else:
            mysql_conn = mysql.connection(db='html_archive2')
        return mysql_conn
    except Exception:
        mysql_conn = mysql.connection(db= 'html_archive2')
        return mysql_conn


def is_archived(url):
    mysql_conn = get_mysql_connection()

    sql = select_sql('question_db_offline.manfen5_zujuan_question_20161205',
                     ('question_id',),
                     condition='where `spider_url` = %s')
    result = execute(mysql_conn, sql, values=(url,))
    return result


def main():
    mysql_conn = get_mysql_connection()

    max_id = 67233781
    while True:
        sql = select_sql('manfen5_zujuan_spider_html_archive_table',
                         ('html_id', 'html', 'key', 'info'),
                         condition='where html_id > {} order by html_id limit 1000'.format(max_id))

        rows = execute(mysql_conn, sql)
        if not rows:
            break

        record_questions(rows)

        max_id = rows[-1][0]

    logging.info('# over')


if __name__ == '__main__':
    main()
