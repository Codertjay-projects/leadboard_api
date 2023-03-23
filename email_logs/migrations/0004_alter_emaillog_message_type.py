# Generated by Django 4.0.8 on 2023-03-23 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_logs', '0003_remove_emaillog_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emaillog',
            name='message_type',
            field=models.CharField(choices=[('CUSTOM', 'CUSTOM'), ('LEAD_GROUP', 'LEAD_GROUP'), ('SCHEDULE_GROUP', 'SCHEDULE_GROUP'), ('HIGHVALUECONTENT', 'HIGHVALUECONTENT'), ('CAREER', 'CAREER'), ('EVENT', 'EVENT'), ('SCHEDULE', 'EVENT'), ('ALL', 'ALL'), ('OTHERS', 'OTHERS')], max_length=250),
        ),
    ]
