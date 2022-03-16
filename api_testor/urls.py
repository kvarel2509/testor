from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', TestListAllView.as_view(), name='api_test_list'),
    path('topic/<int:pk>/', TestListFilterView.as_view(), name='api_test_list_filter'),
    path('test/<int:pk>/', TestDetailView.as_view(), name='api_test_detail'),
    path('test/<int:pk>/run/', TestRunView.as_view(), name='api_test_run'),
    path('test/new/', TestCreateView.as_view(), name='api_test_create'),
    path('test/<int:pk>/add_question/', QuestionCreateView.as_view(), name='api_question_create'),
    path('registration/', RegistrationView.as_view(), name='api_registration'),
    path('login/', LoginView.as_view(template_name='api_testor/login.html', next_page='api_test_list'),
         name='api_login'),
    path('logout/', LogoutView.as_view(next_page='api_test_list'), name='api_logout')
]