from celery import shared_task

from communications.models import SendEmailScheduler
from email_logs.models import EmailLog


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
    custom_schedule = SendEmailScheduler.objects.filter(id=custom_schedule_id).first()
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
def create_group_schedule_log(schedule_id):
    """
    The create_group_schedule_log functions enables us to create log of the mail we are creating to each user
    :param schedule_id: the SendGroupsEmailScheduler id since we cant pass instance to task
    :return: True (Note Required)
    """
    # Using this import to avoid conflict
    from .models import SendEmailScheduler
    from leads.models import LeadContact

    # Filter base on the ID Provided
    group_schedule = SendEmailScheduler.objects.filter(id=schedule_id).first()
    if not group_schedule:
        return True
        # Get the email lists
    # The email to must be added before sending the email
    pending_mail_info = group_schedule.get_lead_emails()
    for item in pending_mail_info:
        # Try getting to send group email log if it exists before and if it doesn't
        # exist I just add extra fields
        try:
            lead_contact = LeadContact.objects.get(id=item.get("lead_contact_id"))
            send_group_email_log = EmailLog.objects.create(
                company=group_schedule.company,
                message_type="GROUP",
                scheduler=group_schedule,
                # the email to could be lead_contact model, event register or another
                email_to=lead_contact,
                email_to_id=lead_contact.id,
            )
        except:
            pass
    return True
