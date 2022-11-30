import re


def check_email(email) -> bool:
    # The regular expression
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(pat, email):
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
        f"https:")
    description = description.replace(
        "https",
        f"https://production.codertjay.com:8001/api/v1/communications/update_links_clicked/?&email_type={email_type}"
        f"&email_id={email_id}&redirect_url=https"
    )
    return description
