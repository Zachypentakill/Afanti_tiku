from django.db.utils import IntegrityError
from parsers.models import AnoahQuestion
from clawer.models import AnoahPageHtml
from functional import seq
from functools import partial, wraps
from utils import BaseMixin, HtmlTools, ObjectTools
import json


def question_dict_warpper(func):
    @wraps(func)
    def warpper(instance, obj):
        deal_latex = instance.tools.deal_latex
        deal_option = instance.tools.gen_option_html
        deal_answer = instance.tools.gen_answer_html
        question_dict = {
            'question_html_origin': deal_latex(obj.prompt),
            'option_html_origin': deal_latex(deal_option(obj.options if hasattr(obj, 'options') and obj.options else {})),
            'answer_all_html_origin': deal_latex(deal_answer(obj.answer if hasattr(obj, 'answer') and obj.answer else '')),
            'fenxi_origin': deal_latex(obj.parse),
        }
        func(instance, obj, question_dict)
        return question_dict
    return warpper


class AnoahManger(type):

    def __new__(cls, names, bases, attrs):
        @question_dict_warpper
        def qtype(self, obj, question_dict):
            print("qtype_%s" % obj.qtypeId)
            return {}
        exit_names = list(map(lambda x: x[0], attrs.items()))
        attrs.update(seq(range(50))
                     .map(lambda x: "qtype_%s" % x)
                     .filter(lambda x: x not in exit_names)
                     .map(lambda x: (x, qtype))
                     )
        return super(AnoahManger, cls).__new__(cls, names, bases, attrs)


class AnoahParser(BaseMixin, metaclass=AnoahManger):
    NAME = 'anoah'
    model = AnoahPageHtml
    model_key = 'html_id'
    tools = type("AnoahTools", (HtmlTools, ObjectTools), {})()
    __metaclass__ = AnoahManger

    def __init__(self):
        self.qtype_funcs = (seq(dir(self))
                            .filter(lambda x: 'qtype_' in x))
        self.exit_keys = AnoahQuestion.objects.all().values_list('spider_url')
        self.exit_keys = map(lambda x: x[0], self.exit_keys)

    @question_dict_warpper
    def qtype_1(self, obj, question_dict):
        print('qtype_1')
        question_dict['option_html_origin'] = self.tools.judge_html
        question_dict['answer_all_html_origin'] = self.tools.judge_answers_map(
            obj.answer)
        if not question_dict['answer_all_html_origin']:
            question_dict['answer_all_html_origin'] = obj.answer

    @question_dict_warpper
    def qtype_2(self, obj, question_dict):
        print('qtype_2')

    @question_dict_warpper
    def qtype_3(self, obj, question_dict):
        print('qtype_3')

    @question_dict_warpper
    def qtype_4(self, obj, question_dict):
        pass

    @question_dict_warpper
    def qtype_5(self, obj, question_dict):
        question_dict['question_html_origin'] = self.tools.gen_cloze_html(
            question_dict['question_html_origin'])

    @question_dict_warpper
    def qtype_6(self, obj, question_dict):
        pass

    @question_dict_warpper
    def qtype_7(self, obj, question_dict):
        pass

    def qtype_8(self, obj):
        return {}  # not need

    def qtype_9(self, obj):
        return {}  # not complete yeah

    @question_dict_warpper
    def qtype_11(self, obj, question_dict):
        question_dict[
            'question_html_origin'] = self.tools.gen_cloze_html(
            question_dict['question_html_origin']) + self.tools.gen_mult_question_html(obj.items)
        question_dict[
            'answer_all_html_origin'] = self.tools.gen_cloze_answer_html(obj.items)

    @question_dict_warpper
    def qtype_12(self, obj, question_dict):
        print("qtype_12")
        # question_dict[
        #     'question_html_origin'] = self.tools.gen_cloze_html(
        #     question_dict['question_html_origin']) + self.tools.gen_mult_question_html(obj.items)
        multi_part = self.tools.gen_diff_type_question(self, obj)
        question_dict['question_html_origin'] += multi_part('prompt')
        question_dict['answer_all_html_origin'] += multi_part('answer')

    @question_dict_warpper
    def qtype_30(self, obj, question_dict):
        print('qtype_30')

    def choose_func(self, _type):
        return getattr(self, list(filter(lambda x: "qtype_%s" % _type == x, self.qtype_funcs))[0])

    def is_question_exit(self, key):
        return True if key in self.exit_keys else False

    def init_question(self, question):
        def _get_obj(obj):
            question.spider_url = obj.key
            question.html_id = obj.html_id
        return _get_obj

    def create_question(self, obj):
        question = AnoahQuestion()
        self.init_question(question)(obj)
        def assign_dict(question_dict):
            [setattr(question, k, v) for k, v in question_dict.items()]
            len(question_dict) and question.save()
        return assign_dict

    def run_parser(self, _id):
        obj = self.get_obj(_id)
        question = self.create_question(obj)
        html_obj = self.tools.text2obj(obj.html)
        if html_obj.qtypeId in ['1','2','3','4','5','6','7','8','11','30']:
        # if html_obj.qtypeId in ['12']:
            print(obj.source_id)
            result = self.choose_func(html_obj.qtypeId)(html_obj)
            question = question(result)

    def remove_ids(self, ids):
        exit_ids = AnoahQuestion.objects.all().values_list('html_id')
        exit_ids = list(map(lambda x: x[0], exit_ids))
        return list(set(ids) - set(exit_ids))

    def start(self):
        self.run()

    def run(self):
        ids = self.get_objects_id()
        ids = self.remove_ids(ids)
        list(map(self.run_parser, ids))
