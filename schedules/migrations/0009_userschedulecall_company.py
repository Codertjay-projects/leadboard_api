# Generated by Django 4.0.8 on 2023-03-22 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0010_company_logo'),
        ('schedules', '0008_schedulecall_redirect_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userschedulecall',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]
