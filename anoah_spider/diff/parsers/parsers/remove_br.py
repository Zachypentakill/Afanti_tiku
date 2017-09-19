from utils import BaseMixin
from parsers.models import *
from functional import seq
from functools import partial
import re


class RmoveBr(BaseMixin):
    NAME = "remove_br"
    model = AnoahQuestion
    model_key = "question_id"
    fiels = ['question_html','question_html_origin','option_html_origin','option_html_origin','fenxi_origin','fenxi_origin']
    container_size = 1000

    def start(self):
        self.run()

    @property
    def br_re(self):
        return re.compile("(^<br>)|(^<br/>)|(<br>$)|(<br/>$)")

    def has_br(self, question):
        return seq(self.fiels).map(partial(getattr, question)).filter(self.br_re.findall)

    def set_re_html(self, question):
        print(question.question_id)
        for field in self.fiels:
            html = getattr(question, field)
            # print(html)
            setattr(question, field, self.br_re.sub('', html))
            # print(getattr(question, field))
            question.save()

    def multi_update(self, bulk_id):
        questions = AnoahQuestion.objects.filter(question_id__in=bulk_id)
        seq(questions).filter(self.has_br).map(self.set_re_html).to_list()

    def run(self):
        ids = self.get_objects_id()
        bulk_ids = seq(ids).grouped(self.container_size)
        bulk_ids = list(map(list, bulk_ids))
        for bulk_id in bulk_ids:
            self.multi_update(bulk_id)
