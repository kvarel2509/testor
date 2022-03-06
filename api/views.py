from django.forms import model_to_dict
from django.shortcuts import redirect
from rest_framework import generics, views, permissions, status
from rest_framework.response import Response
from .serializers import *
from testor.models import *
from rest_framework.generics import get_object_or_404


class RegistrationView(views.APIView):

    def post(self, request, *args, **kwargs):
        ser_data = RegistrationUserSerializer(data=request.data)
        ser_data.is_valid(raise_exception=True)
        user, token = ser_data.save()
        data = ser_data.validated_data
        data['token'] = 'Token ' + token.key
        del data['password']
        return Response(data)


class GetToken(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = RegistrationUserSerializer(obj).data
        data['token'] = 'Token ' + Token.objects.get(user_id=obj.pk).key
        return Response(data=data)


class TestListView(generics.ListCreateAPIView):
    """Показывает все тесты, позволяет создать новый тест"""
    serializer_class = TestListSerializer
    queryset = TestObj.objects.all()


class TestListCategory(generics.ListAPIView):
    """Показывает тесты в рамках категории"""
    serializer_class = TestListSerializer

    def get_queryset(self):
        return TestObj.objects.filter(topic=self.kwargs['pk'])


class QuestionListView(views.APIView):

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(TestObj, pk=kwargs['pk'])
        question_list = obj.question_set.all().prefetch_related()
        new_question_list = []
        for i in question_list:
            i.answers = i.answer_set.all().values('text')
            new_question_list.append(i)
        data = QuestionSerializer(question_list, many=True).data
        return Response({'id': obj.pk, 'Название': obj.name, 'Описание': obj.description, 'questions': data})

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(TestObj, pk=kwargs['pk'])
        data = QuestionSerializer2(data=request.data, many=True)
        data.is_valid(raise_exception=True)
        saved_questions = data.save(testobj=obj)
        result = []
        for i in saved_questions:
            data = model_to_dict(i)
            data['answers'] = i.answer_set.all().values('text', 'status')
            result.append(data)
        return Response(result)


class RunTestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def create_new_testing(self, request, testobj):
        obj = Testing()
        obj.user = request.user
        obj.testobj = testobj
        obj.distant = 0
        obj.point = 0
        obj.question = [question.pk for question in testobj.question_set.all()]
        obj.total = len(obj.question)
        obj.diagram = [None for _ in range(obj.total)]
        obj.save()
        return obj

    def get(self, request, *args, **kwargs):
        testobj = get_object_or_404(TestObj, pk=kwargs['pk'])
        obj = Testing.objects.filter(user=request.user, testobj=testobj)
        if not obj:
            obj = self.create_new_testing(request, testobj)
        else:
            obj = obj.get()
        if obj.question:
            question_pk = obj.question[-1]
            question_obj = Question.objects.get(pk=question_pk)
            result = {'diagram': obj.diagram,
                      'text': question_obj.text,
                      'answers': question_obj.answer_set.all().values('pk', 'text')}
            return Response(result)
        return redirect(reverse_lazy('api_result', kwargs={'pk': testobj.pk}))

    def post(self, request, *args, **kwargs):
        testobj = get_object_or_404(TestObj, pk=kwargs['pk'])
        obj = Testing.objects.filter(user=request.user, testobj=testobj)
        if not obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        obj = obj.get()
        if not obj.question:
            return Response({'error': 'Все вопросы закончились'}, status=status.HTTP_412_PRECONDITION_FAILED)
        question_pk = obj.question[-1]
        question_obj = Question.objects.get(pk=question_pk)
        answer_list = question_obj.answer_set.all()
        bool(answer_list)
        data = RunTestingSerializer(data=request.data, context={"answer_list": answer_list})
        if data.is_valid():
            user_answers = sorted(data.validated_data['answers'])
            positive_answers = sorted([i.pk for i in answer_list.filter(status=True)])

            obj.distant += 1
            del obj.question[-1]
            if user_answers == positive_answers:
                obj.point += 1
                obj.diagram[obj.distant-1] = True

            else:
                obj.diagram[obj.distant - 1] = False
            obj.save()
            return redirect(reverse_lazy('api_run_test', kwargs={'pk': testobj.pk}))
        return Response(data.errors)


class ResultView(views.APIView):
    def get(self, request, *args, **kwargs):
        testobj = get_object_or_404(TestObj, pk=kwargs['pk'])
        obj = Testing.objects.filter(user=request.user, testobj=testobj)
        ser_data = ResultTestingView(obj.get()).data
        return Response({'result': ser_data})