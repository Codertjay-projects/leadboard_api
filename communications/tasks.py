from celery import shared_task
from django.contrib.contenttypes.models import ContentType

from communications.models import SendEmailScheduler
from email_logs.models import EmailLog
from events.models import EventRegister
from users.utils import is_valid_uuid


@shared_task
def create_custom_schedule_log(custom_schedule_id):
    """
    The create_custom_schedule_log functions enables us to create log of the mail we are creating to each user
    :param custom_schedule_id: the SendCustomEmailScheduler id since we cant pass instance to task
    :return: True (Note Required)
    """

    print("<<<<<<<>>>>>>>>>CUSTOM<<<<<<<>>>>>>>>>")
    # Using this import to avoid conflict

    # Filter base on the ID Provided
    custom_schedule = SendEmailScheduler.objects.filter(id=is_valid_uuid(custom_schedule_id)).first()
    if not custom_schedule:
        return True
        # Get the email lists
    email_lists = custom_schedule.get_custom_emails()
    for item in email_lists:
        # this contains list of emails which is gotten from the email_list description
        send_group_email_log = EmailLog.objects.create(
            company=custom_schedule.company,
            message_type="CUSTOM",
            scheduler=custom_schedule,
            email=item
            # the email to could be lead_contact model, event register or another
        )

    return True


@shared_task
def create_lead_group_schedule_log(schedule_id):
    """
    The create_group_schedule_log functions enables us to create log of the mail we are creating to each user
    :param schedule_id: the SendGroupsEmailScheduler id since we cant pass instance to task
    :return: True (Note Required)
    """
    # Using this import to avoid conflict
    from .models import SendEmailScheduler
    from leads.models import LeadContact

    # Filter base on the ID Provided
    lead_group_schedule = SendEmailScheduler.objects.filter(id=schedule_id).first()
    if not lead_group_schedule:
        return True
        # Get the email lists
    # The email to must be added before sending the email
    pending_mail_info = lead_group_schedule.get_lead_emails()
    for item in pending_mail_info:
        # Try getting to send group email log if it exists before and if it doesn't
        # exist I just add extra fields
        try:
            lead_contact = LeadContact.objects.get(id=item.get("lead_contact_id"))
            send_group_email_log = EmailLog.objects.create(
                company=lead_group_schedule.company,
                message_type="LEAD_GROUP",
                scheduler=lead_group_schedule,
                # the email to could be lead_contact model, event register or another
                email_to=ContentType.objects.get_for_model(lead_contact),
                email_to_instance_id=lead_contact.id,
            )
        except Exception as a:
            print(a)
    return True


@shared_task
def send_email_to_all_event_registers(schedule_id):
    """"
    This is used to send email to all registers on all event by a company
    """
    # Using this import to avoid conflict
    from .models import SendEmailScheduler

    # Filter base on the ID Provided
    event_schedule = SendEmailScheduler.objects.filter(id=schedule_id).first()
    if not event_schedule:
        return True
        # Get the email lists
    #  loop through the event emails and send the email
    for item in event_schedule.get_events_email():
        # Get the event register instance
        # create the email log
        event_register = EventRegister.objects.filter(id=item.get("event_register_id")).first()
        if event_register:
            email_log = EmailLog.objects.create(
                company=event_schedule.company,
                message_type="EVENT",
                scheduler=event_schedule,
                email_to=ContentType.objects.get_for_model(event_register),
                email_to_instance_id=event_register.id,
            )
    return True


@shared_task
def send_email_to_all_emails(schedule_id):
    """
    this is used to send mail to all the email on the company
    from the company which are , newsletter, event registers, leadcontacts, schedules
    :param schedule_id:
    :return:
    """
    from .models import SendEmailScheduler

    # Filter base on the ID Provided
    all_mail_schedule = SendEmailScheduler.objects.filter(id=schedule_id).first()
    if not all_mail_schedule:
        return True
        #  loop through the event emails and send the email
    for item in all_mail_schedule.get_all_emails():
        # Get the event register instance
        # create the email log
        if item:
            email_log = EmailLog.objects.create(
                company=all_mail_schedule.company,
                message_type="ALL",
                scheduler=all_mail_schedule,
                email=item,
            )
    return True


@shared_task
def send_email_to_high_value_contents(schedule_id):
    """
    this is used to send email to high value contents each or all of them  provided
    :param schedule_id:
    :return:
    """
    # Filter base on the ID Provided
    high_value_contents_schedule = SendEmailScheduler.objects.filter(id=schedule_id).first()
    if not high_value_contents_schedule:
        return True
        #  loop through the high_value_contents_schedule emails and send the email

    # The email to must be added before sending the email
    pending_mail_info = high_value_contents_schedule.get_all_high_value_contents()
    for item in pending_mail_info:
        # Try getting to send group email log if it exists before and if it doesn't
        # exist I just add extra fields
        try:
            from leads.models import LeadContact
            lead_contact = LeadContact.objects.get(id=item.get("lead_contact_id"))
            send_group_email_log = EmailLog.objects.create(
                company=high_value_contents_schedule.company,
                message_type="HIGHVALUECONTENT",
                scheduler=high_value_contents_schedule,
                # the email to could be lead_contact model, event register or another
                email_to=ContentType.objects.get_for_model(lead_contact),
                email_to_instance_id=lead_contact.id,
            )
        except Exception as a:
            print(a)
    return True


@shared_task
def create_user_schedule_schedule_log(custom_schedule_id):
    """
    The create_custom_schedule_log functions enables us to create log of the mail we are creating to each user
    :param custom_schedule_id: the SendCustomEmailScheduler id since we cant pass instance to task
    :return: True (Note Required)
    """

    print("<<<<<<<>>>>>>>>>USER SCHEDULE<<<<<<<>>>>>>>>>")
    # Using this import to avoid conflict

    # Filter base on the ID Provided
    email_schedule = SendEmailScheduler.objects.filter(id=custom_schedule_id).first()
    if not email_schedule:
        return True
        # Get the email lists
    email_lists = email_schedule.get_schedule_emails()
    for item in email_lists:

        try:
            from schedules.models import UserScheduleCall
            user_schedule = UserScheduleCall.objects.get(id=item.get("user_schedule_id"))
            send_group_email_log = EmailLog.objects.create(
                company=user_schedule.company,
                message_type="SCHEDULE_GROUP",
                scheduler=email_schedule,
                # the email to could be lead_contact model, event register or another
                email_to=ContentType.objects.get_for_model(user_schedule),
                email_to_instance_id=user_schedule.id,
            )
        except Exception as a:
            print(a)

    return True
