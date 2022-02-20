from django import forms
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