from django.urls import path, include
from .views import RegistrationView, GetToken, TestListView, QuestionListView, RunTestView, ResultView, TestListCategory

urlpatterns = [
    path('', RegistrationView.as_view()),
    path('get-token/<int:pk>/', GetToken.as_view()),
    path('auth/', include('djoser.urls')),
    path('test-list/', TestListView.as_view()),
    path('test-list/<int:pk>/', TestListCategory.as_view()),
    path('test/<int:pk>/', QuestionListView.as_view()),
    path('test/<int:pk>/run/', RunTestView.as_view(), name='api_run_test'),
    path('test/<int:pk>/result/', ResultView.as_view(), name='api_result')
]