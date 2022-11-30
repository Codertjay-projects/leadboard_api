from celery import shared_task
from post_office import mail


@shared_task
def send_email_custom_schedule_task(
        to_email,
        subject, reply_to, description, scheduled_date, company_info_email, company_name, email_id):
    mail.send(
        to_email,
        headers={
            "reply_to": reply_to
        },
        subject=subject,
        html_message=f""
                     f"{description}"
                     f"<img src='http://production.codertjay.com:8001/api/v1/communications/update_view_count/"
                     f"?email_id={email_id}&email_type=custom'/>",
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
                                   company_name,
                                   email_id
                                   ):
    # The reason why I create this is just because the group have a name so maybe the message might be different
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
                     f"<p>{description}</p>"
                     f"<img src='http://production.codertjay.com:8001/api/v1/communications/update_view_count/"
                     f"?email_id={email_id}&email_type=group'/>",
        scheduled_time=scheduled_date
    )
