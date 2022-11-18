from celery import shared_task
from post_office import mail

from events.models import Event


@shared_task
def send_user_register_event(first_name, last_name, email, event_id):
    """
    this sends an email to the user that register for an event
    :return:
    """
    event = Event.objects.filter(id=event_id).first()
    if not event:
        return False
    company_email = event.company.owner.email
    event_type = "Free"
    if event.is_paid:
        event_type = "Paid"
    mail.send(
        email,
        company_email,
        subject='Event Successfully Registered',
        html_message=f"<h2>Hi {first_name} - {last_name},</h2>"
                     f"<p>You have successfully registered for an event </p>"
                     f"<p>The event date {event.start_date} and the end time is {event.end_date}."
                     f"The location of the event is {event.location} and the event is {event_type}"
                     f"<a href='mailto:{company_email}'>{company_email}</a></p>",
        priority='now',
    )
    return True
