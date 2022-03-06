from django.contrib import admin
from django.urls import path, include
from testor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.MainView.as_view(), name='main'),
    path('theme/<int:pk>/', views.MainView.as_view(), name='theme'),
    path('test/<int:pk>/start/', views.CreateTestingView.as_view(), name='transit'),
    path('test/<int:pk>/', views.TestDetailView.as_view(), name='testobj'),
    path('test/<int:pk>/result/', views.ResultView.as_view(), name='result'),
    path('testing/<int:pk>/', views.TestingView.as_view(), name='testing'),
    path('auth/login/', views.LoginView.as_view(template_name='testor/login.html'), name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/registration/', views.RegistrationView.as_view(), name='registration'),
    path('api/', include('api.urls'))
    ]
