# Generated by Django 4.0.8 on 2022-12-02 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('careers', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AddField(
            model_name='job',
            name='job_types',
            field=models.ManyToManyField(blank=True, to='careers.jobtype'),
        ),
        migrations.AddField(
            model_name='applicant',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]