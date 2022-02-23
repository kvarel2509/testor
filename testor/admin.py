from django.contrib import admin
from django.db import models
from .models import *
from .forms import *


class AnswerInline(admin.TabularInline):
    model = Answer
    formset = CustomInlineFormSet


class QuestionInline(admin.StackedInline):
    model = Question


@admin.register(TestObj)
class TestObjAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основные поля', {'fields': ('name', 'description'), 'description': 'Эти поля лучше заполнить'}),
        ('Доп поля', {'fields': ('topic', 'test_display')})
    )
    list_display = ('name', 'description', 'upper_name_test',)
    # list_display_links = ('name', 'upper_name_test')
    list_filter = ('topic',)
    list_per_page = 10
    list_max_show_all = 100
    # ordering = ('-name',)
    # prepopulated_fields = {'description': ('name', )}
    autocomplete_fields = ('topic',)
    readonly_fields = ('test_display',)
    search_fields = ('name', 'topic__name')
    inlines = (QuestionInline,)

    def test_display(self, obj):
        return 5

    @admin.display(description='Custom description')
    def upper_name_test(self, obj):
        return f'{obj.name} - ОПИСАНИЕ {obj.description}'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline, ]
    list_display = ['text', 'many']