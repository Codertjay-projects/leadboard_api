import datetime

from celery import shared_task
from decouple import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

LEADBOARD_INFO_MAIL = config("LEADBOARD_INFO_MAIL")
LEADBOARD_CUSTOMER_SUPPORT_MAIL = config("LEADBOARD_CUSTOMER_SUPPORT_MAIL")


@shared_task
def login_notification_email(first_name, email):
    """this sends an email to the user once he logs in  """
    headers = {"Reply_to": LEADBOARD_INFO_MAIL}
    description = f"""<h2>Hi {first_name},</h2> <p>We have detected a new login to your Leadboard App account as at
                      {datetime.datetime.now()}</p>
                     <p>For security reasons, we want to make sure it was you. If this action is done by you,
                      kindly disregard this notice.</p> 
                     <p>If you did not login to your account, immediately change your password on the app and contact 
                     <a href='mailto:{LEADBOARD_INFO_MAIL}'>{LEADBOARD_INFO_MAIL}</a></p>"""

    html_message = render_to_string('mail.html', {"description": description})
    msg = EmailMessage(
        subject="Login Notification",
        body=html_message,
        headers=headers,
        from_email=f"leadboard <skills@instincthub.com>",
        to=[email]
    )
    msg.content_subtype = "html"
    msg.send()
    return True


@shared_task
def send_otp_to_email_task(otp, email, first_name, last_name):
    """
    This sends an email to the logged-in user for verification
    """
    headers = {"Reply_to": LEADBOARD_INFO_MAIL}
    description = f"""
       <h3> Hello {first_name} {last_name} </h3>
       <p>
        Please use this OTP to complete your request:{otp}
        </br> If you haven't performed and action that requires an OTP please contact us
        </p>
        f"contact <a href='mailto:{LEADBOARD_CUSTOMER_SUPPORT_MAIL}'>{LEADBOARD_INFO_MAIL}</a></p>"""

    html_message = render_to_string('mail.html', {"description": description})
    msg = EmailMessage(
        subject="Leadboard App Request OTP",
        body=html_message,
        headers=headers,
        from_email=f"leadboard <lead@instincthub.com>",
        to=[email]
    )
    msg.content_subtype = "html"
    msg.send()
    return True
