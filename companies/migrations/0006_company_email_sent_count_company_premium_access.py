# Generated by Django 4.0.8 on 2023-02-22 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_rename_headquater_company_headquarter'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='email_sent_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='company',
            name='premium_access',
            field=models.BooleanField(default=True),
        ),
    ]
