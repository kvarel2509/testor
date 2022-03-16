from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from testor.models import *


class RegistrationUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        token = Token.objects.create(user=user)
        return user, token


class AnswerSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Answer
        fields = ['pk', 'text', 'status']


class QuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True, source='answer_set')

    class Meta:
        model = Question
        fields = ['pk', 'text', 'many', 'answer']
        read_only_fields = ['many']

    def save_answers(self, answers, instance, positive_count=0):
        for i in range(len(answers)):
            if answers[i]['status']:
                positive_count += 1
            answers[i]['question'] = instance
            answers[i] = Answer(**answers[i])
        if positive_count > 1 and not instance.many:
            instance.many = True
            instance.save()
        elif positive_count == 1 and instance.many:
            instance.many = False
            instance.save()
        Answer.objects.bulk_create(answers)

    def create(self, validated_data):
        answers = validated_data.pop('answer_set')
        instance = super().create(validated_data)

        if answers:
            self.save_answers(answers, instance)
        return instance

    def update(self, instance, validated_data):
        answers = validated_data.pop('answer_set')
        print(answers)
        instance = super().update(instance, validated_data)
        if answers:
            instance.answer_set.all().delete()
            self.save_answers(answers, instance)
        return instance

    def validate_answer(self, value):
        flag_positive = False
        flag_negative = False
        for i in value:
            if not i['status']:
                flag_negative = True
            elif i['status']:
                flag_positive = True
            if flag_negative and flag_positive:
                return value
        raise ValidationError('Должен быть и правильный ответ и неправильный')


class TestListSerializer(serializers.ModelSerializer):
    topic = serializers.PrimaryKeyRelatedField(many=True, queryset=Topic.objects.all())

    class Meta:
        model = TestObj
        fields = ['pk', 'name', 'description', 'topic']


class TestRetrieveSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(many=True, source='question_set', read_only=True)

    class Meta:
        model = TestObj
        fields = ['pk', 'name', 'description', 'topic', 'question']


class RunTestingPostSerializer(serializers.Serializer):
    answers = serializers.ListField(child=serializers.IntegerField())

    def validate_answers(self, value):
        answers_list = [i.pk for i in self.context['answer_list']]
        for i in value:
            if i not in answers_list:
                raise serializers.ValidationError('id вашего ответа нет в списке предложенных')
        return value


class TopicListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = ['pk', 'name']


class TopicRetrieveSerializer(serializers.ModelSerializer):
    tests = TestListSerializer(read_only=True, many=True, source='testobj_set')

    class Meta:
        model = Topic
        fields = ['pk', 'name', 'tests']