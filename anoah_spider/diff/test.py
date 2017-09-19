# -*- coding:utf8 -*-
from __future__ import unicode_literals
import re
from bs4 import BeautifulSoup
import logging

#from tidylib import tidy_fragment


#from afanti_tiku_lib.html.cleaner import Cleaner

# 定义题目的存储格式如下：
# 后期可以加入paper的存储信息(主要是章节信息)
'''
{
    'knowledge': '',    # 知识点
    'paper_name': '',   # 试卷名称
    'question_body': 'question content'.        # question_html
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
    'sub_questions': [  # 嵌套的子题目，结构与question相同
        {
            'knowledge': '',
            'paper_name': '',
            'question_body': 'question content'.
            'question_body': 'sub question_content',
            'option_lst': [],  # this sub question has no option
            'answer': 'answer of the sub_question',
            'analy': 'analy of the sub_question',
            'sub_questions': []  # this sub question has no sub question
        },
        {
            'knowledge': '',
            'paper_name': '',
            'question_body': 'question content'.
            'question_body': 'sub question_content',
            'option_lst': [],  # this sub question has no option
            'answer': 'answer of the sub_question',
            'analy': 'analy of the sub_question',
            'sub_questions': []  # this sub question has no sub question
        },
    ]
}
'''

# 对应的HTML结构如下
'''
<!-- question_html -->

<div class="aft_question">
     question_html
</div>

<table class="aft_option_wrapper">
    <tbody class="measureRoot">
        <tr>
            <td class="aft_option" data="A">
                <i class="aft_option_value">A</i>
                <div class="aft_option_content"></div>
            </td>
        </tr>
        <tr>
            <td class="aft_option" data="B">
                <i class="aft_option_value">B</i>
                <div class="aft_option_content"></div>
            </td>
        </tr>
        <tr>
            <td class="aft_option" data="C">
                <i class="aft_option_value">C</i>
                <div class="aft_option_content"></div>
            </td>
        </tr>
        <tr>
            <td class="aft_option" data="D">
                <i class="aft_option_value">D</i>
                <div class="aft_option_content"></div>
            </td>
        </tr>
    </tbody>
</table>

<div class="aft_sub_question_wrapper">
    <i class="aft_sub_question_value">1.</i>
    <div class="aft_sub_question_content">
        <div class="aft_question">
        ...
        </div>
        <!-- sub question option begin -->
        <!-- sub question option end -->
    </div>
</div>

<!-- question_html end -->


<!-- answer_html begin -->
<div class="aft_answer">
    answer
</div>
<div class="aft_sub_question_wrapper">
    <i class="aft_sub_question_value">1.</i>
    <div class="aft_sub_question_content">
        <div class="aft_answer">answer</div>
    </div>
</div>
<!-- answer_html end -->


<!--analy_html begin -->
<div class="aft_analy">
    analy
</div>
<div class="aft_sub_question_wrapper">
    <i class="aft_sub_question_value">1.</i>
    <div class="aft_sub_question_content">
        <div class="aft_analy">answer</div>
    </div>
</div>
<!--analy_html end -->


<!-- comment begin -->
<div class="aft_comment">
    comment
</div>
<div class="aft_sub_question_wrapper">
    <i class="aft_sub_question_value">1.</i>
    <div class="aft_sub_question_content">
        <div class="aft_comment">answer</div>
    </div>
</div>
<!-- comment end -->
'''



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


