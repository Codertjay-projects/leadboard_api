# Generated by Django 4.0.8 on 2023-02-26 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0005_schedulecall_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulecall',
            name='description',
            field=models.TextField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='userschedulecall',
            name='hours_per_week',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]