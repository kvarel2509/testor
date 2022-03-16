import requests
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import generic

from .forms import *
from .mixin import TopicListMixin


class TestListAllView(generic.View, TopicListMixin):

    def get(self, request, *args, **kwargs):
        test_list = requests.get('http://127.0.0.1:8000/api/test-list/').json()
        return render(request, 'api_testor/main.html', context={
            'topic_list': self.get_topic_list(),
            'test_list': test_list,
            'topic_all': True,
        })


class TestListFilterView(generic.View, TopicListMixin):

    def get(self, request, *args, **kwargs):
        test_list = requests.get(f'http://127.0.0.1:8000/api/topic/{kwargs["pk"]}').json()
        return render(request, 'api_testor/main.html', context={
            'topic_list': self.get_topic_list(),
            'test_list': test_list['tests'],
            'topic_all': False,
            'topic_name': test_list['name']
        })


class TestDetailView(generic.TemplateView, TopicListMixin):
    template_name = 'api_testor/test_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic_list'] = self.get_topic_list()
        context['object'] = requests.get(f'http://127.0.0.1:8000/api/test/{kwargs["pk"]}').json()
        return context


class TestRunView(generic.View, TopicListMixin):

    def get_token(self):
        token_data = requests.get(f'http://127.0.0.1:8000/api/get-token/{self.request.user.pk}/').json()
        token = token_data['token']
        return {'Authorization': token}

    def get(self, request, *args, **kwargs):
        data = requests.get(f'http://127.0.0.1:8000/api/test/{kwargs["pk"]}/run/', headers=self.get_token()).json()
        if data['question']:
            form = AnswerForm(obj=data['question'])
            return render(request, 'api_testor/run_test.html', context={'data': data,
                                                                        'topic_list': self.get_topic_list(),
                                                                        'form': form
                                                                        })
        else:
            return render(request, 'api_testor/result_test.html', context={'data': data,
                                                                           'topic_list': self.get_topic_list()})

    def post(self, request, *args, **kwargs):
        data = {'answers': request.POST.getlist('answer')}
        print(data)
        requests.post(f'http://127.0.0.1:8000/api/test/{kwargs["pk"]}/run/',
                      headers=self.get_token(),
                      data=data,
                      ).json()
        return redirect('api_test_run', pk=kwargs['pk'])


class TestCreateView(generic.View, TopicListMixin):

    def get(self, request, *args, **kwargs):
        form = TestCreateForm(topic_list=self.get_topic_list())
        return render(request, 'api_testor/test_create.html', context={'form': form,
                                                                       'topic_list': self.get_topic_list()})

    def post(self, request, *args, **kwargs):
        form = TestCreateForm(request.POST, topic_list=self.get_topic_list())
        if request.POST.getlist('topic'):
            data = request.POST.copy()
            data['topic'] = request.POST.getlist('topic')
            obj = requests.post('http://127.0.0.1:8000/api/test-list/', json=data)
            if obj.status_code == 201:
                return redirect('api_question_create', pk=obj.json()['pk'])
        return render(request, 'api_testor/test_create.html', context={'form': form,
                                                                       'topic_list': self.get_topic_list()})


class QuestionCreateView(generic.View, TopicListMixin):

    def get(self, request, *args, **kwargs):
        form1 = QuestionCreateForm(prefix='question')
        form2 = AnswerCreateFormSet(prefix='answer')
        return render(request, 'api_testor/question_create.html', context={'form1': form1, 'form2': form2,
                                                                           'topic_list': self.get_topic_list()})

    def post(self, request, *args, **kwargs):
        print(request.POST)
        form1 = QuestionCreateForm(request.POST, prefix='question')
        form2 = AnswerCreateFormSet(request.POST, prefix='answer')
        if form1.is_valid() and form2.is_valid():
            data = form1.cleaned_data
            data['answer'] = form2.cleaned_data
            resp = requests.post(f'http://127.0.0.1:8000/api/test/{kwargs["pk"]}/question-list/',
                                 json=data)
            if resp.status_code == 201:
                if 'next' in request.POST:
                    return redirect('api_question_create', pk=kwargs['pk'])
                else:
                    return redirect('api_test_list')
            return render(request, 'api_testor/question_create.html', context={'form1': form1,
                                                                               'form2': form2,
                                                                               'mess': resp.json()['answer']})


class RegistrationView(generic.View, TopicListMixin):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, 'api_testor/login.html', context={'form': form, 'topic_list': self.get_topic_list()})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['password'] = form.cleaned_data['password1']
            obj = requests.post('http://127.0.0.1:8000/api/', json=form.cleaned_data)
            if obj.status_code == 200:
                login(form.cleaned_data)
                return redirect('api_test_list')
        return render(request, 'api_testor/login.html', context={'form': form, 'topic_list': self.get_topic_list()})