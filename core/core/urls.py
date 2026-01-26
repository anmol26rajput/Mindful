from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from journal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('profile/', views.profile_setup, name='profile_setup'),
    path('profile/overview/', views.profile_overview, name='profile_overview'),
    
    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='journal/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='journal/password_change_done.html'), name='password_change_done'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='journal/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='journal/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='journal/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='journal/password_reset_complete.html'), name='password_reset_complete'),

    path('quiz/', views.quiz_setup, name='quiz_setup'),
    path('login/', auth_views.LoginView.as_view(template_name='journal/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='journal/logout.html', next_page='login'), name='logout'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('habits/', views.habits_list, name='habits_list'),
    path('sleep/', views.sleep_tracker, name='sleep_tracker'),
    path('goals/', views.goals_tracker, name='goals_tracker'),
    path('journal/', views.journal_list, name='journal_list'),
    
    # Email Change Flow
    path('email/change/initiate/', views.initiate_email_change, name='initiate_email_change'),
    path('email/change/verify/', views.verify_email_change, name='verify_email_change'),
    path('email/change/final/', views.change_email_final, name='change_email_final'),
]