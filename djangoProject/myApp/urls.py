from django.urls import path
from . import views
from .views import edit_profile

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
    path('profile/', views.profile, name='view_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]
