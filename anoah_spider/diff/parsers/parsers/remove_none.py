# from parsers.models import *

# ids = AnoahQuestion.objects.all().values_list('question_id')

# fields = ['question_html_origin', 'option_html_origin', 'answer_all_html_origin', 'jieda_origin', 'fenxi_origin', 'dianping_origin']

# for _id in ids:
#     question = AnoahQuestion.objects.get(question_id=_id[0])
#     for field in fields:
#         value = getattr(question, field)
#         if (not value):
#             print(field, question)
#             setattr(question, field, '')
#     question.save()
