from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('create/', views.create_event, name='create_event'),
    path('search/', views.search_events, name='search_events'),
    path('event/<int:event_id>/register/', views.register_event, name='register_event'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('history/', views.user_history, name='user_history'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('about_us/', views.about_us, name='about_us'),
    path('team_details/', views.team_details, name='team_details'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', views.request_otp, name='password_reset'),
    path('verify_otp/<uidb64>/', views.verify_otp, name='verify_otp'),
    path('reset_password/<uidb64>/', views.reset_password, name='reset_password'),
    path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
]