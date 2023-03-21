from events.models import EventRegister
from leads.models import LeadContact


def get_email_to(message_type, email_to_id):
    """
    this is used to get the email to which could be lead_contact,
    if returns none or the instance
    :return:
    """
    if message_type == "GROUP":
        lead_contact = LeadContact.objects.filter(id=email_to_id).first()
        return lead_contact
    elif message_type == "EVENT":
        event_register = EventRegister.objects.filter(id=email_to_id).first()
        return event_register
    return None
