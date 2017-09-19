# from parsers.models import AnoahQuestion
# import re
# import oss2

# oss_AccessKeyId = "kI0OZGuxBI7ZmFAX"
# oss_AccessKeySecret = "NEaDBx2tJ2s5Tdt1Sh3k5e7f7f58wF"
# oss_endpoint = "oss-cn-beijing-internal.aliyuncs.com"
# oss_bucket = "afanti-question-images"

# auth = oss2.Auth(oss_AccessKeyId, oss_AccessKeySecret)
# bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket)


# class UpdateOssImage(object):
#     NAME = "oss_image"
#     model = AnoahQuestion
#     model_key = 'question_id'
#     fields = ['question_html_origin', 'answer_all_html_origin']

#     def start(self):
#         self.run()

#     def has_img(self, html):
#         return True if "http://qimg.afanti100.com" in html else False 

#     def img_re(self, html):
#         return re.compile(r'"http://qimg.afanti100.com.*?"').findall(html)

#     def run(self):
#         image_urls = []
#         questions = AnoahQuestion.objects.all()[:12000]
#         for question in questions:
#             for field in self.fields:
#                 html = getattr(question, field)
#                 if not html:
#                     continue
#                 if not self.has_img(html):
#                     continue
#                 print(self.img_re(html))
#                 image_urls += self.img_re(html)
#         return image_urls
# import time

# oss_path = "data/image/question_image/71"
# online_images = oss2.ObjectIterator(bucket,prefix=oss_path)
# online_md5 = [old_key for old_key in online_images]
# online_md5 = list(map(lambda x:x.key,online_md5))
# for old_key in online_md5:
#     new_key = old_key.replace('71','75')
#     print(new_key)
#     requests.get("http://baidu.com")    
#     old_obj = bucket.get_object(old_key)
#     print(old_obj)
#     try:
#         bucket.put_object(new_key,old_obj)
#     except:
#         pass

# for obj in online_images:
#     file_name = (obj.key.split('/')[-1])
#     online_md5.append(file_name)


