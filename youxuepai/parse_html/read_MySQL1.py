import traceback
import json
import pymysql
import pymysql.cursors
from question_template import Question,QuestionFormatter
from multiprocessing import Pool, Process
import re
import time
from twisted.enterprise import adbapi
import os
from afanti_tiku_lib.html.image_magic import ImageMagic

def writecsv(items):
    strlist = [str(items['source_id']), str(items['key2']), str(items['html']),
               str(items['request_info']), str(items['subject']), str(items['question_type'])]
    strs = ','.join(strlist)
    f.writelines(strs + '\n')

def remove_biaoqian(str_bioaqian):
    if isinstance(str_bioaqian, str):
        str_bioaqian = str_bioaqian.replace('&nbsp;',' ').replace('; ; ; ;','').replace("\\/",'/')
        str_bioaqian = str_bioaqian.replace('; ; ;','').replace('&nbsp', ' ')
        str_bioaqian = str_bioaqian.replace('; ;', ' ').replace('\/','/')
        return str_bioaqian
    else:
        print("插入的不是str格式！")


def Data_to_MySQL(datas):
    #采用同步的机制写入mysql
    conn = pymysql.connect(host='10.44.149.251', user='liyanfeng', passwd='AFtdbliyf7893', db='question_db_offline',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    datas["sorce"] = 75
    insert_sql = """
                insert ignore into youxuepai_parse_0807(spider_source, spider_url, knowledge_point,
                 `subject`, difficulty, question_type, question_html,question_html_origin,
                answer_all_html, answer_all_html_origin, jieda, jieda_origin, fenxi, fenxi_origin, 
                dianping, dianping_origin, html_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
    if len(datas['question_body']) != 0:
        cursor.execute(insert_sql, (
        75, datas["spider_url"], datas["knowledge_point"], datas["subject"], datas["difficulty"],
        datas["question_type"], datas["question_body"],
        datas["question_body"], datas["answer"], datas["answer"], datas["jieda"], datas["jieda"], datas["analy"],
        datas["analy"], datas["comment"], datas["comment"], datas["question_id"]))
    else:
        cursor.execute(insert_sql, (
        75, datas["spider_url"], datas["knowledge_point"], datas["subject"], datas["difficulty"],
        datas["question_type"], '', '', datas["answer"], datas["answer"], datas["jieda"], datas["jieda"],
        datas["analy"], datas["analy"], datas["comment"], datas["comment"], datas["question_id"]))
    conn.commit()

def tableToJson(table):
    conn = pymysql.connect(host='10.44.149.251', user='liyanfeng', passwd='AFtdbliyf7893', db='html_archive',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()
    #sql = 'select * from %s where question_type = 12 limit 15000, 2800' % table
    #sql = 'select * from %s where question_type = 2 limit 500 ' % table
    # sql = 'select * from %s limit 300000, 100000' % table
    sql = 'select * from %s limit 670000, 20000' % table
    #sql = 'select * from {} where html like "%frac%" limit 500 '.format(table)
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    jsonData = []
    for row in data:
        image_parse = ImageMagic(75, download=True, archive_image=False)
        # row = list(row)
        result = {}  # temp store one jsonObject
        result['question_id'] = row['source_id']
        result['spider_sorce'] = 75
        result['spider_url'] = row['key2']
        result['subject'] = row['subject']
        result['question_type'] = row['question_type']
        import traceback
        #由于html解析后出现"aorder":false等情况，如果不加下列两行，则出现name 'false' is not defined报错
        false = False
        true = True
        null = None
        try:
            if isinstance(row['html'], str):
                html_contents = row['html']
                try:
                    html_contents = image_parse.bewitch(html_string=str(html_contents), spider_url=row['key2'],
                                                        spider_source='75')
                except Exception as e:
                    print(traceback.print_exc())
                html_contents = remove_biaoqian(html_contents)
                html_contents = eval(html_contents)
                if isinstance(html_contents,bytes):
                    html_contents = html_contents.decode()
                    html_content = eval(html_contents)
                elif isinstance(html_contents,dict):
                    html_content = html_contents

        except Exception as e:
            # print(row)
            # print(row['html'])
            # print('++' * 20)
            # print(traceback.print_exc())
            # print(e)
            pass

        try:
            result['difficulty'] = html_content['difficulty']
        except:
            pass

        try:
            result['question_body'] = html_content['prompt']
        except:
            pass

        try:
            options = html_content['options']
            option = []
            if options:
                for keys, values in options.items():
                    value_items = {}
                    value_items['value'] = keys
                    value_items['content'] = values
                    option.append(value_items)
            result['option_lst'] = option
        except:
            pass

        a = int(row['question_type'])
        if a == 2 or a == 4 or a == 3:
            try:
                answer = html_content['answer']
                if len(answer) == 0:
                    answer = ''
                    result['answer'] = answer
                else:
                    if isinstance(answer, str):
                        result['answer'] = answer
                    elif isinstance(answer, list):
                        answers = ''
                        for i in answer:
                            if isinstance(i, str):
                                answers += i + ' '
                            elif isinstance(i, list):
                                answers += i[0] + ' '
                        if len(answers) == 0:
                            answers = ''
                        result['answer'] = answers
            except:
                pass

        else:
            try:
                jieda = html_content['jieda']
                if len(jieda) == 0:
                    jieda = ''
                    result['jieda'] = jieda
                else:
                    if isinstance(jieda, str):
                        result['jieda'] = jieda
                    elif isinstance(jieda, list):
                        jiedas = ''
                        for i in jieda:
                            if isinstance(i, str):
                                jiedas += i + ' '
                            elif isinstance(i, list):
                                jiedas += i[0] + ' '
                        if len(jiedas) == 0:
                            jiedas = ''
                        result['jieda'] = jiedas
            except:
                pass

        try:
            result['analy'] = html_content['parse']
        except:
            pass

        try:
            result['comment'] = html_content['comment']
        except:
            pass

        try:
            sub_question_lst = html_content['items']
            sub_question_lsts = []
            if sub_question_lst:
                for i in range(len(sub_question_lst)):
                    sub_question = parse_sub_question_lst(sub_question_lst[i])
                    sub_question_lsts.append(sub_question)
                result['sub_question_lst'] = sub_question_lsts
        except:
            pass

        try:
            result['flag'] = row['flag']
        except:
            pass
        jsonData.append(result)
    return jsonData

def parse_sub_question_lst(row):
    result ={}
    try:
        result['question_type'] = row['qtypeId']
    except:
        pass

    try:
        result['subject'] = row['subjectId']
    except:
        pass

    try:
        gid = row['gid']
        number = re.findall('.+tion:(.+?)-sub', gid)
        newnumnber = re.findall(number[0])
        result['question_id'] = newnumnber
    except:
        pass

    try:
        result['difficulty'] = row['difficulty']
    except:
        pass

    try:
        answer = row['answer']
        if answer is None:
            answer = ''
        result['answer'] = answer
    except:
        pass

    try:
        result['comment'] = row['comment']
    except:
        pass

    try:
        options = row['options']
        option = []
        if options:
            for keys, values in options.items():
                value_items = {}
                value_items['value'] = keys
                value_items['content'] = values
                option.append(value_items)
        result['option_lst'] = option
    except:
        pass

    try:
        result['question_body'] = row['prompt']
    except:
        pass

    try:
        result['analy'] = row['parse']
    except:
        pass

    try:
        result['score'] = row['score']
    except:
        pass

    try:
        result['sub_question_lst'] = row['items']
    except:
        pass
    return result


if __name__ == '__main__':
    jsonData = tableToJson('youxuepai_0802')
    pool = Pool()
    none_list = []
    for table in jsonData:
        youxuepai = Question(**table)
        # if len(youxuepai['answer'] + youxuepai['jieda'] + youxuepai['comment'] + youxuepai['analy'] + youxuepai['question_body']) != 0:
        #     youxuepais = youxuepai.normialize()
        #     pool.apply_async(func=Data_to_MySQL,args=(youxuepais,))
        youxuepais = youxuepai.normialize()
        pool.apply_async(func=Data_to_MySQL, args=(youxuepais,))
    pool.close()
    pool.join()


    # all_content = []
    # for table in jsonData:
    #     youxuepai = Question(**table)
    #     try:
    #         youxuepais = youxuepai.normialize()
    #     except Exception as e:
    #         print(e)
    #     # youxuepaiss = parse_database(youxuepais)
    #     all_content.append(youxuepais)
    # for tables in all_content:
    #     Data_to_MySQL(tables)