class Question(object):
    '''
    试题对象
    将题目转换为题库需要的文本格式
    '''
    def __init__(self, **kwargs):
        self._question_id = -1
        self._question_type = ''
        self._difficulty = ''
        self.source = ''
        self._option_lst = []
        self._sub_question_lst = []
        if kwargs:
            self._question_body = kwargs['question_body']
            option_lst = kwargs.get('option_lst', [])
            for option_dict in option_lst:
                option_node = Option(option_dict['value'], option_dict['content'])
                self.append_option(option_node)
            for sub_question in kwargs.get('sub_question_lst', []):
                question = Question(**sub_question)
                self.append_sub_question(question)
            self._answer = kwargs.get('answer', '')
            self._analy = kwargs.get('analy', '')
            self._comment = kwargs.get('comment', '')
        else:
            self._question_body = ''
            self._answer = ''
            self._analy = ''
            self._comment = ''
        self._question_abbr_text = ''

    @property
    def question_id(self):
        return self._question_id

    @question_id.setter
    def question_id(self, question_id):
        try:
            question_id = int(question_id)
        except Exception:
            raise
        self._question_id = question_id

    @property
    def question_type(self):
        return self._question_type

    @question_type.setter
    def question_type(self, question_type):
        self._question_type = question_type

    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, difficulty):
        self._difficulty = difficulty

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    @property
    def question_body(self):
        return self._question_body

    @question_body.setter
    def question_body(self, question_body):
        self._question_body = question_body

    @property
    def option_lst(self):
        return self._option_lst

    def append_option(self, option_node):
        if not isinstance(option_node, Option):
            raise Exception('option_node is not instance of Option')
        self._option_lst.append(option_node)

    @property
    def sub_question_lst(self):
        return self._sub_question_lst

    def append_sub_question(self, sub_question):
        if not isinstance(sub_question, Question):
            raise Exception('sub_question object is not instance of Question')
        self._sub_question_lst.append(sub_question)

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, answer):
        self._answer = answer

    @property
    def analy(self):
        return self._analy

    @analy.setter
    def analy(self, analy):
        self._analy = analy

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, comment):
        self._comment = comment

    def to_html(self):
        qc = QuestionConvetor()
        return qc.render_html(self)

    def normialize(self):
        qc = QuestionConvetor()
        return qc.wrap_question(self)

    def __str__(self):
        if not self.__question_abbr_text:
            soup = BeautifulSoup(self._question_body, 'html.parser')
            self._question_abbr_text = soup.text[:100]
        return '<Question %s>' % self._question_abbr_text



