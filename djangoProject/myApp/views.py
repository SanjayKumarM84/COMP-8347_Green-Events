import traceback

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Event, Profile, Registration
from .forms import EventForm, UserRegistrationForm, ProfileForm, UserForm
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import ListView, DetailView


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


def send_confirmation_email(user_email, event, user):
    try:
        subject = 'Event Registration Confirmation'
        message = f'''
        Dear {user.username},
    
        You have successfully registered for the event "{event.name}".
    
        Event Details:
        Name: {event.name}
        Description: {event.description}
        Date: {event.eventDate.strftime('%Y-%m-%d %H:%M')}
        Location: {event.location}
        Agenda: {event.agenda}
        Speakers: {event.speakers}
    
        Thank you for registering!
    
        Best regards,
        Team Green Events
        '''

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]

        send_mail(subject, message, from_email, recipient_list)
    except Exception as err:
        print(traceback.print_exc())
        print(str(err))


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

            user_email = request.user.email
            send_confirmation_email(user_email, event, request.user)

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
    return render(request, 'profile.html',
                  {'form': form, 'past_events': past_events, 'upcoming_events': upcoming_events})


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


@login_required
def view_profile(request):
    if request.method == 'POST':
        user = request.user
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return render(request, 'profile.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'names' : user.get_full_name(),
            })
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form  # Ensure user data is passed to the template
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {'form': form})