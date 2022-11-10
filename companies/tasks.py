from celery import shared_task
from post_office import mail


@shared_task
def send_request_to_admin(admin_email, user_email, message):
    """
    This function is meant to send a request to the admin from a user wanting to join a company
    :param message: The message the user is sending to the admin
    :param user_email: The user wanting tob join the organisation
    :type admin_email: object
    :return:
    """
    mail.send(
        admin_email,
        subject="Request to Join Organisation",
        html_message=message + f"\n If okay with user you can add him/her as a marketer or an admin "
                               f"in your organisation using the email  {user_email}",

        priority='now',
    )
    return True


@shared_task
def send_request_to_user(user_email, company_name):
    """
    This sends a request to the user who wants to join an organisation
     after requesting to join the organisation
    :param user_email: The user email
    :return:
    """
    mail.send(
        user_email,
        subject=f"Request to Join {company_name} was sent",
        html_message=f"Your request to Join {company_name} was sent.",
        priority="now",
    )
    return True