class QuestionConvetor(object):
    def __init__(self):
        pass

    def wrap_question(self, question_dict, is_sub_question=False):
        if not isinstance(question_dict, Question):
            raise QuestionTypeError('warp_question function need a Question instance')
        wrapped_question_dict = {}
        # render sub_question
        sub_question_lst = []
        if question_dict.sub_question_lst:
            sub_question_lst = map(
                self.wrap_question,
                question_dict.sub_question_lst,
                (True for _ in question_dict.sub_question_lst)
            )

        # question_id
        wrapped_question_dict['question_id'] = question_dict.question_id

        # question_html = question_html + option_html + sub_question_html
        question_body = question_dict.question_body
        # get option_html
        question_body = self.wrap_html_by_div('aft_question', question_body)
        has_question_body = question_body and True or False
        option_html = self.render_option(question_dict.option_lst, has_question_body)
        # get sub_question_html
        sub_question_body = self.get_sub_question_html('question_body', sub_question_lst)
        question_body = question_body + option_html + sub_question_body
        question_body = self.make_tag_close(question_body)
        wrapped_question_dict['question_body'] = question_body

        # answer
        answer_html = question_dict.answer
        answer_html = self.wrap_html_by_div('aft_answer', answer_html)
        sub_question_answer = self.get_sub_question_html('answer', sub_question_lst)
        answer_html += sub_question_answer
        answer_html = self.make_tag_close(answer_html)
        wrapped_question_dict['answer'] = answer_html

        # analy
        analy_html = question_dict.analy
        analy_html = self.wrap_html_by_div('aft_analy', analy_html)
        sub_question_analy = self.get_sub_question_html('analy', sub_question_lst)
        analy_html += sub_question_analy
        analy_html = self.make_tag_close(analy_html)
        wrapped_question_dict['analy'] = analy_html

        # comment
        comment_html = question_dict.comment
        comment_html = self.wrap_html_by_div('aft_comment', comment_html)
        sub_question_comment = self.get_sub_question_html('comment', sub_question_lst)
        comment_html += sub_question_comment
        comment_html = self.make_tag_close(comment_html)
        wrapped_question_dict['comment'] = comment_html

        return wrapped_question_dict


    def eraser_old_question_no(self, html):
        # 删除question_html中的题目序号，特征为文本起始处的\d{1,2}\.
        # 需要避免误提取小数，所以该组合后不能有数字。
        pattern = re.compile(r'<[^<>]+>(\d{1,2}\.)(?!\d)', flags=re.U)
        html = pattern.sub('', html)
        return html

    def get_sub_question_html(self, coloum, sub_question_lst):
        '''
        返回sub_question的指定字段的HTML文本组合
        '''
        res_html = ''
        tmp_id = 1
        for sub_question in sub_question_lst:
            if sub_question['question_id'] > 0:
                tmp_id = sub_question['question_id']
            tmp_html = sub_question[coloum]
            # 删除原有小题号
            tmp_html = self.eraser_old_question_no(tmp_html)
            if not tmp_html:
                continue
            tmp_html = '<div class="aft_sub_question_wrapper">'\
                '<i class="aft_sub_question_value">%s.</i>'\
                '<div class="aft_sub_question_content">%s</div>'\
                '</div>' % (tmp_id, tmp_html)
            res_html += tmp_html
            tmp_id += 1
        return res_html


    def clean_html(self, html):
        '''
        清理HTML中多余的内容，包括空格、空标签
        '''
        if not html:
            return html
        html = self.make_tag_close(html)
        html = re.sub(r'((?<=(?:<p>))(?:&nbsp;)+)', '&nbsp;',
                        html, flags=re.U | re.I)

        # del 
        #cleaner = Cleaner()
        #cleaner.feed(html)
        #html = cleaner.get_html()
        # del whitespace
        html = re.sub(r'\s{2,}', ' ', html, flags=re.U)
        html = re.sub(r'(?:&nbsp;){2,}', '&nbsp;', html)
        html = re.sub(r'(?<=(?:&nbsp;))\s+', '', html, flags=re.I | re.U)
        html = re.sub(r'\s+(?=(?:&nbsp;))', '', html, flags=re.I | re.U)

        # 删除<p><img></p>这样的组合
        html = re.sub(r'<p[^<>]*?>(<img[^<>]*?>)<\s*/p\s*>', lambda m: m.group(1), html, flags=re.U | re.I|re.S)

        # delete blank tag. <p> <span> </span></p>
        pattern = re.compile('(<(?P<tag>[^<>u/][^<>/]*)\s*?[^<>/]*?>(?:&nbsp;|\s)*?</(?P=tag)\s*?>)', flags=re.I|re.U)
        while pattern.findall(html):
            html = pattern.sub('', html)
        return html


    # option_html
    def render_option(self, option_lst, has_question_body):
        if not option_lst:
            return ''

        if has_question_body:
            option_html_begin_tag = '<table class="aft_option_wrapper" style="width: 100%;">'\
            '<tbody class="measureRoot">'
        else:
            option_html_begin_tag = '<table class="aft_option_wrapper no_question_content" '\
            'style="width: 100%;"><tbody class="measureRoot">'
        option_html_end_tag = '</tbody></table>'

        option_to_html = lambda option: \
            '<tr><td class="aft_option" data="{value}">'\
            '<i class="aft_option_value">{value}.</i>'\
            '<div class="aft_option_content">{content}</div>'\
            '</td></tr>'.format(value=option.value, content=option.content)
        option_middle_html = ''.join(map(option_to_html, option_lst))
        option_html = option_html_begin_tag + option_middle_html + option_html_end_tag
        return option_html

    def wrap_html_by_div(self, _type, html):
        '''
        为一段HTML添加一个class=_type的div父标签
        '''
        html = self.clean_html(html)
        html = html.strip()
        html = re.sub(
            r'^<div[^<>]*>([^<>]+?)</div>$', lambda m: m.group(1),
            html, flags=re.U | re.I | re.S)
        if html:
            html = '<div class="{0}">{1}</div>'.format(_type, html)
        return html

    def make_tag_close(self, html):
        '''
        try:
            html, errors = tidy_fragment(html, options={'output-html':1, 'doctype': 'html5', 'indent': 0})
        except Exception as err:
            raise err
        '''
        return html



dic = {
    'knowledge': '',    # 知识点
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
    'answer': '',         # 答案
    'analy': 'analy of the question',           # 分析
    'comment': 'comment of the question',       # 评价
    'sub_questions': [  # 嵌套的子题目，结构与question相同
        {
            'knowledge': '',
            'paper_name': '',
            'question_body': 'question content',
            'question_body': 'sub question_content',
            'option_lst': [],  # this sub question has no option
            'answer': 'answer of the sub_question',
            'analy': 'analy of the sub_question',
            'sub_questions': []  # this sub question has no sub question
        },
        {
            'knowledge': '',
            'paper_name': '',
            'question_body': 'question content',
            'question_body': 'sub question_content',
            'option_lst': [],  # this sub question has no option
            'answer': 'answer of the sub_question',
            'analy': 'analy of the sub_question',
            'sub_questions': []  # this sub question has no sub question
        },
    ]
}

new_question_dict = Question(**dic).normialize()
print(new_question_dict)