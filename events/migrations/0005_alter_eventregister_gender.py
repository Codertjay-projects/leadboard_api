# Generated by Django 4.0.8 on 2023-03-31 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_eventregister_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventregister',
            name='gender',
            field=models.CharField(choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE')], max_length=50),
        ),
    ]