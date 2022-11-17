import uuid

from django.db import models

# Create your models here.
from companies.models import Company

JOB_TYPE_CHOICES = (
    ("REMOTE", "REMOTE"),
    ("CONTRACT", "CONTRACT"),
    ("FULL-TIME", "FULL-TIME"),
)


class JobType(models.Model):
    """
    this contains the categories of jobs which is either contract,fulltime or remote
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    job_type = models.CharField(choices=JOB_TYPE_CHOICES, max_length=250, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)


APPLICANT_STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("INVITED", "INVITED"),
    ("REJECTED", "REJECTED"),
)


class Applicant(models.Model):
    """
    this contains list of user who applied to a job
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250)
    email = models.EmailField()
    image = models.ImageField(upload_to="applicants")
    last_name = models.CharField(max_length=250)
    status = models.CharField(choices=APPLICANT_STATUS_CHOICES, max_length=50, default="PENDING")
    nationality = models.CharField(max_length=250)
    country_of_residence = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=50)
    home_address = models.CharField(max_length=250)
    experience = models.JSONField(blank=True, null=True)
    education = models.JSONField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to="resumes")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def job_position(self):
        return self.job_set.first().job_types

    @property
    def job_id(self):
        return self.job_set.first().id


JOB_CATEGORY_CHOICES = (
    ("DEVELOPER", "DEVELOPER"),
    ("ANIMATION", "ANIMATION"),
    ("ANIMATION", "ANIMATION"),
    ("DESIGN", "DESIGN"),
)
JOB_EXPERIENCE_LEVEL_CHOICES = (
    ("JUNIOR-LEVEL", "JUNIOR-LEVEL"),
    ("MID-LEVEL", "MID-LEVEL"),
    ("SENIOR-LEVEL", "SENIOR-LEVEL"),
)


class Job(models.Model):
    """the contains list of jobs that are available under a company """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_category = models.CharField(choices=JOB_CATEGORY_CHOICES, max_length=250)
    job_experience_level = models.CharField(choices=JOB_EXPERIENCE_LEVEL_CHOICES, max_length=250)
    job_types = models.ManyToManyField(JobType, blank=True)
    applicants = models.ManyToManyField(Applicant, blank=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    application_deadline = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def applicant_counts(self):
        return self.applicants.count()
