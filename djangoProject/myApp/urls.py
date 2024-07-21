# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import path
# from . import views
# from django.contrib.auth import views as auth_views
#
#
# urlpatterns = [
#     path('', views.HomeView.as_view(), name='home'),
#     path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
#     path('create/', views.create_event, name='create_event'),
#     path('search/', views.search_events, name='search_events'),
#     path('event/<int:event_id>/register/', views.register_event, name='register_event'),
#     path('register/', views.register, name='register'),
#     path('history/', views.user_history, name='user_history'),
#     path('contact_us/', views.contact_us, name='contact_us'),
#     path('about_us/', views.about_us, name='about_us'),
#     path('team_details/', views.team_details, name='team_details'),
#     path('login/', views.user_login, name='login'),
#     path('logout/', views.user_logout, name='logout'),
#     path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
#     path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
#     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
#     path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
#     path('profile/', views.view_profile, name='view_profile'),
#     path('profile/edit/', views.edit_profile, name='edit_profile'),
#     path('feedback/', views.feedback_view, name='feedback'),
#     path('user-history/', views.user_history, name='user_history'),
#     path('event_feedback/<int:event_id>/', views.event_feedback_view, name='event_feedback'),
#     path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
#     path('terms_of_service/', views.terms_of_service, name='terms_of_service'),
#     path('advertise/', views.advertise, name='advertise'),
#     path('sustainability_for_all/', views.sustainability, name='sustainability_for_all'),
#     path('news/', views.news, name='news'),
#     path('socials/', views.socials, name='socials'),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.conf.urls.static import static
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
    path('history/', views.user_history, name='user_history'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('about_us/', views.about_us, name='about_us'),
    path('team_details/', views.team_details, name='team_details'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('event_feedback/<int:event_id>/', views.event_feedback_view, name='event_feedback'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms_of_service/', views.terms_of_service, name='terms_of_service'),
    path('advertise/', views.advertise, name='advertise'),
    path('sustainability_for_all/', views.sustainability, name='sustainability_for_all'),
    path('news/', views.news, name='news'),
    path('socials/', views.socials, name='socials'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

