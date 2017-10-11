# -*- coding: utf-8 -*-

import json

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute
from afanti_tiku_lib.dbs.sql import select_sql

from parser import VkoParser

parser = VkoParser(download=False)

mysql = CommonMysql('html_archive2')
mysql_conn = mysql.connection()


def test():
    sql = select_sql('vko_spider_html_archive_table',
                     ('key', 'html'),
                     condition='where `key` = "vko_qs_970"')
                     # condition='where html_id = 11496')
                     # condition='where html_id > 0 limit 10')
    rows = execute(mysql_conn, sql)

    for row in rows:
        url = row[0]
        js = json.loads(row[1])

        cols = parser.parse(js, url)

        print(json.dumps(cols, indent=4, ensure_ascii=False))

        # print(js['content'])

if __name__ == '__main__':
    test()
