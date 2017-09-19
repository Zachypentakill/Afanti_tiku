from django.contrib import admin
from .models import *

@admin.register(AnoahPageHtml)
class AnoahPageHtmlAdmin(admin.ModelAdmin):
    list_display = ['html_id','subject', 'key']
    search_fields = ['html_id','subject', 'key']
