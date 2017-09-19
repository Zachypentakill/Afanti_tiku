from django.contrib import admin
from .models import *
# Register your models here.
# @admin.register(QyzkPageHtml)
class BaseSpiderTaskAdmin(admin.ModelAdmin):
    list_display = ['task_name','url']
    search_fields = ['task_name','url']

admin.site.register(BaseSpiderTask,BaseSpiderTaskAdmin)