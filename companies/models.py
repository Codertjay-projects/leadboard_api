import random
import uuid

from django.db import models
# Create your models here.
from django.db.models.signals import pre_save
from django.utils import timezone

from users.models import User
from users.utils import create_slug


class Industry(models.Model):
    """
    these are the list of the industries in which a company can choose
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


COMPANY_SIZE_CHOICES = (
    ("2-10", "2-10"),
    ("11-50", "11-50"),
    ("51-200", "51-200"),
    ("11-50", "11-50"),
    ("51-200", "51-200"),
    ("201-500", "201-500"),
    ("501-1000", "501-1000"),
    ("1001-5000", "1001-5000"),
    ("5001-10000", "5001-10000"),
    ("10000-+", "10000-+"),
)


class Location(models.Model):
    """this contains list of location which could be used for the company """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


COMPANY_EMPLOYEE_STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("DEACTIVATE", "DEACTIVATE"),
    ("PENDING", "PENDING"),
)


class Company(models.Model):
    """
    This enables identifying what company a user exists in when assigning marketer to a lead
    and also add what part does a user belong to in his company
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=250)
    username = models.SlugField(unique=True, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=25)
    info_email = models.EmailField(blank=True, null=True)
    customer_support_email = models.EmailField(blank=True, null=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    company_size = models.CharField(choices=COMPANY_SIZE_CHOICES, max_length=250, blank=True, null=True)
    headquater = models.CharField(max_length=250, blank=True, null=True)
    founded = models.DateField(blank=True, null=True)
    locations = models.ManyToManyField(Location, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
    def __str__(self):
        return f"{self.username} -- {self.name}"
    def admins_count(self):
        """
        this returns the total number of admin in a company
        """
        return self.companyemployee_set.filter(role="ADMIN").count()

    def marketers_count(self):
        """
        this returns the total number of marketers in a company
        """
        return self.companyemployee_set.filter(role="MARKETER").count()

    def company_employees(self):
        return self.companyemployee_set.all()

    def first_marketer_user(self):
        """
        this returns first employee in a company but shows only the user on it.
        It is only called when the company have more than zero marketer
        """
        return self.companyemployee_set.filter(role="MARKETER", status="ACTIVE").first().user

    def first_admin_user(self):
        """
        this returns first employee in a company but shows only the user on it.
        It is only called when the company have more than zero admin
        """
        return self.companyemployee_set.filter(role="ADMIN", status="ACTIVE").first().user

    def all_marketers_user_ids(self):
        """
        This returns list of IDS in the of the marketers but the user id that was used to create it
        :return:
        """
        user_id = self.companyemployee_set.filter(role="MARKETER", status="ACTIVE").values_list("user_id")
        user_id_list = []
        for item in user_id:
            user_id_list.append(item[0])
        return user_id_list

    def all_admins_user_ids(self):
        """
        This returns list of IDS in the of the admins but the user id that was used to create it
        :return:
        """
        user_id = self.companyemployee_set.filter(role="ADMIN", status="ACTIVE").values_list("user_id")
        user_id_list = []
        for item in user_id:
            user_id_list.append(item[0])
        return user_id_list


ROLE_CHOICES = (
    ("ADMIN", "ADMIN"),
    ("MARKETER", "MARKETER"),
)


class CompanyEmployeeManager(models.Manager):
    """
    This enables create optional function
    """

    def create_or_update(self, user, company, role, status):
        """
        this enables getting or creating a company employee if he or she exists we just update
        """
        company_employee = self.filter(user=user, company=company).first()
        if company_employee:
            """if the employees exist we just make an update"""
            company_employee.role = role
            company_employee.status = status
            company_employee.save()
        else:
            # We just create a new employee
            company_employee = CompanyEmployee.objects.create(user=user, company=company, role=role, status=status)
        return company_employee


class CompanyEmployee(models.Model):
    """
    THIS company marketer is meant for us to track the marketer which was added to the company
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES, max_length=250,blank=True,null=True)
    invited= models.BooleanField(default=True)
    status = models.CharField(choices=COMPANY_EMPLOYEE_STATUS, max_length=250, )
    timestamp = models.DateTimeField(default=timezone.now)
    lead_actions_count = models.IntegerField(default=0)
    schedule_actions_count = models.IntegerField(default=0)
    objects = CompanyEmployeeManager()

    class Meta:
        ordering = ["-timestamp"]


INVITE_STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("PENDING", "PENDING"),
)


class CompanyInvite(models.Model):
    """This is meant to create an invitation which would be sent to the user to join the company """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    # this id is sent to the user upon creating
    invite_id = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    role = models.CharField(max_length=250, choices=ROLE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=250, choices=INVITE_STATUS, default="PENDING")
    invited = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]

    def save(self, *args, **kwargs):
        if not self.invite_id:
            self.invite_id = random.randint(1000000, 9999999)
        return super(CompanyInvite, self).save(*args, **kwargs)


class Group(models.Model):
    """
    This contains list of activities on a companies in which the company uses to group
    his or her leads or meeting schedules
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, null=False, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.title


def pre_save_group_receiver(sender, instance, *args, **kwargs):
    # enable creating slug for a  group before it is being saved
    if not instance.slug:
        instance.slug = create_slug(instance, Group)


pre_save.connect(pre_save_group_receiver, sender=Group)
