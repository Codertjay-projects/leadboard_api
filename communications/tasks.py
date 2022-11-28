from celery import shared_task
from post_office import mail


@shared_task
def send_email_custom_schedule_task(
        to_email,
        subject, reply_to, description, scheduled_date, company_info_email, company_name):
    mail.send(
        to_email,
        headers={
            "reply_to": reply_to
        },
        subject=subject,
        html_message=f""
                     f"{description}"
                     f"Message from {company_name} "
                     f"<a href='mailto:{company_info_email}'>{company_info_email}</a></p>",
        scheduled_time=scheduled_date
    )


@shared_task
def send_email_group_schedule_task(to_email,
                                   subject,
                                   reply_to,
                                   first_name,
                                   last_name, description,
                                   scheduled_date,
                                   company_info_email,
                                   company_name):
    """

    This is used by the SendGroupsEmailSchedulerLog on post_save so once the log is created
    we just send the mail with the schedule time .
    :return:
    """
    mail.send(
        to_email,
        subject=subject,
        headers={
            "Reply-to": reply_to,
        },
        html_message=f"<h1> Hello {first_name} - {last_name}. </h1>"
                     f"<p>{description}</p> "
                     f"<div>Yor are getting this message from {company_name}"
                     f"<img "
                     f"src='http://production.codertjay.com:8001/api/v1/companies/email_read/?company_id=280fb0d16f5446829aea1948d75bd612' "
                     f"alt='Image'> "
                     f"<a href='mailto:{company_info_email}'>{company_info_email}</a></p>",
        scheduled_time=scheduled_date
    )
