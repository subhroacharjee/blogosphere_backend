# Generated by Django 5.0 on 2023-12-13 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_verifytoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='avatar',
        ),
        migrations.RemoveField(
            model_name='user',
            name='description',
        ),
        migrations.RemoveField(
            model_name='user',
            name='slug',
        ),
    ]
