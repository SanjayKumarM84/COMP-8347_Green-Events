# Generated by Django 5.0.6 on 2024-07-08 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0002_alter_event_remaining_seats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='eventDate',
            field=models.DateTimeField(),
        ),
    ]
