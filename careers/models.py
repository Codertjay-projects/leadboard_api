import uuid

from django.db import models

# Create your models here.
from django.utils import timezone

from companies.models import Company
from .utils import JOB_TYPE_CHOICES, JOB_CATEGORY_CHOICES, JOB_EXPERIENCE_LEVEL_CHOICES, APPLICANT_STATUS_CHOICES


class ApplicantExperience(models.Model):
    """
    List of experience the applicant have
    """
    job = models.ForeignKey("Job", on_delete=models.CASCADE)
    applicant = models.ForeignKey("Applicant", on_delete=models.CASCADE)
    job_title = models.CharField(max_length=250)
    company_name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    from_date = models.DateField()
    to_date = models.DateField(blank=True, null=True)
    still_working = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)


class ApplicantEducation(models.Model):
    """"
    This is used by the applicants which contain list of institution the applicant attend
    """
    job = models.ForeignKey("Job", on_delete=models.CASCADE)
    applicant = models.ForeignKey("Applicant", on_delete=models.CASCADE)
    institution = models.CharField(max_length=250)
    course = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    from_date = models.DateField()
    to_date = models.DateField(blank=True, null=True)
    still_schooling = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)


class Applicant(models.Model):
    """
    this contains list of user who applied to a job
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    job = models.ForeignKey("Job", on_delete=models.CASCADE, blank=True, null=True)
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
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to="resumes")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def job_position(self):
        return self.job.job_types

    @property
    def job_id(self):
        # returns the id of the job post
        return self.job.id

    def applicant_experience(self):
        """
        :return: all the experience the applicant have
        """
        return self.applicantexperience_set.all()

    def applicant_education(self):
        """
        :return: all the institution the applicant went to
        """
        return self.applicanteducation_set.all()


class Job(models.Model):
    """the contains list of jobs that are available under a company """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_category = models.CharField(choices=JOB_CATEGORY_CHOICES, max_length=250)
    job_experience_level = models.CharField(choices=JOB_EXPERIENCE_LEVEL_CHOICES, max_length=250)
    job_types = models.CharField(choices=JOB_TYPE_CHOICES, max_length=250, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    application_deadline = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def applicant_counts(self):
        return self.applicants.count()

    @property
    def applicants(self):
        return self.applicant_set.all()
