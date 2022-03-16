from django.urls import path, include
from .views import *

urlpatterns = [
    path('', TestListView.as_view()),
    path('registration', RegistrationView.as_view(), name='reg'),
    path('get-token/<int:pk>/', GetToken.as_view()),
    path('test-list/', TestListView.as_view(), name='test_list'),
    path('test-list/<int:pk>/', TestListView.as_view(), name='test_list_filter'),
    path('test/<int:pk>/', TestRetrieveView.as_view(), name='test_detail'),
    path('test/<int:pk>/question-list/', QuestionForTestListView.as_view()),
    path('question/<int:pk>/', QuestionDetailView.as_view()),
    path('test/<int:pk>/run/', RunTestView.as_view(), name='api_run_test'),
    path('answer/<int:pk>/', AnswerView.as_view()),
    path('topic/', TopicListView.as_view()),
    path('topic/<int:pk>/', TopicRetrieveView.as_view())
]