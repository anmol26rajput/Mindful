from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from journal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_setup, name='profile_setup'),
    path('quiz/', views.quiz_setup, name='quiz_setup'),
    path('login/', auth_views.LoginView.as_view(template_name='journal/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='journal/logout.html'), name='logout'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('habits/', views.habits_list, name='habits_list'),
    path('sleep/', views.sleep_tracker, name='sleep_tracker'),
    path('goals/', views.goals_tracker, name='goals_tracker'),
    path('journal/', views.journal_list, name='journal_list'),
]