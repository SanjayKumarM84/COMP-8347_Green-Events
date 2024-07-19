from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    pronouns = models.CharField(max_length=100, blank=True, null=True)  # Add this line
    past_events = models.ManyToManyField('Event', related_name='attended_events', blank=True)
    upcoming_events = models.ManyToManyField('Event', related_name='upcoming_events', blank=True)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    is_logged_out = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


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


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    user_attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

