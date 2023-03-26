from communications.utils import check_email
from events.models import EventRegister
from leads.models import LeadContact
from schedules.models import UserScheduleCall


def get_email_to(message_type, email_to_id, email):
    """
    this is used to get the email to which could be lead_contact,
    if returns none or the instance
    :return:
    """
    if message_type == "LEAD_GROUP":
        lead_contact = LeadContact.objects.filter(id=email_to_id).first()
        email = lead_contact.email
    elif message_type == "SCHEDULE_GROUP":
        user_schedule = UserScheduleCall.objects.filter(id=email_to_id).first()
        email = user_schedule.email
    elif message_type == "EVENT":
        event_register = EventRegister.objects.filter(id=email_to_id).first()
        email = event_register.email
    elif message_type == "ALL":
        email = email
    elif message_type == "CUSTOM":
        email = email
    elif message_type == "HIGHVALUECONTENT":
        # the highvalue content also uses the lead for the contenttype
        lead_contact = LeadContact.objects.filter(id=email_to_id).first()
        email = lead_contact.email
    # check if its a valid email
    if not check_email(email):
        return None
    return email
