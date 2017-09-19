题目格式化工具：
题目基础结构如下图显示：
```json
{
    'question_body': '',
    'option_lst': '',
    'answer': '',
    'analy': '',
    'comment': '',
    'knowledge': '',
    'paper_name': ''
}
```

有些题目可能会复杂一些，即包含小题信息，我们可以将题目进行嵌套，得到一个有层次信息的题目，如下所示：
```json
{
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
     'answer': 'answer of the question',         # 答案
     'analy': 'analy of the question',           # 分析
     'comment': 'comment of the question',       # 评价
     'sub_question_lst': [  # 嵌套的子题目，结构与question相同
         {
             'knowledge': '',
             'paper_name': '',
             'question_body': 'question content',
             'question_body': 'sub question_content',
             'option_lst': [],  # this sub question has no option
             'answer': 'answer of the sub_question',
             'analy': 'analy of the sub_question',
             'sub_question_lst': []  # this sub question has no sub question
         },
         {
             'knowledge': '',
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
```

question_template提供了一个Question类，用于将嵌套的题目转换为非嵌套的题目格式，即题目的各个字段由小题中对应的字段拼接而成。

例子如下：




```ipython
In [1]: from afanti_tiku_lib.question_template.question_template import Question

In [2]: dic = {
   ...:     'knowledge': '',    # 知识点
   ...:     'paper_name': '',   # 试卷名称
   ...:     'question_body': 'question content',        # question_html
   ...:     'option_lst': [     # 选项列表
   ...:         {
   ...:             'value': 'A',
   ...:             'content': 'content of option A'
   ...:         },
   ...:         {
   ...:             'value': 'B',
   ...:             'content': 'content of option B'
   ...:         },
   ...:         {
   ...:             'value': 'C',
   ...:             'content': 'content of option C'
   ...:         },
   ...:         {
   ...:             'value': 'D',
   ...:             'content': 'content of option D'
   ...:         },
   ...:     ],
   ...:     'answer': 'answer of the question',         # 答案
   ...:     'analy': 'analy of the question',           # 分析
   ...:     'comment': 'comment of the question',       # 评价
   ...:     'sub_question_lst': [  # 嵌套的子题目，结构与question相同
   ...:         {
   ...:             'knowledge': '',
   ...:             'paper_name': '',
   ...:             'question_body': 'question content',
   ...:             'question_body': 'sub question_content',
   ...:             'option_lst': [],  # this sub question has no option
   ...:             'answer': 'answer of the sub_question',
   ...:             'analy': 'analy of the sub_question',
   ...:             'sub_question_lst': []  # this sub question has no sub question
   ...:         },
   ...:         {
   ...:             'knowledge': '',
   ...:             'paper_name': '',
   ...:             'question_body': 'question content',
   ...:             'question_body': 'sub question_content',
   ...:             'option_lst': [],  # this sub question has no option
   ...:             'answer': 'answer of the sub_question',
   ...:             'analy': 'analy of the sub_question',
   ...:             'sub_question_lst': []  # this sub question has no sub question
   ...:         },
   ...:     ]
   ...: }

In [3]: # 需要传入一个符合特定规则的字典，字典对应的字段可以在Question类的__init__函数中看到, 重要的字段有question_body, option_lst, answer, analy, comment， sub_question_lst.
   ...: q = Question(**dic)

In [4]: q.normialize()
Out[4]: 
{'analy': '<div class="aft_question_wrapper">analy of the question</div><div class="aft_sub_question_wrapper"><i class="aft_sub_question_value">1.</i><div class="aft_sub_question_content">analy of the sub_question</div></div><div class="aft_sub_question_wrapper"><i class="aft_sub_question_value">2.</i><div class="aft_sub_question_content">analy of the sub_question</div></div>',
 'answer': '<div class="aft_question_wrapper">answer of the question</div><div class="aft_sub_question_wrapper"><i class="aft_sub_question_value">1.</i><div class="aft_sub_question_content">answer of the sub_question</div></div><div class="aft_sub_question_wrapper"><i class="aft_sub_question_value">2.</i><div class="aft_sub_question_content">answer of the sub_question</div></div>',
 'comment': '<div class="aft_question_wrapper">comment of the question</div>',
 'difficulty': '',
 'question_body': '<div class="aft_question_wrapper">question content</div><table class="aft_option_wrapper" style="width: 100%;"><tbody class="measureRoot"><tr><td class="aft_option" data="A"><i class="aft_option_value">A.</i><div class="aft_option_content">content of option A</div></td></tr><tr><td class="aft_option" data="B"><i class="aft_option_value">B.</i><div class="aft_option_content">content of option B</div></td></tr><tr><td class="aft_option" data="C"><i class="aft_option_value">C.</i><div class="aft_option_content">content of option C</div></td></tr><tr><td class="aft_option" data="D"><i class="aft_option_value">D.</i><div class="aft_option_content">content of option D</div></td></tr></tbody></table><div class="aft_sub_question_wrapper"><i class="aft_sub_question_value">1.</i><div class="aft_sub_question_content">sub question_content</div></div><div class="aft_sub_question_wrapper"><i class="aft_sub_question_value">2.</i><div class="aft_sub_question_content">sub question_content</div></div>',
 'question_id': -1,
 'source': -1}

```


更详细的例子可以在`test/question_template/`文件夹中看到：question.json为符合要求的题目字典的json文件，question.html为转换格式后成的网页文件，static为对应的静态文件。
可以通过修改question.json文件后运行test_question_template.py脚本来测试自定义题目字典
