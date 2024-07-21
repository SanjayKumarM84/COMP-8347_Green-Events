import traceback
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Feedback, Event, Profile, Registration
from .forms import EventForm, UserRegistrationForm, ProfileForm, UserForm, FeedbackForm, EventFeedbackForm
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView
import random
from twilio.rest import Client



class HomeView(ListView):
    model = Event
    template_name = 'home.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(eventDate__gte=timezone.now()).order_by('eventDate')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user_events = Event.objects.filter(registration__user=self.request.user, registration__user_attended=False,
                                               eventDate__gte=timezone.now()).order_by('eventDate')
            context['user_events'] = user_events
        else:
            context['user_events'] = None
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if self.request.user.is_authenticated:
            profile, created = Profile.objects.get_or_create(user=self.request.user)
            profile.past_events.add(obj)
        return obj


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('home')
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})


def search_events(request):
    query = request.GET.get('q')
    date = request.GET.get('date')
    location = request.GET.get('location')

    filters = Q()
    if query:
        filters &= Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query)
    if date:
        filters &= Q(date=date)
    if location:
        filters &= Q(location__icontains=location)

    events = Event.objects.filter(filters)

    return render(request, 'search_results.html',
                  {'events': events, 'query': query, 'date': date, 'location': location})


# Function to generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send the OTP via SMS
def send_otp_sms(receiver_phone_number, otp_code):
    # Twilio credentials
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    twilio_phone_number = os.getenv('twilio_phone_number')

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'Your OTP code is {otp_code}',
        from_=twilio_phone_number,
        to=receiver_phone_number
    )

    print(f"OTP sent to {receiver_phone_number}. Message SID: {message.sid}")


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if event.remaining_seats > 0:
        is_user_already_registered = Registration.objects.filter(event=event, user=request.user).exists()
        if not is_user_already_registered:
            event.registered_seats += 1
            event.save()
            Registration.objects.create(event=event, user=request.user)
            profile = Profile.objects.get(user=request.user)
            profile.upcoming_events.add(event)

            otp_code = generate_otp()

            receiver_phone_number = f'+1{profile.phone_number}'
            send_otp_sms(receiver_phone_number, otp_code)

            # Return success response to trigger popup message
            return JsonResponse({'status': 'success', 'message': 'You have successfully registered for the event!'})
        else:
            # Return error response to trigger popup message
            return JsonResponse({'status': 'error', 'message': 'Already Registered.'})
    else:
        # Return error response to trigger popup message
        return JsonResponse({'status': 'error', 'message': 'No seats available for this event.'})


@login_required
def user_history(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    visited_events = profile.past_events.all()

    return render(request, 'user_history.html', {'visited_events': visited_events})


def contact_us(request):
    if request.method == 'POST':
        # Handle contact form submission
        messages.success(request, 'Your message has been sent!')
        return redirect('contact_us')
    return render(request, 'contact_us.html')


def about_us(request):
    return render(request, 'about_us.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def advertise(request):
    return render(request, 'advertise.html')

def sustainability(request):
    return render(request,'sustainability_for_all.html')

def news(request):
    return render(request, 'news.html')

def team_details(request):
    return render(request, 'team_details.html')

def socials(request):
    return render(request, 'socials.html')


# # Create your views here.
# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 response = HttpResponseRedirect(reverse('home'))
#                 response.set_cookie('last_login', timezone.now().strftime('%Y-%m-%d %H:%M:%S'), max_age=3600)
#                 return response
#             else:
#                 return HttpResponse('Your account is disabled.')
#         else:
#             return HttpResponse('Invalid login details.')
#     else:
#         return render(request, 'login.html')
#
#
# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse(('home')))


@login_required
def view_profile(request):
    # Initialize or update visit counter in session
    today_date = timezone.now().strftime('%Y-%m-%d')
    if 'last_visit_date' not in request.session or request.session['last_visit_date'] != today_date:
        request.session['last_visit_date'] = today_date
        request.session['visit_count'] = 1
    else:
        request.session['visit_count'] += 1
    lastLogin = request.COOKIES.get('last_login', '')
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user': request.user,
        'user_form': user_form,
        'profile_form': profile_form,
        'lastLogin': lastLogin,
        'visit_count': request.session['visit_count']
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        print('Received POST request')
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            print('Forms are valid')
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('view_profile')
        else:
            print('Forms are not valid')
            print('User Form Errors:', user_form.errors)
            print('Profile Form Errors:', profile_form.errors)
            messages.error(request, 'Please correct the error below.')
    else:
        print('Received GET request')
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def feedback_view(request):
    initial_data = {
        'name': request.user.get_full_name(),
        'email': request.user.email
    }
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return redirect('home')
    else:
        form = FeedbackForm(initial=initial_data)

    return render(request, 'webfeedback.html', {'form': form})


@login_required
def event_feedback_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.event = event
            feedback.save()
            messages.success(request, 'Your feedback has been submitted.')
            return redirect('home')  # Redirect to the event detail page
    else:
        form = EventFeedbackForm()

    return render(request, 'event_feedback_form.html', {'form': form, 'event': event})


@login_required
def user_history(request):
    profile = get_object_or_404(Profile, user=request.user)

    # Fetch attended events where user_attended is True
    attended_events = Event.objects.filter(registration__user=request.user, registration__user_attended=True).distinct()

    # Fetch upcoming events where user_attended is False and the event date is in the future
    upcoming_events = Event.objects.filter(registration__user=request.user, registration__user_attended=False, eventDate__gte=timezone.now()).distinct()

    return render(request, 'user_history.html', {
        'attended_events': attended_events,
        'upcoming_events': upcoming_events
    })

