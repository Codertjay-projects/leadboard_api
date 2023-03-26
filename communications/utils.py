import re


def check_email(email) -> bool:
    # The regular expression
    if not email:
        return False
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(pat, email.replace(" ", "")):
        return True
    else:
        return False


def append_links_and_id_to_description(description, email_type, email_id):
    """
    This updates the links http://docs.django.com
    to https://production.codertjay.com/?url=http://docs.djang.com&type=custom&id=uuid
    :param email_id: The id of the email
    :param email_type: The email type is custom, group or more, but it used but the link clicked class
    :param description: text description
    :return: description
    """

    description = description.replace(
        "http:",
        f"https:"
    )
    description = description.replace(
        "https",
        f"https://leadapi.instincthub.com/api/v1/email_logs/update_links_clicked/?&email_type={email_type}"
        f"&email_id={email_id}&redirect_url=https"
    )
    return description


def modify_names_on_description(description, first_name, last_name):
    """
    this is used to modify the first name and last name if passed as first_name and last_name
    on the description
    :return: description
    """
    # replace first_name
    if first_name:
        description = description.replace(
            "first_name", first_name)
    else:
        description = description.replace(
            "first_name", " "
        )
    #  replace last_name
    if last_name:
        description = description.replace(
            "last_name", last_name)
    else:
        description = description.replace(
            "last_name", " "
        )
    return description
