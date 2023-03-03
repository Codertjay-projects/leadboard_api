import json
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leadboard_api.settings")
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "..", ".."))
django.setup()

from users.models import User
from leads.models import LeadContact
from companies.models import Company, CompanyEmployee, Group, Industry
from schedules.models import ScheduleCall, UserScheduleCall
from feedbacks.models import Feedback
from high_value_contents.models import HighValueContent


def get_or_create_company():
    """
    this is used to create the company
    :return:
    """
    industry, created = Industry.objects.get_or_create(
        name="Technology"
    )

    company = Company.objects.filter(name="Instincthub").first()
    if not company:
        owner = User.objects.get(email="noaholatoye101@gmail.com")
        company = Company.objects.create(
            owner=owner,
            name="Instincthub",
            # username="Instincthub",
            website="https://www.instincthub.com",
            phone="2348162880409",
            info_email="noaholatoye101@gmail.com",
            customer_support_email="noaholatoye101@gmail.com",
            industry=industry,
            overview="""
            At instinctHub, our approach to learning management is centered around delivering seamless and effective
            solutions that meet the unique needs of both our learners and partners. Our work process is designed to ensure that
            we deliver the highest quality service and support, while also providing a smooth and efficient 
            experience for our users.
            """,
            company_size="51-200",
            headquarter="Ikoye,Lagos Island",
            founded="2016-01-01",
            premium_access=True
        )
    return company


def create_users():
    """
    this is used to create users
    :return:
    """
    users_datas = open("data/users.json", "r+")
    data = json.load(users_datas)
    for item in data:
        if item.get("email"):
            # check if the user exists
            if User.objects.filter(email=item.get("email")).exists():
                # Check if the email has been used before
                continue
            else:
                # Create user
                User.objects.create(
                    is_superuser=item.get("is_superuser"),
                    first_name=item.get("first_name"),
                    last_name=item.get("last_name"),
                    email=item.get("email"),
                    is_staff=item.get("is_staff"),
                )


def create_company_employee():
    """
    this would check leads which have a users created by and create and employee who is a merketer
    :return:
    """
    lead_contacts = open("data/lead_contacts.json", "r+")
    data = json.load(lead_contacts)
    for item in data:
        if item.get("staff"):
            user = User.objects.filter(email=item.get("staff").get("email")).first()
            if not user:
                user, created = User.objects.get_or_create(
                    first_name=item.get("staff").get("first_name"),
                    last_name=item.get("staff").get("last_name"),
                    email=item.get("staff").get("email"),
                )
            company_employee, created = CompanyEmployee.objects.get_or_create(
                user=user,
                company=get_or_create_company(),
                role="MARKETER",
                status="ACTIVE"
            )


def create_groups():
    """
    this is used to create groups under a company
    :return:
    """
    groups = open("data/lead_groups.json", "r+")
    data = json.load(groups)
    company = get_or_create_company()
    for item in data:
        group = Group.objects.filter(slug=item.get("slug")).first()
        if not group:
            group, created = Group.objects.get_or_create(
                company=company,
                title=item.get("title"),
                slug=item.get("slug"),
            )


def create_high_value_content():
    """
    this is used to create high value content
    :return:
    """
    high_value_contents = open("data/high_value_contents.json", "r+")
    data = json.load(high_value_contents)
    for item in data:
        group, created = Group.objects.get_or_create(
            title="HIGHVALUECONTENT",
            slug="HIGHVALUECONTENT",
            company=get_or_create_company()
        )
        high_value_content, created = HighValueContent.objects.get_or_create(
            company=get_or_create_company(),
            created_by=User.objects.get(email="noaholatoye101@gmail.com"),
            group=group,
            title=item.get("title"),
            slug=item.get("slug"),
            description=item.get("description"),
            thumbnail=item.get("thumbnail"),
            file=item.get("pdf_file"),
            link=item.get("link"),
            youtube_link=item.get("youtube_link"),
            vimeo_link=item.get("vimeo_link"),
            vimeo_hash_key=item.get("vimeo_hash_key"),
            schedule_link=item.get("schedule_link"),
            publish=False,
        )


def create_schedule_call():
    """
    this is used to create schedule call
    :return:
    """
    schedule_calls = open("data/schedule_calls.json", "r+")
    data = json.load(schedule_calls)

    for item in data:
        schedule_call, created = ScheduleCall.objects.get_or_create(
            staff=User.objects.get(email="noaholatoye101@gmail.com"),
            company=get_or_create_company(),
            title=item.get("title"),
            slug=item.get("slug"),
            minutes=item.get("minutes"),
            description=item.get("description"),
            meeting_link=item.get("meeting_link"),
            timestamp=item.get("timestamp"),
        )


