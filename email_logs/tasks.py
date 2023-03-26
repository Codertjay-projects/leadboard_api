from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from communications.utils import append_links_and_id_to_description, modify_names_on_description
from leadboard_api.lead_celery import app

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


@app.task
def leadboard_send_mail(
        message_id,
        company_name,
        email_to,
        reply_to,
        email_subject,
        description,
        message_type,
):
    """
    message_id : this could be none not required but if passed we use it to access the mail from the log
    company_name: the company_name
    email_to: the mail to is an email
    reply_to: the mail the user can reply to
    email_subject: the subject of the mail
    description: content
    this takes the normal params the default send mails needs, but we just add some extra filed
    """
    from .models import EmailLog

    try:
        # the update updates all queryset with the id
        log = EmailLog.objects.filter(id=message_id).first()

        headers = {"Reply-To": reply_to}

        #  append link and id to the description
        description = append_links_and_id_to_description(
            description=description,
            email_id=message_id,
            email_type=message_type
        )

        if log.message_type == "LEAD_GROUP" or log.message_type == "SCHEDULE_GROUP" or \
                log.message_type == "EVENT":
            # modify the first_name and last_name and also use the content type to access the model
            model_instance = log.email_to.get_object_for_this_type(id=log.email_to_instance_id)
            first_name = model_instance.first_name
            last_name = model_instance.last_name
            description = modify_names_on_description(
                description=description,
                first_name=first_name,
                last_name=last_name
            )

        html_message = render_to_string('mail.html', {"description": description})

        msg = EmailMessage(
            subject=email_subject,
            body=html_message,
            headers=headers,
            from_email=f"{company_name} <lead@instincthub.com>",
            to=[email_to]
        )
        msg.content_subtype = "html"
        msg.send()
        # the update updates all queryset with the id
        log = EmailLog.objects.filter(id=message_id).first()
        if log:
            # Update the log status
            log.status = "SENT"
            log.max_retries += 1
            log.save()
            # increase the number of email the company has send with one
            company = log.company
            if not company.premium_access:
                company.email_sent_count += 1
                company.save()
        return True
    except Exception as a:
        # the update updates all queryset with the id
        log = EmailLog.objects.filter(id=message_id).first()
        if log is not None:
            log.status = "FAILED"
            log.max_retries += 1
            log.error = f"{a}"
            # resend the email in the next 10 minutes
            log.scheduled_date = timezone.now() + timedelta(minutes=10)
            log.save()
        return False


@shared_task
def send_custom_mail(reply_to, description, email_subject, company_name, email_to):
    headers = {"Reply-To": reply_to}
    html_message = render_to_string('mail.html', {"description": description})
    msg = EmailMessage(
        subject=email_subject,
        body=html_message,
        headers=headers,
        from_email=f"{company_name} <lead@instincthub.com>",
        to=[email_to]
    )
    msg.content_subtype = "html"
    msg.send()
