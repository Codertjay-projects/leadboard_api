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
    description = f"""
## Hi {first_name},

We have detected a new login to your Leadboard App account as at {datetime.datetime.now()}.

For security reasons, we want to make sure it was you. If this action is done by you, kindly disregard this notice.

If you did not login to your account, immediately change your password on the app and contact
[{LEADBOARD_INFO_MAIL}](mailto:{LEADBOARD_INFO_MAIL}).
        """

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
### Hello {first_name} {last_name}

Please use this OTP to complete your request: {otp}
    
If you haven't performed any action that requires an OTP, please contact us at {LEADBOARD_CUSTOMER_SUPPORT_MAIL}
"""

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
