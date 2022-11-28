import random
import uuid

from django.db import models
# Create your models here.
from django.db.models.signals import pre_save, post_save
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
    role = models.CharField(choices=ROLE_CHOICES, max_length=250)
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
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    # this id is sent to the user upon creating
    invite_id = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    role = models.CharField(max_length=250, choices=ROLE_CHOICES)
    status = models.CharField(max_length=250, choices=INVITE_STATUS, default="PENDING")
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

EMAIL_STATUS = (
    ("PENDING", "PENDING"),
    ("SENT", "SENT"),
    ("FAILED", "FAILED"),
)


class SendCustomEmailSchedulerManager(models.Manager):
    """
    this is used to create custom method
    """

    def get_custom_emails(self, status):
        # Get the list of all we need to send
        value_list_info = self.filter(status=status).values_list(
            'id',
            "email_subject",
            "description",
            "email_list",
            "company__info_email",
            "company__customer_support_email",
            "company__name",
            "company__id",
            "scheduled_date",
        )
        custom_email_list_info = []
        for item in value_list_info:
            info = {
                "custom_id": item[0],
                "email_subject": item[1],
                "description": item[2],
                "email_list": item[3].split(","),
                "company__info_email": item[4],
                "company__customer_support_email": item[5],
                "company__name": item[6],
                "company__id": item[7],
                "scheduled_date": item[8],
            }
            custom_email_list_info.append(info)
        return custom_email_list_info

    def update_all_schedule_status_to_sent(self):
        """
        this update all schedule status to send.
        After the email was sent we update all schedule to sent
        """
        self.filter(status="PENDING", scheduled_date__lte=timezone.now()).update(status="SENT")
        return True


class SendCustomEmailScheduler(models.Model):
    """
    This is used to send custom mail email message to users passed in text comma seperated
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    email_subject = models.CharField(max_length=250)
    #  list of email comma seperated
    email_list = models.TextField()
    description = models.TextField()
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=250, choices=EMAIL_STATUS, default="PENDING")
    timestamp = models.DateTimeField(default=timezone.now)
    objects = SendCustomEmailSchedulerManager()


class SendGroupsEmailSchedulerLog(models.Model):
    """
    This is used to log the emails sent by the SendGroupsEmailScheduler
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    send_groups_email_scheduler = models.ForeignKey("SendGroupsEmailScheduler", on_delete=models.CASCADE)
    # the emails would be unique with this SendGroupsEmailScheduler so on create I send the email with post_office
    email = models.EmailField()
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    links_clicked = models.TextField(blank=True, null=True)
    status = models.CharField(choices=EMAIL_STATUS, max_length=50, default="PENDING", blank=True, null=True)
    emails_view_count = models.IntegerField(default=0)
    sent_mail_count = models.IntegerField(default=0)
    read_mail_count = models.IntegerField(default=0)


def post_save_send_group_email_log(sender, instance, *args, **kwargs):
    # This creates a task on celery and sends an email on the scheduled time
    from .tasks import send_email_schedule_task
    if instance.status == "PENDING" or instance.status == "FAILED":
        send_email_schedule_task.delay(
            to_email=instance.email,
            subject=instance.send_groups_email_scheduler.email_subject,
            reply_to=instance.company.customer_support_email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            description=instance.send_groups_email_scheduler.description,
            scheduled_date=instance.send_groups_email_scheduler.scheduled_date,
            company_info_email=instance.company.info_email,
            company_name=instance.company.name,
        )
        # Set the status to sent
        instance.status = "SENT"


post_save.connect(post_save_send_group_email_log, sender=SendGroupsEmailSchedulerLog)


class SendGroupsEmailScheduler(models.Model):
    """
    This is used to send am email to list of groups users on the lead.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    # the set of groups the email is sent to it could be from  newsletters, contacts,downloads and schedule
    email_to = models.ManyToManyField(Group, blank=True)
    email_from = models.CharField(max_length=250)
    email_subject = models.CharField(max_length=250)
    scheduled_date = models.DateTimeField()
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def get_lead_emails(self) -> list:
        #  Get the leads email  that are connected to the SendGroupsEmailScheduler
        #  and also the id of the SendGroupsEmailScheduler
        from leads.models import LeadContact
        value_list_info = LeadContact.objects.filter(company=self.company, groups__in=self.email_to.all()).values_list(
            "email",
            "first_name",
            "last_name",
        )
        schedule_email_list_info = []
        for item in value_list_info:
            # Create a dictionary which enables easy access
            info = {
                "email": item[0],
                "first_name": item[1],
                "last_name": item[2],
            }
            schedule_email_list_info.append(info)
        return schedule_email_list_info


def post_save_create_send_group_email_log(sender, instance, *args, **kwargs):
    # This creates a log on the SendGroupsEmailSchedulerLog which enables us to get more information about
    # the email
    if instance.email_to.count() > 0:
        # The email to must be added before sending the email
        pending_mail_info = instance.get_lead_emails()
        for item in pending_mail_info:
            # Try getting to send group email log if it exists before and if it doesn't
            # exist I just add extra fields
            send_group_email_log, created = SendGroupsEmailSchedulerLog.objects.get_or_create(
                email=item.get("email"),
                send_groups_email_scheduler=instance,
                company=instance.company
            )
            if created:
                # Get the first name and last name from the dictionary on the list
                send_group_email_log.first_name = item.get("first_name")
                send_group_email_log.last_name = item.get("last_name")
                send_group_email_log.save()


post_save.connect(post_save_create_send_group_email_log, sender=SendGroupsEmailScheduler)
