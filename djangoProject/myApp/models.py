from django.db import models
from django.contrib.auth.models import User

#--------------------------------------------------------------------
# Worked By Jahnavi

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    past_events = models.ManyToManyField('Event', related_name='attended_events', blank=True)
    upcoming_events = models.ManyToManyField('Event', related_name='upcoming_events', blank=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    is_logged_out = models.BooleanField(default=False)
<<<<<<< HEAD
    phone_number = models.CharField(max_length=15, blank=True, null=True)
=======
    phone_number = models.IntegerField(default=0)
    pronouns = models.CharField(max_length=50, blank=True, null=True)
>>>>>>> 298191027a9fc2f5cbcb78a8edf4e0998bfa1528

    def __str__(self):
        return self.user.username

#---------------------------------------------------------------------------------------------------------
#Worked by Sanjay

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    eventDate = models.DateTimeField()
    location = models.CharField(max_length=255)
    agenda = models.TextField()
    speakers = models.TextField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    total_num_of_seats = models.IntegerField()
    registered_seats = models.IntegerField(default=0)
    remaining_seats = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.remaining_seats = self.total_num_of_seats - self.registered_seats
        super().save(*args, **kwargs)

#--------------------------------------------------------------------
#Worked by Bhuvanesh

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    user_attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

#--------------------------------------------------------------------
# Worked By Aamani

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_feedbacks')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class EventFeedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    star_rating = models.IntegerField(default=1, choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 star rating
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.event.name} feedback by {self.user.username} on {self.created_at.strftime("%Y-%m-%d %H:%M")}'
