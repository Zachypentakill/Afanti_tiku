from utils import BaseMixin
from parsers.models import *
from functional import seq
from functools import partial
import re


class RmoveRed(BaseMixin):
    NAME = "remove_red"
    model = AnoahQuestion
    model_key = "question_id"
    # fiels = ['question_html_origin','question_html','answer_all_html','answer_all_html_origin']
    fiels = ['option_html_origin','option_html_origin','fenxi_origin','fenxi_origin']
    container_size = 1000

    def start(self):
        self.run()

    def remove_red_style(self, html):
        return html.replace('style="color:red"','')

    def has_red(self, question):
        return seq(self.fiels).map(partial(getattr, question)).filter(lambda x:'style="color:red"' in x)

    def set_red_html(self, question):
        print(question.question_id)
        for field in self.fiels:
            html = getattr(question, field)
            print(html)
            html = self.remove_red_style(html)
            setattr(question, field, html)
            print(getattr(question, field))
        question.save()

    def multi_update(self, bulk_id):
        questions = AnoahQuestion.objects.filter(question_id__in=bulk_id)
        seq(questions).filter(self.has_red).map(self.set_red_html).to_list()

    def run(self):
        ids = self.get_objects_id()
        bulk_ids = seq(ids).grouped(self.container_size)
        bulk_ids = list(map(list, bulk_ids))
        for bulk_id in bulk_ids:
            self.multi_update(bulk_id)
