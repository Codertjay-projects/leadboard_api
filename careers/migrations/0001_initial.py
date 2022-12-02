# Generated by Django 4.0.8 on 2022-12-02 13:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('first_name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=254)),
                ('image', models.ImageField(upload_to='applicants')),
                ('last_name', models.CharField(max_length=250)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('INVITED', 'INVITED'), ('REJECTED', 'REJECTED')], default='PENDING', max_length=50)),
                ('nationality', models.CharField(max_length=250)),
                ('country_of_residence', models.CharField(max_length=250)),
                ('phone_number', models.CharField(max_length=50)),
                ('home_address', models.CharField(max_length=250)),
                ('experience', models.JSONField(blank=True, null=True)),
                ('education', models.JSONField(blank=True, null=True)),
                ('linkedin', models.URLField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('facebook', models.URLField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('resume', models.FileField(upload_to='resumes')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('job_type', models.CharField(choices=[('REMOTE', 'REMOTE'), ('CONTRACT', 'CONTRACT'), ('FULL-TIME', 'FULL-TIME')], max_length=250, unique=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('job_category', models.CharField(choices=[('DEVELOPER', 'DEVELOPER'), ('ANIMATION', 'ANIMATION'), ('ANIMATION', 'ANIMATION'), ('DESIGN', 'DESIGN')], max_length=250)),
                ('job_experience_level', models.CharField(choices=[('JUNIOR-LEVEL', 'JUNIOR-LEVEL'), ('MID-LEVEL', 'MID-LEVEL'), ('SENIOR-LEVEL', 'SENIOR-LEVEL')], max_length=250)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('application_deadline', models.DateField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('applicants', models.ManyToManyField(blank=True, to='careers.applicant')),
            ],
        ),
    ]
