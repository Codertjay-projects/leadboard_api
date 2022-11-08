from high_value_contents.models import HighValueContent
from users.models import User
from companies.models import Group, Company


def check_group_is_under_company(company: Company, group: Group):
    # check if the user is an admin
    if company == group.company:
        return True
    return False


def check_marketer_and_admin_access_company(user: User, company: Company):
    # check if the user is the owner of the company
    if user == company.owner:
        return True
    # check if the user is one of the admin
    if user in company.admins.all():
        return True
    # check if the user is one of the marketers
    if user in company.marketers.all():
        return True
    return False


def check_admin_access_company(user: User, company: Company):
    # check if the user is the owner of the company
    if user == company.owner:
        return True
    # check if the user is one of the admin
    if user in company.admins.all():
        return True
    return False


def check_company_high_value_content_access(high_value_content: HighValueContent, company: Company):
    """
    this function is used to check the high value content, and it returns a boolean either
    true or false if the company is the owner of that content
    :param high_value_content:
    :param company:
    :return: bool
    """
    if high_value_content.company != company:
        return False
    return True


def get_random_marketer_not_last_marketer(last_assigned_marketer: User, company: Company) -> User:
    """
    this takes an assigned marketer, and it is called if
    the random marketer is not equal this
    :param last_assigned_marketer: last marketer on a lead or schedule
    :return:
    """
    random_assigned_marketer = company.marketers.order_by("?").all().first()
    if company.marketers.count() > 1:
        # if the random marker gotten was the last it recall the function
        if random_assigned_marketer == last_assigned_marketer:
            return get_random_marketer_not_last_marketer(last_assigned_marketer, company)
    return random_assigned_marketer


def get_random_admin_not_last_admin(last_assigned_admin: User, company: Company) -> User:
    """
    this takes an assigned admin, and it is called if
    the random admin is not equal this
    :param last_assigned_admin: last admin on a lead or schedule
    :return:
    """
    random_assigned_admin = company.admins.order_by("?").all().first()
    if company.admins.count() > 1:
        # if the random marker gotten was the last it recall the function
        if random_assigned_admin == last_assigned_admin:
            return get_random_admin_not_last_admin(last_assigned_admin, company)
    return random_assigned_admin


def get_assigned_marketer_from_company_lead(company: Company):
    """
    This function get a user from the company . 
    first it looks for a random user who was not the last assingned markterv on a lead.
    or
    it uses the admin if the company have no  marketers
    or
    it uses the owner of the company
    """
    last_lead = company.leadcontact_set.first()
    if not last_lead:
        # the first lead is managed by the owner
        return company.owner
    if company.marketers.count() > 1:
        # if the company have more than one marketer then we can get a random one
        # check if the last lead have a assigned marketer
        if last_lead.assigned_marketer:
            last_assigned_marketer = last_lead.assigned_marketer
            # get a random assigned marketer
            assigned_marketer = get_random_marketer_not_last_marketer(last_assigned_marketer, company)
            return assigned_marketer
        else:
            return company.marketers.first()
    elif company.marketers.count() == 1:
        # company have only one marketer, so we can just use the one we have
        return company.marketers.first()
    elif company.admins.count() > 1:
        # if the company have more than one marketer then we can get a random one
        # check if the last lead have a assigned marketer
        if last_lead.assigned_admin:
            last_assigned_admin = last_lead.assigned_admin
            # get a random assigned admin
            assigned_admin = get_random_admin_not_last_admin(last_assigned_admin, company)
            return assigned_admin
        else:
            return company.admins.first()
    elif company.admins.count() == 1:
        # company have only one admin, so we can just use the one we have
        return company.admins.first()
    else:
        return company.owner
