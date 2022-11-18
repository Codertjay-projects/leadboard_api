from celery import shared_task
from decouple import config
from post_office import mail

LEADBOARD_INFO_MAIL = config("LEADBOARD_INFO_MAIL")
LEADBOARD_CUSTOMER_SUPPORT_MAIL = config("LEADBOARD_CUSTOMER_SUPPORT_MAIL")


@shared_task
def send_accepted_mail(email, first_name, last_name, company_email):
    mail.send(
        email,
        company_email,
        subject='Login Notification',
        html_message=f"<h2>Hi {first_name} - {last_name},</h2>"
                     f"<p> You have been accepted come for interview."
                     f"<a href='mailto:{company_email}'>{company_email}</a></p>",
        priority='now',
    )
    return True


@shared_task
def send_rejection_mail(email, first_name, last_name, company_email):
    mail.send(
        email,
        company_email,
        subject='Login Notification',
        html_message=f"<h2>Hi {first_name} - {last_name},</h2>"
                     f"<p> You have been rejected dont come for interview."
                     f"<a href='mailto:{company_email}'>{company_email}</a></p>",
        priority='now',
    )
    return True
