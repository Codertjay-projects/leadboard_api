# Generated by Django 4.0.8 on 2023-03-24 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0010_remove_userschedulecall_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedulecall',
            name='group',
        ),
        migrations.AlterField(
            model_name='schedulecall',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]