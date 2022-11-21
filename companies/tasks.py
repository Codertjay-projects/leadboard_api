from celery import shared_task
from django.utils import timezone
from post_office import mail

from companies.models import SendGroupsEmailScheduler


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
    This is used to send email using this SendGroupsEmailScheduler model
    where we get the leads to send follow-ups
    """
    # Get the shedulemail  not sent and also the once which fails to sent and the
    # once which email is less that the current date time
    send_groups_email_scheduler_qs = SendGroupsEmailScheduler.objects.filter(
        status="PENDING", scheduled_date__lte=timezone.now())

    # Next Get the leads that are connected to this
    groups = send_groups_email_scheduler_qs.values_list("email_to__lead_groups")
