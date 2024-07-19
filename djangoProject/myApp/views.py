import traceback
import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Event, Profile, Registration
from .forms import EventForm, UserRegistrationForm, ProfileForm, PasswordResetForm, SetPasswordForm
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView
import random
from twilio.rest import Client
# Load environment variables from .env file
load_dotenv()

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
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
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


def send_otp_sms(receiver_phone_number, otp_code):
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'Your OTP code is {otp_code}',
        from_=twilio_phone_number,
        to=receiver_phone_number
    )

    print(f"OTP sent to {receiver_phone_number}. Message SID: {message.sid}")


def request_otp(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            if not phone_number.startswith('+1'):
                phone_number = '+1' + phone_number
            try:
                user = User.objects.get(profile__phone_number=phone_number)
                otp = generate_otp()
                user.profile.otp = otp
                user.profile.save()
                send_otp_sms(phone_number, otp)
                return redirect('verify_otp', uidb64=urlsafe_base64_encode(force_bytes(user.pk)))
            except User.DoesNotExist:
                form.add_error('phone_number', 'Phone number not registered.')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})


def verify_otp(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.method == 'POST':
        otp = request.POST['otp']
        if user is not None and user.profile.otp == otp:
            return redirect('reset_password', uidb64=uidb64)
        else:
            return HttpResponse('Invalid OTP')
    return render(request, 'password_reset_confirm.html', {'uidb64': uidb64})


def reset_password(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_reset_complete')
    else:
        form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})


def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')

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


def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    past_events = profile.past_events.all()
    upcoming_events = profile.upcoming_events.all()
    return render(request, 'profile.html', {'form': form, 'past_events': past_events, 'upcoming_events': upcoming_events})


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


def team_details(request):
    return render(request, 'team_details.html')


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse(('home')))
