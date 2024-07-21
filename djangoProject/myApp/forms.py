from django import forms
from .models import Event, Profile, Feedback, EventFeedback
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'eventDate', 'location', 'agenda', 'speakers', 'image', 'total_num_of_seats']


# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField()
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = Profile.objects.create(user=user, phone_number=self.cleaned_data['phone_number'])
            profile.save()
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'pronouns', 'phone_number', 'profile_picture']


class FeedbackForm(forms.ModelForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'feedback_text']
        widgets = {
            'feedback_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'feedback_text': 'Feedback',
        }


class EventFeedbackForm(forms.ModelForm):
    class Meta:
        model = EventFeedback
        fields = ['feedback_text']
        widgets = {
            'feedback_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'feedback_text': 'Feedback',
        }

