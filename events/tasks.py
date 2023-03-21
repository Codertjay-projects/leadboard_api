from celery import shared_task

# Note: I am currently having the import inside my
# function just to prevent circular import in the future
from events.models import EventRegister


@shared_task
def send_mail_to_event_register(event_slug, subject, message, schedule_date):
    """
    this sends an email to all registers on an event only one event
    and it use our Email log to send the email
    :return:
    """
    from .models import Event
    from email_logs.models import EmailLog
    from communications.models import SendEmailScheduler

    event = Event.objects.filter(slug=event_slug).first()
    if not event:
        return False

    # Create the schedule model
    scheduler = SendEmailScheduler.objects.create(
        company=event.company,
        message_type="EVENT",
        email_subject=subject,
        scheduled_date=schedule_date,
        description=message,
    )
    # add the event
    scheduler.events.add(event)
    #  loop through the event emails and send the email
    for item in scheduler.get_events_email():
        # create the email log
        event_register = EventRegister.objects.filter(id=item.get("event_register_id")).first()
        if event_register:
            email_log = EmailLog.objects.create(
                company=event.company,
                message_type="EVENT",
                scheduler=scheduler,
                email_to=event_register,
                email_to_instance_id=event_register.id,
            )
    return True


@shared_task
def send_email_to_all_event_registers(company_id, subject, message, schedule_date):
    """"
    This is used to send email to all registers on all event by a company
    """
    from .models import Event
    from email_logs.models import EmailLog

    from companies.models import Company

    # Get the company
    company = Company.objects.filter(id=company_id).first()
    if not company:
        return False

    #  Get  all the company event
    company_event_qs = Event.objects.filter(company__id=company_id)
    # Create the schedule model
    from communications.models import SendEmailScheduler
    scheduler = SendEmailScheduler.objects.create(
        company=company,
        message_type="EVENT",
        email_subject=subject,
        scheduled_date=schedule_date,
        description=message,
    )
    # add  all the event
    for event in company_event_qs:
        scheduler.events.add(event)
    #  loop through the event emails and send the email
    for item in scheduler.get_events_email():
        # Get the event register instance
        # create the email log
        event_register = EventRegister.objects.filter(id=item.get("event_register_id")).first()
        if event_register:
            email_log = EmailLog.objects.get_or_create(
                company=company,
                message_type="EVENT",
                scheduler=scheduler,
                email_to=event_register,
                email_to_instance_id=event_register.id,
            )
    return True
