from django.contrib import admin
from .models import Document

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 5    # сколько пустых полей показывать
    max_num = 15 # максимум за один раз
