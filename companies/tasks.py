from celery import shared_task
from post_office import mail


@shared_task
def send_email_schedule_task(to_email,
                             subject,
                             reply_to,
                             first_name,
                             last_name, description,
                             scheduled_date,
                             company_info_email,
                             company_name):
    # This is used to send an email from the lead
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


@shared_task
def send_request_to_user(company_name, invitation_id, first_name, last_name, user_email):
    """
    This sends a request to the user who wants to join an organisation
     after requesting to join the organisation
    :param first_name: First name of the user
    :param last_name: Last name of the user
    :param company_name: The name of the company
    :param invitation_id: The invitation to join
    :param user_email: The user email
    :return:
    """
    mail.send(
        user_email,
        subject=f"Invitation to Join {company_name}",
        html_message=f"<h1> Hello {first_name} - {last_name}. </h1>"
                     f"<p>{company_name} has invited you to join the their organisation you can use this code to join "
                     f"{invitation_id}</p>   ",
        priority="now",
    )
    return True


@shared_task
def send_schedule_custom_email():
    """
    This is used to send email using this SendCustomEmailScheduler model
    the pending_mail_info is in this format :
    info = [{
                "custom_id": item[0],
                "email_subject": item[1],
                "description": item[2],
                "email_list": [mail1,mail2,mail3,mail4,mail5,mail6,mail7 ....],
                "company__info_email": item[4],
                "company__customer_support_email": item[5],
                "company__name": item[6],
                "company__id": item[7],
                "scheduled_date": datetime,

            },....]
    """
    from companies.models import SendCustomEmailScheduler

    # Get the scheduled mail which are  currently pending which is a list of dictionaries
    pending_mail_info = SendCustomEmailScheduler.objects.get_lead_emails(status="PENDING")
    for item in pending_mail_info:
        if not item.get('email_list'):
            # Skip if the is not list
            continue
        if not isinstance(item.get('email_list'), list):
            # If the instance is not a list I skip also
            continue
        for item_mail in item.get('email_list'):
            mail.send(
                item_mail,
                headers={
                    "Reply-to": item.get("company__customer_support_email"),
                    "company_id": item.get("company_id"),
                },
                subject=item.get("email_subject"),
                html_message=f"<h1> Hello {item.get('first_name')} - {item.get('last_name')}. </h1>"
                             f"<p>{item.get('description')}</p> "
                             f"<div>Yor are getting this message from {item.get('company__name')}"
                             f"<img src='http://production.codertjay.com:8001/api/v1/companies/email_read/?company_id=280fb0d16f5446829aea1948d75bd612' alt=''>"
                             f"<a href='mailto:{item.get('company__info_email')}'>{item.get('company__info_email')}</a>",
                scheduled_time=item.get("scheduled_date")
            )
    # Update all Pending to sent
    SendCustomEmailScheduler.objects.update_all_schedule_status_to_sent()
