from django.db.models import Case, When, F, Value, Exists
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect
from django.views import generic

from .forms import QuestionForm
from .models import *


class MainView(generic.ListView):
    template_name = 'testor/themes-list.html'

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return TestObj.objects.filter(pk=self.kwargs['pk'])
        return TestObj.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Список тем'
        context['topics'] = Topic.objects.all()
        context['topic_all'] = False if 'pk' in self.kwargs else True
        return context


class TestDetailView(generic.DetailView):
    extra_context = {'title': 'Инфо по тесту'}

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return TestObj.objects.all().annotate(button=Case(
                When(~Exists(Testing.objects.filter(
                    user=self.request.user, testobj=self.kwargs['pk'])),
                     then=Value('Начать')),
                When(Exists(Testing.objects.filter(
                    user=self.request.user, testobj=self.kwargs['pk'], total__gt=F('distant'))),
                    then=Value('Продолжить')),
                When(Exists(Testing.objects.filter(
                    user=self.request.user, testobj=self.kwargs['pk'], total=F('distant'))), then=Value('Результат')),
                default=Value('Sign in'), ))
        else:
            return TestObj.objects.all()


class CreateTestingView(generic.View):

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = User.objects.get(pk=self.request.user.pk)
            test = TestObj.objects.get(pk=self.kwargs['pk'])
            # Проверяем, есть ли в базе такой уже начатый тест
            testing = Testing.objects.filter(user=user, testobj=test)
            if not testing.exists():
                # Если нет, мы его создаем, потом делаем редирект на тест
                new_test = Testing()
                new_test.user = user
                new_test.testobj = test
                new_test.question = list(new_test.testobj.question_set.all().values('pk'))
                new_test.total = len(new_test.question)
                new_test.diagram = [None for i in range(new_test.total)]
                new_test.save()
            else:
                # Если тест есть, мы делаем на него редирект
                new_test = testing.get()
            return redirect('testing', pk=new_test.pk)
        return Http404


class TestingView(generic.TemplateView, generic.detail.SingleObjectMixin):
    template_name = 'testor/testing.html'
    model = Testing

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user != request.user:
            return HttpResponseForbidden()
        if self.object.distant == self.object.total:
            return redirect('result', pk=self.object.pk)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.object.question[-1]['pk'])
        context['form'] = QuestionForm(obj=context['question'])
        context['diagram'] = self.object.diagram
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        question_id = obj.question[-1]['pk']
        question_obj = Question.objects.get(pk=question_id)
        form = QuestionForm(request.POST, obj=question_obj)
        if form.is_valid():
            obj.distant += 1
            del obj.question[-1]
            answers_positive = question_obj.answer_set.filter(status=True)
            answers_data = form.cleaned_data['answer'] if question_obj.many else [form.cleaned_data['answer']]
            for answer_positive in answers_positive:
                if answer_positive not in answers_data or len(answers_data) != len(answers_positive):
                    obj.diagram[obj.distant - 1] = False
                    obj.save()
                    return redirect('testing', pk=obj.pk)
            obj.diagram[obj.distant - 1] = True
            obj.point += 1
            obj.save()
        return redirect('testing', pk=obj.pk)


class ResultView(generic.detail.SingleObjectMixin, generic.TemplateView):
    template_name = 'testor/result.html'
    model = Testing

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['percent'] = self.object.point / self.object.total * 100
        return context
