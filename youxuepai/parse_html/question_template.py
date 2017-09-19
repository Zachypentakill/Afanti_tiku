# -*- coding:utf8 -*-
from __future__ import unicode_literals
import re
try:
    from functools import reduce
except ImportError:
    pass


# 定义题目的存储格式如下：
# 后期可以加入paper的存储信息(主要是章节信息)
'''
{
    'knowledge_point': '',    # 知识点
    'paper_name': '',   # 试卷名称
    'question_body': 'question content',        # question_html
    'option_lst': [     # 选项列表
        {
            'value': 'A',
            'content': 'content of option A'
        },
        {
            'value': 'B',
            'content': 'content of option B'
        },
        {
            'value': 'C',
            'content': 'content of option C'
        },
        {
            'value': 'D',
            'content': 'content of option D'
        },
    ],
    'answer': 'answer of the question',         # 答案
    'analy': 'analy of the question',           # 分析
    'comment': 'comment of the question',       # 评价
    'sub_question_lst': [  # 嵌套的子题目，结构与question相同
        {
            'knowledge_point': '',
            'paper_name': '',
            'question_body': 'question content',
            'question_body': 'sub question_content',
            'option_lst': [],  # this sub question has no option
            'answer': 'answer of the sub_question',
            'analy': 'analy of the sub_question',
            'sub_question_lst': []  # this sub question has no sub question
        },
        {
            'knowledge_point': '',
            'paper_name': '',
            'question_body': 'question content',
            'question_body': 'sub question_content',
            'option_lst': [],  # this sub question has no option
            'answer': 'answer of the sub_question',
            'analy': 'analy of the sub_question',
            'sub_question_lst': []  # this sub question has no sub question
        },
    ]
}
'''

# 对应的HTML结构如下


class QuestionError(Exception):
    pass


class QuestionTypeError(QuestionError):
    pass


class Option(object):
    '''
    选项对象, 存储选项编号（A、B、C、D等）和选项内容
    '''
    def __init__(self, item_value, item_content):
        self.value = item_value  # 编号
        self.content = item_content  # 选项内容


class Question(dict):
    def __init__(self, is_sub_question=False, **kwargs):
        defaults = {
            'question_id': -1,
            'spider_source': 0,
            'spider_url': '',
            'knowledge_point': '',
            'subject': 0,
            'zhuanti': '',
            'exam_year': '',
            'exam_city': '',
            'question_type': 0,
            'question_quality': 0,
            'paper_name': '',
            'question_body': '',
            'difficulty': '',
            'source': -1,
            'option_lst': [],
            'answer': '',
            'jieda': '',
            'analy': '',
            'comment': '',
            'sub_question_lst': []
        }
        for key, value in kwargs.items():
            if key in defaults:
                defaults[key] = value
        attr_dict = self.__format_question(defaults, is_sub_question)
        self.update(attr_dict)

    def __format_question(self, attr_dict, is_sub_question):
        res_dict = {}
        for key, value in attr_dict.items():
            if key == 'option_lst':
                tmp_option_lst = []
                for option in value:
                    option_node = Option(option['value'], option['content'])
                    tmp_option_lst.append(option_node)
                value = sorted(tmp_option_lst, key=lambda op: op.value)
            elif key == 'sub_question_lst':
                tmp_question_lst = []
                for question in value:
                    question_node = Question(is_sub_question=True, **question)
                    tmp_question_lst.append(question_node)
                value = sorted(tmp_question_lst, key=lambda q: q.question_id)
            elif key == 'knowledge_point':
                # 将子题目中的知识点提取到外层题目中
                if not is_sub_question:
                    def get_knowledge_lst(question_dict):
                        if not question_dict.get('sub_question_lst'):
                            return [question_dict.get('knowledge_point')]
                        else:
                            return [question_dict.get('knowledge_point')] + (
                                        reduce(
                                            lambda l1, l2: l1 + l2,
                                            map(
                                                get_knowledge_lst,
                                                question_dict.get('sub_question_lst'))
                                        ))
                    value_lst = get_knowledge_lst(attr_dict)
                    value_lst = filter(
                                    lambda m: m != None and m != '',
                                    value_lst
                                    )
                    value = ', '.join(set(value_lst))
            res_dict[key] = value
        return res_dict

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Question' object has no attribute '%s'" % key)

    def normialize(self):
        qf = QuestionFormatter()
        return qf.wrap_question(self)


class QuestionFormatter(object):
    def wrap_question(self, question_dict, is_sub_question=False):
        if not isinstance(question_dict, Question):
            raise QuestionTypeError('wrap question func need a Question instance')
        sub_question_lst = question_dict.get('sub_question_lst', [])
        if sub_question_lst:
            wrapped_sub_question_lst = map(
                    self.wrap_question,
                    sub_question_lst, (True, ) * len(sub_question_lst))
        else:
            wrapped_sub_question_lst = []
        wrapped_sub_question_lst = list(wrapped_sub_question_lst)


        wrapped_question_dict = {}

        for key, value in question_dict.items():
            if key in ['option_lst', 'sub_question_lst']:
                continue
            if key in ['question_body', 'answer', 'jieda', 'analy', 'comment']:
                value = self.wrap_html_with_by_div(key, value, is_sub_question)
                if key == 'question_body':
                    has_question_body = value and True or False
                    value += self.wrap_option_lst(question_dict.option_lst, has_question_body)
                value += self.get_sub_question_html(key, wrapped_sub_question_lst)
            wrapped_question_dict[key] = value

        return wrapped_question_dict

    def wrap_html_with_by_div(self, coloum, html, is_sub_question):
        '''为html加上div标签的包裹，如果根标签为div标签，为其添加上对应的class
        '''
        if is_sub_question:
            return html
        class_ = 'aft_question_wrapper'
        html = html.strip()
        if not html:
            return html
        return '<div class="%s">%s</div>' % (class_, html)

    def get_sub_question_html(self, coloum, sub_question_lst):
        res_html = ''
        tmp_id = 1
        for sub_question in sub_question_lst:
            if sub_question['question_id'] > 0:
                tmp_id = sub_question['question_id']
            tmp_html = sub_question[coloum]
            # 删除原有小题号
            #tmp_html = self.eraser_old_question_no(tmp_html)
            if not tmp_html:
                continue
            tmp_html = '<div class="aft_sub_question_wrapper">'\
                '<i class="aft_sub_question_value">%s.</i>'\
                '<div class="aft_sub_question_content">%s</div>'\
                '</div>' % (tmp_id, tmp_html)
            res_html += tmp_html
            tmp_id += 1
        return res_html

    def wrap_option_lst(self, option_lst, has_question_body):
        if not option_lst:
            return ''

        base_class = 'aft_option_wrapper'
        if not has_question_body:
            base_class += ' no_question_content'
        option_begin = '<table class="{}" style="width: 100%;">'\
                '<tbody class="measureRoot">'.format(base_class)
        option_end = '</tbody></table>'

        option_to_html = lambda option: \
            '<tr><td class="aft_option" data="{value}">'\
            '<i class="aft_option_value">{value}.</i>'\
            '<div class="aft_option_content">{content}</div>'\
            '</td></tr>'.format(value=option.value, content=option.content)
        option_middle = ''.join(map(option_to_html, option_lst))

        html = option_begin + option_middle + option_end
        return html

