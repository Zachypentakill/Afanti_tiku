from django.contrib import admin
from .models import AnoahQuestion

@admin.register(AnoahQuestion)
class AnoahQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_id','spider_source','spider_url']
    search_fields = ['question_id','spider_source','spider_url']
