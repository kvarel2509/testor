from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy


class Person(User):
    """
    Расширение модели юзера
    """
    birthday = models.DateField('День рождения')
    city = models.CharField('Город', max_length=20, blank=True)


class Topic(models.Model):
    """
    Список тем
    """
    name = models.CharField('Название', max_length=50)

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('theme', kwargs={'pk': self.pk})


class TestObj(models.Model):
    """
    Тест. Его название, описание. Можно добавить список тем, к которым он подходит.
    """
    name = models.CharField('Название', max_length=30)
    description = models.TextField('Описание теста')
    topic = models.ManyToManyField(Topic, verbose_name='Тема теста')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def get_absolute_url(self):
        return reverse_lazy('testobj', kwargs={'pk': self.pk})


class Question(models.Model):
    """
    Описание вопроса
    """
    text = models.TextField('Вопрос')
    testobj = models.ForeignKey(TestObj, on_delete=models.CASCADE, verbose_name='Тест')
    many = models.BooleanField('Много ответов', default=False)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.text


class Answer(models.Model):
    """
    Ответы
    """
    text = models.TextField('Ответ')
    status = models.BooleanField('Верный?', default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return self.text


class Testing(models.Model):
    """
    Тестирование
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    testobj = models.ForeignKey(TestObj, on_delete=models.SET_NULL, null=True, verbose_name='Тест')
    distant = models.PositiveIntegerField('Всего задано вопросов', default=0)
    point = models.PositiveIntegerField('Правильных ответов', default=0)
    total = models.PositiveIntegerField('Всего вопросов в тесте', default=0)
    question = models.JSONField('id оставшихся вопросов')
    diagram = models.JSONField('Диаграмма ответов', default=list)
