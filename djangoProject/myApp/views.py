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
from datetime import datetime
from django.contrib.auth import views as auth_views
from django.views.generic import ListView, DetailView
import datetime


#Worked by Sanjay
#Home Page is implemented using class based views
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


#Worked By Sanjay
#This view function is used to search for events based on event title, location and date
def search_events(request):
    query = request.GET.get('q') # If user enters event title or a part of a event title
    date = request.GET.get('date') # If user enters date
    location = request.GET.get('location') # If user enters location

    filters = Q()
    if query:
        filters &= Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query)
    if date:
        filters &= Q(date=date)
    if location:
        filters &= Q(location__icontains=location)

    events = Event.objects.filter(filters) # Fetch data from database based on above filter

    # Returning the results
    return render(request, 'search_results.html',
                  {'events': events, 'query': query, 'date': date, 'location': location})


#--------------------------------------------------------------------
#Worked by Bhuvanesh
#Event Detail Page has been implemented using class based views
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


#Worked by Bhuvanesh
#User Regsitration/Sign Up Function
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST) #Input values (username, email, password) are been captured using django Forms
        if form.is_valid():
            # User data will be saved if the form is valid
            user = form.save() #Saving user data into the database
            return redirect('login')  # Redirect to login page after successful registration
    else:
        # For GET method
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


# Worked by Bhuvanesh
# To register a event
@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # Checking whether there are any remanining seats in that particular event
    if event.remaining_seats > 0:
        is_user_already_registered = Registration.objects.filter(event=event, user=request.user).exists()
        # If the user has not registered
        if not is_user_already_registered:
            event.registered_seats += 1
            event.save()
            Registration.objects.create(event=event, user=request.user)
            profile = Profile.objects.get(user=request.user)
            profile.upcoming_events.add(event)

            # Returning success response to trigger popup message
            return JsonResponse({'status': 'success', 'message': 'You have successfully registered for the event!'})
        else:
            # If the user has already registered
            # Returning error response to trigger popup message
            return JsonResponse({'status': 'error', 'message': 'Already Registered.'})
    else:
        # If there are no remaining seats left
        # Returning error response to trigger popup message
        return JsonResponse({'status': 'error', 'message': 'No seats available for this event.'})


# Worked By Bhuvanesh
# Login View Function
class CustomLoginView(auth_views.LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        # Call the parent form_valid method to log in the user
        response = super().form_valid(form)

        # Set the cookie with the last login time
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), max_age=3600)

        return response


#--------------------------------------------------------------------
# Worked By Jahnavi
# View function used to show user profile
@login_required
def view_profile(request):
    # Initialize or update visit counter in session
    today_date = timezone.now().strftime('%Y-%m-%d')
    if 'last_visit_date' not in request.session or request.session['last_visit_date'] != today_date:
        request.session['last_visit_date'] = today_date
        request.session['visit_count'] = 1
    else:
        request.session['visit_count'] += 1
    last_login = request.COOKIES.get('last_login', '')
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user': request.user,
        'user_form': user_form,
        'profile_form': profile_form,
        'lastLogin': last_login,
        'visit_count': request.session['visit_count']
    })

# Worked by Jahnavi
# View Function used to edit user profile
@login_required
def edit_profile(request):
    if request.method == 'POST':
        print('Received POST request')
        # User data will be captured from Forms
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        # If the forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            print('Forms are valid')
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('view_profile')
        else:
            # If the forms are invalid
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


# Worked By Jahnavi
# View function used for website feedback
def feedback_view(request):
    # Capturing user full name and email
    initial_data = {
        'name': request.user.get_full_name(),
        'email': request.user.email
    }
    if request.method == 'POST':
        # Forms is been used to take user input data
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # If the form is valid, save the user input data in the database and redirect user to the home page
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return redirect('home')
    else:
        # For GET method
        form = FeedbackForm(initial=initial_data)

    return render(request, 'webfeedback.html', {'form': form})


#--------------------------------------------------------------------
# Worked By Aamani
# View function used for event feedback
@login_required
def event_feedback_view(request, event_id):
    event = get_object_or_404(Event, id=event_id) # Querying event data based on id
    if request.method == 'POST':
        # User input data will be captured using django forms
        form = EventFeedbackForm(request.POST)
        if form.is_valid():
            # If the form is valid, then user input data will be saved in the database and user will be redirected to home page
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.event = event
            feedback.save()
            return redirect('home')  # Redirect to the event detail page
    else:
        # For GET method
        form = EventFeedbackForm()

    return render(request, 'event_feedback_form.html', {'form': form, 'event': event})


# Worked by Aamani
# View function to see the past and upcoming events of the user
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

#--------------------------------------------------------------------
# Static Pages

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


#---------------------------------------------------------------------------------------------------------
#Worked by Sanjay
# To create a event
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

