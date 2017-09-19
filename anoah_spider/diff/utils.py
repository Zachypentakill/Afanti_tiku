# encoding:utf-8
from functional import seq
import re
import json
# from afanti_tiku_lib.question_template import question_template
import copy
from functools import partial
from gevent import monkey
import gevent


monkey.patch_all(socket=True, dns=True, time=True, select=True,
                 thread=False, os=True, ssl=True, httplib=False, aggressive=True)


class BaseMixin(object):
    model = ''
    model_key = ''
    thread_number = 5

    def start(self):
        self.run_all()

    def run(self, obj):
        pass

    def get_obj(self, _id):
        return self.model.objects.get(**{self.model_key: _id})

    def get_objects_id(self):
        ids = self.model.objects.all().values_list(self.model_key)
        return seq(ids).map(lambda x: x[0]).list()

    def run_each(self, id_group):
        seq(id_group).map(self.get_obj).for_each(self.run)

    def run_all(self):
        ids = self.get_objects_id()
        size = int(len(ids) / self.thread_number) + 1
        id_groups = seq(seq(ids).grouped(size)).map(list).list()
        jobs = [gevent.spawn(self.run_each, id_group)
                for id_group in id_groups]
        print(jobs)
        gevent.joinall(jobs)


class ObjectTools(object):

    def text2json(self, text):
        return json.loads(text)

    def json2obj(self, json_data):
        return type("JsonObj", (), json_data)

    def text2obj(self, text):
        return self.json2obj(self.text2json(text))


class HtmlTools(object):

    __afanti_question_template = {
        'knowledge': '',    # 知识点
        'paper_name': '',   # 试卷名称
        'question_body': '',        # question_html
        'option_lst': [     # 选项列表
            # {
            #     'value': 'A',
            #     'content': 'content of option A'
            # },
        ],
        'answer': '',         # 答案
        'analy': '',           # 分析
        'comment': '',       # 评价
        'sub_questions': [  # 嵌套的子题目，结构与question相同
            # {
            #     'knowledge': '',
            #     'paper_name': '',
            #     'question_body': 'question content',
            #     'question_body': 'sub question_content',
            #     'option_lst': [],  # this sub question has no option
            #     'answer': 'answer of the sub_question',
            #     'analy': 'analy of the sub_question',
            #     'sub_questions': []  # this sub question has no sub question
            # },
        ]
    }

    @property
    def afanti_question_dict(self):
        return copy.copy(self.__afanti_question_template)

    @property
    def latex_img_re(self):
        return re.compile(r'<img.*?data-mathml-txt=".*?".*?>')

    @property
    def latex_data_re(self):
        return re.compile(r'data-mathml-txt="(.*?)"')

    def get_real_latex(self, latex_string):
        return """<span class="afanti-latex">\( %s \)</span>""".__mod__(latex_string)

    def get_latex_data(self, element):
        return self.latex_data_re.search(element)

    def sub_img(self, matched):
        latex_data = self.get_latex_data(matched.group()).groups()[0]
        return self.get_real_latex(latex_data)

    def deal_latex(self, html):
        return self.latex_img_re.sub(self.sub_img, html) if html else ''

    def judge_answers_map(self, value):
        judge_map = {'T': u'√', 'F': u'x'}
        return judge_map.get(value)

    def option_td(self, option):
        return """<tr><td class="aft_option" data="{0}"><i class="aft_option_value">{0}.</i><div class="aft_option_content"><div>{1}</div></div></td></tr>""".format(option[0], option[1])
        # return """<tr><td class="aft_option" data="{}">{}</td></tr>""".format(option[0], "%s. %s".__mod__(option))

    def options_html(self, options):
        option_html = """<table class="aft_option_wrapper" style="width: 100%;"><tbody class="measureRoot">{}</tbody></table>"""
        return option_html.format(
            seq(options.items())
            .sorted()
            .map(self.option_td)
            .make_string('')
        ) if options else ''

    @property
    def judge_html(self):
        return self.options_html({u'√': '', u'X': ''})

    def gen_option_html(self, option_dict):
        return self.options_html(option_dict)

    def group_answers(self, answers):
        return seq(answers).make_string(' , ')

    def tuple2answer(self, _t):
        return "{}. {}; ".format(_t[0] + 1, self.group_answers(_t[1]))

    def gen_answer_html(self, answer):
        if isinstance(answer, str):
            return answer
        return (seq(answer)
                .enumerate()
                .map(self.tuple2answer)
                .make_string(''))

    @property
    def cloze_re(self):
        return re.compile('(<pos></pos><!--填写区域-->|<pos></pos></填写区域>|<pos></pos>)')

    def sub_cloze(self, matched):
        self.temp_index += 1
        return "%s._______".__mod__(self.temp_index)

    def gen_cloze_html(self, html):
        self.temp_index = 0
        return self.cloze_re.sub(self.sub_cloze, html)

    def gen_cloze_item_options(self, item):
        option_html = """<tr><td class="aft_option" data="%s"><i class="aft_option_value">%s.</i><div class="aft_option_content"><div>%s</div></div></td></tr>""".__mod__
        return (seq(item.items())
                .sorted()
                .map(lambda x: (x[0], x[0], x[1]))
                .map(option_html)
                .make_string(''))

    def gen_cloze_item(self, is_sub=False):
        sub_symbol = ('', '')
        if is_sub:
            sub_symbol = ("(", ")")
        def item_lable(item):
            return """<div class="aft_sub_question_wrapper"><i class="aft_sub_question_value">{0}{2}{1}.</i><div class="aft_sub_question_content"><div class="aft_question">{3}</div>{4}</div></div>""".format(*sub_symbol, *item)
        return item_lable

    def gen_mult_question_html(self, obj):
        return (seq(obj)
                .enumerate(start=1)
                .map(lambda x: (x[0], self.deal_latex(x[1].get('prompt')), self.options_html(x[1].get('options'))))
                .map(self.gen_cloze_item(True))
                .make_string(''))

    def gen_cloze_answer_html(self, obj):
        return (seq(obj)
                .map(lambda x: x.get('answer'))
                .enumerate(start=1)
                .map(lambda x: "%s. %s; ".__mod__(x))
                .make_string(''))

    def gen_diff_type_question(self, instance, html_obj):
        temp_questions = (seq(html_obj.items)
                          .map(instance.tools.json2obj)
                          .map(lambda x: (x, instance.choose_func(x.qtypeId)(x)))
                          .map(lambda x: {
                              'prompt': x[1]['question_html_origin'],
                              'options': x[0].options if hasattr(x[0], 'options') else [],
                              'answer': x[1]['answer_all_html_origin']}))
        new_question = {
            'prompt': self.gen_mult_question_html(temp_questions),
            'answer': (seq(temp_questions)
                       .enumerate(start=1)
                       .map(lambda x: (x[0], '', x[1].get('answer')))
                       .map(self.gen_cloze_item(True))
                       .make_string(''))
        }
        print(temp_questions)
        def multi_part(value):
            return new_question.get(value)
        return multi_part

options = [{'options': {'A': "liked", 'B': "seemed",
                        'C': "sounded", 'D': "felt"}, 'answer': "B", 'score': "0"},
           {'options': {'A': "liked", 'B': "seemed",
                        'C': "sounded", 'D': "felt"}, 'answer': "B", 'score': "0"}]
