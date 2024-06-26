# Generated by Django 4.0.8 on 2023-03-24 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0010_remove_userschedulecall_groups'),
        ('communications', '0010_alter_sendemailscheduler_message_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendemailscheduler',
            name='schedule_calls',
            field=models.ManyToManyField(blank=True, to='schedules.schedulecall'),
        ),
    ]
