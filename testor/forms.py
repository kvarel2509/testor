from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import Answer, Question, TestObj


class QuestionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.obj = kwargs.pop('obj')
        super().__init__(*args, **kwargs)
        if self.obj.many:
            self.fields['answer'] = forms.ModelMultipleChoiceField(
                queryset=self.obj.answer_set.all(),
                label='Варианты ответа',
                widget=forms.CheckboxSelectMultiple
            )
        else:
            self.fields['answer'] = forms.ModelChoiceField(
                queryset=self.obj.answer_set.all(),
                label='Варианты ответа',
                widget=forms.RadioSelect
            )


class CustomInlineFormSet(BaseInlineFormSet):
    def clean(self):
        print(self.cleaned_data)
        positive_flag = False
        negative_flag = False
        for i in self.cleaned_data:
            if i:
                i = i['status']
                print(i)
                if i and not positive_flag:
                    positive_flag = True
                elif not i and not negative_flag:
                    negative_flag = True
        if positive_flag and negative_flag:
            return self.cleaned_data
        raise ValidationError('Проверьте, чтобы был и правильный и неправильный ответ')