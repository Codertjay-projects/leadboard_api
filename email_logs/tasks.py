from datetime import timedelta

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from communications.utils import update_group_schedule_log_status, update_custom_schedule_log_status
from leadboard_api.lead_celery import app


@app.task
def leadboard_send_mail(
        message_id,
        company_name,
        email_to,
        reply_to,
        email_subject,
        description,
):
    """
    message_id : this could be none not required but if passed we use it to access the mail from the log
    company_name: the company_name
    email_to: the mail to
    reply_to: the mail the user can reply to
    email_subject: the subject of the mail
    description: content
    this takes the normal params the default send mails needs, but we just add some extra filed
    """
    from .models import EmailLog

    try:

        headers = {"Reply-To": reply_to}
        html_message = render_to_string('mail.html', {"description": description})
        msg = EmailMessage(
            subject=email_subject,
            body=html_message,
            headers=headers,
            from_email=f"{company_name} <skills@instincthub.com>",
            to=[email_to]
        )
        msg.content_subtype = "html"
        msg.send()
        # the update updates all queryset with the id
        log = EmailLog.objects.filter(
            message_id=message_id).first()
        if log:
            # Update the log if the email has been sent
            if log.message_type == "CUSTOM":
                update_custom_schedule_log_status(id=log.message_id, status="SENT")
            elif log.message_type == "GROUP":
                update_group_schedule_log_status(id=log.message_id, status="SENT")
            # Update the log status
            log.status = "SENT"
            log.max_retries += 1
            log.save()
        return True
    except Exception as a:
        # the update updates all queryset with the id
        log = EmailLog.objects.filter(
            message_id=message_id).first()
        if log is not None:
            # Update the log if the email failed
            if log.message_type == "CUSTOM":
                update_group_schedule_log_status(id=log.message_id, status="FAILED")
            elif log.message_type == "GROUP":
                update_group_schedule_log_status(id=log.message_id, status="FAILED")

            log.status = "FAILED"
            log.max_retries += 1
            log.error = f"{a}"
            # resend the email in the next 10 minutes
            log.scheduled_date = timezone.now() + timedelta(minutes=10)
            log.save()
        return False
