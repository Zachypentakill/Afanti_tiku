from parsers.models import AnoahQuestion
from utils import BaseMixin
from bs4 import BeautifulSoup
from functional import seq
from functools import partial
import re


class UpdateTableStyle(BaseMixin):
    NAME = "table_style"
    model = AnoahQuestion
    model_key = 'question_id'
    fields = ['question_html','question_html_origin','option_html_origin','option_html_origin','fenxi_origin','fenxi_origin']

    @property
    def table_re(self):
        return re.compile(r'<table style="(.*?)"')

    # def sub_table(self, matched):
    #     return self.get_real_latex(latex_data)

    def replace_style(self, html):
        return self.table_re.sub('<table style="width:100%"',html)

    def setfields(self, obj):
        worker = partial(setattr, obj)
        def getfield(field):
            worker(field, self.replace_style(getattr(obj, field)))
        return getfield

    def has_table(self, obj):
        return (seq(self.fields)
                .map(partial(getattr, obj))
                .filter(lambda x: "<table style=" in x)
                )

    def run(self, obj):
        if not self.has_table(obj):
            return
        print(obj.question_id)
        seq(self.fields).for_each(self.setfields(obj))
        obj.save()
