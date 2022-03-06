from rest_framework import serializers
from testor.models import *
from rest_framework.authtoken.models import Token


class RegistrationUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        token = Token.objects.create(user=user)
        return user, token


class TestListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestObj
        fields = ['pk', 'name', 'description', 'topic']
        depth = 1


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['text', 'status']


class QuestionSerializer2(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['text', 'many', 'answers']

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        obj = Question.objects.create(**validated_data)
        for i in range(len(answers)):
            answers[i]['question'] = obj
            answers[i] = Answer(**answers[i])
        Answer.objects.bulk_create(answers)
        return obj


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.ReadOnlyField()

    class Meta:
        model = Question
        fields = ['text', 'answers']


class RunTestingSerializer(serializers.Serializer):
    answers = serializers.ListField()

    def validate_answers(self, value):
        answers_list = [i.pk for i in self.context['answer_list']]
        for i in value:
            if i not in answers_list:
                raise serializers.ValidationError('id вашего ответа нет в списке предложенных')
        return value


class ResultTestingView(serializers.ModelSerializer):

    class Meta:
        model = Testing
        fields = ['point', 'total', 'diagram']