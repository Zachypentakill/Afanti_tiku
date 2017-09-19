from utils import BaseMixin
from parsers.models import *
from functional import seq
from functools import partial
import re


class MathLabel(BaseMixin):
    NAME = "math_label"
    model = AnoahQuestion
    model_key = "question_id"
    fiels = ['question_html_origin', 'answer_all_html_origin']
    container_size = 500

    def start(self):
        self.run()

    def math_re_sub(self, matched):
        return """<span class="afanti-latex">{}</span>""".format(matched.group())

    @property
    def math_re(self):
        return re.compile('<math>.*?</math>')

    def has_deal(self, html):
        return True if '<span class="afanti-latex">' in html else False

    def has_math(self, question):
        for field in self.fiels:
            html = getattr(question, field)
            if self.math_re.findall(html):
                if not self.has_deal(html):
                    return True
        return False

    def set_math_html(self, question):
        print(question.question_id)
        if not self.has_math(question):
            return
        for field in self.fiels:
            html = getattr(question, field)
            if self.has_deal(html):
                continue
            # print(field, html)
            setattr(question, field, self.math_re.sub(self.math_re_sub, html))
            # print(field,getattr(question, field))
            question.save()


    def multi_update(self, bulk_id):
        questions = AnoahQuestion.objects.filter(question_id__in=bulk_id)
        seq(questions).map(self.set_math_html).to_list()

    def run(self):
        ids = self.get_objects_id()
        bulk_ids = seq(ids).grouped(self.container_size)
        bulk_ids = list(map(list, bulk_ids))
        for bulk_id in bulk_ids:
            self.multi_update(bulk_id)
