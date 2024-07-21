from django import forms
<<<<<<< HEAD
from .models import Event, Profile
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm as DjangoPasswordResetForm, SetPasswordForm as DjangoSetPasswordForm
=======
from .models import Event, Profile, Feedback, EventFeedback
from django.contrib.auth.forms import UserCreationForm
>>>>>>> 298191027a9fc2f5cbcb78a8edf4e0998bfa1528
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
        fields = ['username', 'email', 'password1', 'password2', 'phone_number']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.startswith('+1'):
            phone_number = '+1' + phone_number
        if not phone_number.startswith('+1') or not phone_number[2:].isdigit() or len(phone_number) != 12:
            raise forms.ValidationError("Please enter a valid Canadian phone number starting with +1.")
        return phone_number

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
<<<<<<< HEAD
        fields = ['profile_picture', 'bio', 'phone_number']

class PasswordResetForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.startswith('+1'):
            phone_number = '+1' + phone_number
        if not phone_number.startswith('+1') or not phone_number[2:].isdigit() or len(phone_number) != 12:
            raise forms.ValidationError("Please enter a valid Canadian phone number starting with +1.")
        return phone_number


class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="New password")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn’t match.")
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user
=======
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

>>>>>>> 298191027a9fc2f5cbcb78a8edf4e0998bfa1528
