from celery import shared_task
from post_office import mail


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
