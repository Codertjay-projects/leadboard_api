from celery import shared_task
from post_office import mail

from high_value_contents.models import HighValueContent


@shared_task
def send_high_value_content_verify(company_email, first_name, last_name, email, high_value_content_id):
    """
    this is meant to verify the email and also send the users an email
    """
    high_value_content = HighValueContent.objects.filter(id=high_value_content_id).first()
    if not high_value_content:
        return False
    mail.send(
        email,
        company_email,
        subject=f'{high_value_content.title}',
        html_message=f"<h2>Hi {first_name} - {last_name},</h2>"
                     f"<p> This is the ebook or file link ."
                     f"<a href='mailto:{company_email}'>{company_email}</a></p>",
        priority='now',
    )
    return True