def create_lead_contact():
    """
    this is used to create lead contact
    :return:
    """

    lead_contacts = open("data/lead_contacts.json", "r+")
    data = json.load(lead_contacts)
    for item in data:
        lead_type = "CONTACT_US"
        if item.get("high_value_content"):
            lead_type = "HIGH_VALUE_CONTENT"
        mobile = "0801111111111"
        if item.get("phone"):
            mobile = item.get("phone")
        category = "INFORMATION"
        if item.get("category"):
            category = item.get("category")
        where = "OTHERS"
        if item.get("where"):
            where = item.get("where").replace(" ", "_")
        lead_contact, created = LeadContact.objects.get_or_create(
            prefix=item.get("prefix"),
            lead_type=lead_type,
            company=get_or_create_company(),
            last_name=item.get("last_name"),
            first_name=item.get("first_name"),
            thumbnail=item.get("thumbnail"),
            middle_name=item.get("middle_name"),
            job_title=item.get("job_title"),
            department=item.get("department"),
            sector=item.get("sector"),
            want=item.get("want"),
            email=item.get("email"),
            mobile=mobile,
            lead_source=where,
            assigned_marketer=item.get(""),
            is_safe=item.get("safe"),
            verified=item.get("verified"),
            send_email=item.get("send_email"),
            gender=item.get("gender"),
            category=category.upper(),
            timestamp=item.get("timestamp"),
        )
        if item.get("staff"):
            assigned_marketer = User.objects.filter(email=item.get("staff").get("email")).first()
        else:
            assigned_marketer = User.objects.all().order_by("?").first()
        if assigned_marketer:
            lead_contact.assigned_marketer = assigned_marketer
        if item.get("group"):
            for item_groups in item.get("group"):
                group = Group.objects.filter(slug=item_groups.get("slug")).first()
                if group:
                    lead_contact.groups.add(group)
        lead_contact.save()


def create_user_schedule_call():
    """
    this is used to create the user schedule call
    :return:
    """
    user_scheduled_calls = open("data/user_scheduled_calls.json", "r+")
    data = json.load(user_scheduled_calls)

    for item in data:
        mobile = "0801111111111"
        if item.get("phone"):
            mobile = item.get("phone")
        gender = item.get("gender")
        if not gender:
            gender = "OTHERS"
        user_scheduled_call, created = UserScheduleCall.objects.get_or_create(
            first_name=item.get("first_name"),
            last_name=item.get("last_name"),
            age_range=item.get("age_range"),
            email=item.get("email"),
            location=item.get("location"),
            gender=gender.upper(),
            phone=mobile,
            age=item.get("age"),
            communication_medium="GOOGLE-MEET",
            scheduled_date=f'{item.get("scheduled_date")}T{item.get("scheduled_time")}',
            employed=item.get("employed"),
            other_training=item.get("other_training"),
            other_training_lesson=item.get("other_training_lesson"),
            will_pay=item.get("will_pay"),
            income_range=item.get("income_range"),
            knowledge_scale=item.get("knowledge_scale"),
            have_laptop=item.get("have_laptop"),
            will_get_laptop=item.get("will_get_laptop"),
            when_get_laptop=item.get("when_get_laptop"),
            good_internet=item.get("good_internet"),
            weekly_commitment=item.get("weekly_commitment"),
            saturday_check_in=item.get("saturday_check_in"),
            hours_per_week=item.get("weekly_commitment"),
            catch_up_per_hours_weeks=item.get("catch_up_per_hours_weeks"),
            more_details=item.get("more_details"),
            kids_count=item.get("kids_count"),
            kids_years=item.get("kids_years"),
            time_close_from_school=item.get("time_close_from_school"),
            user_type=item.get("user_type").upper(),
            schedule_category="RESOLVED",
            eligible=item.get("eligible"),
            timestamp=item.get("datetime"),
        )
        if item.get("schedule_call"):
            schedule_call = ScheduleCall.objects.filter(slug=item.get("schedule_call").get("slug")).first()
            if schedule_call:
                user_scheduled_call.schedule_call = schedule_call
        if item.get("staff"):
            assigned_marketer = User.objects.filter(email=item.get("staff").get("email")).first()
        else:
            assigned_marketer = User.objects.all().order_by("?").first()
        user_scheduled_call.assigned_marketer = assigned_marketer
        user_scheduled_call.save()


def create_feedback():
    """
    this is used to create the feedback
    :return:
    """
    feedbacks = open("data/feedbacks.json", "r+")
    data = json.load(feedbacks)
    for item in data:
        if item.get("lead_contact"):
            model_type = "leadcontact"
        elif item.get("userschedulecall"):
            model_type = "userschedulecall"

        if model_type == "leadcontact":
            if item.get("lead_contact"):
                instance = LeadContact.objects.filter(email=item.get("lead_contact").get("email")).first()
        elif model_type == "user_scheduled_call":
            if item.get("user_scheduled_call"):
                instance = UserScheduleCall.objects.filter(
                    timestamp=item.get("user_scheduled_call").get("datetime")).first()

        if item.get("staff"):
            staff = User.objects.filter(email=item.get("staff").get("email")).first()
        if model_type and instance and staff:
            print(item.get("datetime"))
            feedback = Feedback.objects.create_by_model_type(
                model_type=model_type,
                other_model_id=instance.id,
                company=get_or_create_company(),
                staff=staff,
                next_schedule=item.get("next_schedule"),
                action=item.get("action"),
                feedback=item.get("feedback")
            )
            if feedback:
                feedback.timestamp = item.get("timestamp")
                feedback.save()
            else:
                print("No Feedback")



create_users()
print("done with create_users")
get_or_create_company()
print("done with get_or_create_company")

create_company_employee()
print("done with create_company_employee")

create_groups()
print("done with create_groups")

create_schedule_call()
print("done with create_schedule_call")

create_high_value_content()
print("done with create_high_value_content")

create_lead_contact()
print("done with create_lead_contact")

create_user_schedule_call()
print("done with create_user_schedule_call")

create_feedback()
print("done with create_feedback")
