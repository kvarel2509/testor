from django.urls import path, include
from .views import *

urlpatterns = [
    path('', RegistrationView.as_view()),
    path('get-token/<int:pk>/', GetToken.as_view()),
    path('auth/', include('djoser.urls')),
    path('test-list/', TestListView.as_view()),
    path('test-list/<int:pk>/', TestListView.as_view()),
    path('test/<int:pk>/', TestRetrieveView.as_view()),
    path('test/<int:pk>/question-list/', QuestionForTestListView.as_view()),
    path('question/<int:pk>/', QuestionDetailView.as_view()),
    path('test/<int:pk>/run/', RunTestView.as_view(), name='api_run_test'),
    path('test/<int:pk>/result/', ResultView.as_view(), name='api_result'),
    path('answer/<int:pk>/', AnswerView.as_view())
]