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
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = RegistrationUserSerializer(obj).data
        data['token'] = 'Token ' + Token.objects.get(user_id=obj.pk).key
        return Response(data=data)


class TopicListView(generics.ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicListSerializer


class TopicRetrieveView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicRetrieveSerializer


class TestListView(generics.ListCreateAPIView):
    """Показывает все тесты, позволяет создать новый тест"""
    serializer_class = TestListSerializer
    queryset = TestObj.objects.all()

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return TestObj.objects.filter(topic=self.kwargs['pk'])
        return TestObj.objects.all()


class TestRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TestRetrieveSerializer
    queryset = TestObj.objects.all()


class QuestionForTestListView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(testobj=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(testobj=get_object_or_404(TestObj, pk=self.kwargs['pk']))


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


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
        result = {'pk': obj.pk,
                  'total': obj.total,
                  'distant': obj.distant,
                  'point': obj.point,
                  'diagram': obj.diagram,
                  'question': {}}
        if obj.question:
            question_pk = obj.question[-1]
            question_obj = Question.objects.get(pk=question_pk)
            result['question'] = QuestionSerializer(question_obj).data
        return Response(result)

    def post(self, request, *args, **kwargs):
        testobj = get_object_or_404(TestObj, pk=kwargs['pk'])
        obj = Testing.objects.filter(user=request.user, testobj=testobj)
        if not obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        obj = obj.get()
        if not obj.question:
            return Response({'error': 'Все вопросы закончились'}, status=status.HTTP_204_NO_CONTENT)
        question_pk = obj.question[-1]
        question_obj = Question.objects.get(pk=question_pk)
        answer_list = question_obj.answer_set.all()
        bool(answer_list)
        data = RunTestingPostSerializer(data=request.data, context={"answer_list": answer_list})
        if data.is_valid():
            user_answers = sorted(data.validated_data['answers'])
            positive_answers = sorted([i.pk for i in answer_list.filter(status=True)])

            obj.distant += 1
            del obj.question[-1]
            if user_answers == positive_answers:
                obj.point += 1
                obj.diagram[obj.distant - 1] = True

            else:
                obj.diagram[obj.distant - 1] = False
            obj.save()
            return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
        return Response(data.errors, status.HTTP_205_RESET_CONTENT)