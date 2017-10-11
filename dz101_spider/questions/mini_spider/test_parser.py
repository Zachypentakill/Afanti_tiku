# -*- coding: utf-8 -*-

import json

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import select_sql

from parser import Dz101QuestionParser

parser = Dz101QuestionParser(download=False)

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()


def test():
    sql = select_sql('dz101_spider_html_archive_table',
                     ('key', 'html', 'subject'), condition='where html_id > 0 limit 10')
    rows = execute(mysql_conn, sql)

    for row in rows:
        url = row[0]
        html_string = row[1]
        subject = row[2]

        cols = parser.parse(html_string, url, subject)

        print(json.dumps(cols, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    test()
