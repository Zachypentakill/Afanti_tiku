# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
from afanti_tiku_lib.question_template.question_template import Question, Option


def test_generate_html():
    with open('question.json') as f:
        question_dict = json.load(f)
    question = Question(**question_dict)
    question = question.normialize()
    json_str = json.dumps(question_dict, indent=4, separators=(',', ': '))
    html = ''.join(map(lambda item: '<h2>%s</h2><div>%s</div>' % item, question.items()))
    html = '''<link rel="stylesheet" href="static/question.css">'''\
           '''<script src="http://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js" charset="utf-8"></script>'''\
           '''<link rel="stylesheet" href="https://cdn.jsdelivr.net/pure/0.6.0/pure-min.css">'''\
           '''<meta name="viewport" content="width=device-width, initial-scale=1">'''\
           '''<div class="pure-g">'''\
           '''<div class="pure-u-1-2"><h2>origin json</h2> <pre>%s</pre> </div>'''\
           '''<div class="pure-u-1-2"><h2>question templates</h2> %s </div>'''\
           '''<script src="static/question.js"></script>'''\
           '''</div>''' % (json_str, html)
    with open('question.html', 'w') as f:
        f.write(html)

test_generate_html()
