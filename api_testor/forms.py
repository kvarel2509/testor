from django import forms
from django.forms import formset_factory
from django.contrib.auth.forms import UserCreationForm


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)


class AnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.obj = kwargs.pop('obj')
        super().__init__(*args, **kwargs)
        if self.obj['many']:
            self.fields['answer'] = forms.ChoiceField(
                choices=((int(i['pk']), i['text']) for i in self.obj['answer']),
                label='Варианты ответа',
                widget=forms.CheckboxSelectMultiple
            )
        else:
            self.fields['answer'] = forms.ChoiceField(
                choices=((int(i['pk']), i['text']) for i in self.obj['answer']),
                label='Варианты ответа',
                widget=forms.RadioSelect
            )


class TestCreateForm(forms.Form):
    name = forms.CharField(label='Название')
    description = forms.CharField(label='Описание')

    def __init__(self, *args, **kwargs):
        self.topic_list = kwargs.pop('topic_list')
        super().__init__(*args, **kwargs)
        self.fields['topic'] = forms.ChoiceField(
            choices=((i['pk'], i['name']) for i in self.topic_list),
            label='Тема теста',
            widget=forms.CheckboxSelectMultiple,
        )


class QuestionCreateForm(forms.Form):
    text = forms.CharField()


class AnswerCreateForm(forms.Form):
    text = forms.CharField(label='Ответ')
    status = forms.BooleanField(label='Правильный?', required=False)


AnswerCreateFormSet = formset_factory(AnswerCreateForm, extra=4)