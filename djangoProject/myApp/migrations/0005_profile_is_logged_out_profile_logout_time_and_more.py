# Generated by Django 5.0.7 on 2024-07-11 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0004_event_image_profile_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_logged_out',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='logout_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='past_events',
            field=models.ManyToManyField(blank=True, related_name='attended_events', to='myApp.event'),
        ),
        migrations.AddField(
            model_name='profile',
            name='upcoming_events',
            field=models.ManyToManyField(blank=True, related_name='upcoming_events', to='myApp.event'),
        ),
    ]
