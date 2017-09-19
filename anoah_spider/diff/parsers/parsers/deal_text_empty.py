from parsers.models import AnoahQuestion
from utils import BaseMixin
from bs4 import BeautifulSoup
from functional import seq


class CleanEmpty(BaseMixin):
    NAME = "text_empty"
    model = AnoahQuestion
    model_key = 'question_id'
    fields = ['question_html','question_html_origin','answer_all_html_origin','answer_all_html']
    container_size = 1000

    def is_empty(self, question):
        for field in self.fields:
            html = getattr(question, field)
            if not html:
                return True
            bs = BeautifulSoup(html)
            if bs.text == '':
                return True
            return True if bs.text == '' else False

    def run_parser(self, question):
        print(question.question_id)
        question.is_rendered = 1994
        question.flag = 1994
        question.save()

    def multi_update(self, bulk_id):
        questions = AnoahQuestion.objects.filter(question_id__in=bulk_id)
        seq(questions).filter(self.is_empty).map(self.run_parser).to_list()

    def start(self):
        self.run()

    def run(self):
        ids = self.get_objects_id()
        bulk_ids = seq(ids).grouped(self.container_size)
        bulk_ids = list(map(list, bulk_ids))
        for bulk_id in bulk_ids:
            self.multi_update(bulk_id)
