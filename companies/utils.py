import random
import string

from high_value_contents.models import HighValueContent
from users.models import User
from companies.models import Group, Company


def get_username_not_in_db(company: Company, username) -> str:
    """"this returns a username that is not in the  database"""
    item_exist = Company.objects.filter(username=username).first()
    if item_exist:
        # if the item exist recreate the username
        # create random to string
        append_string = random.choices(string.ascii_letters, k=2)
        append_int = random.randint(1, 100)
        get_username_not_in_db(company, f"{username}_{append_string}{append_int}")
    return username


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
    if company.companyemployee_set.filter(user=user, status="ACTIVE", role="ADMIN").first():
        return True
    # check if the user is one of the marketers
    if company.companyemployee_set.filter(user=user, status="ACTIVE", role="MARKETER").first():
        return True
    return False


def check_admin_access_company(user: User, company: Company):
    # check if the user is the owner of the company
    if user == company.owner:
        return True
    # check if the user is one of the admin
    if company.companyemployee_set.filter(user=user, status="ACTIVE", role="ADMIN").first():
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
    random_assigned_marketer = company.companyemployee_set.filter(role="MARKETER").order_by("?").all().first().user
    if company.marketers_count() > 1:
        # if the random marker gotten was the last it recall the function
        if random_assigned_marketer == last_assigned_marketer:
            return get_random_marketer_not_last_marketer(last_assigned_marketer, company)
    return random_assigned_marketer


def get_random_admin_not_last_admin(last_assigned_admin: User, company: Company) -> User:
    """
    This is only used when there is no marketer
    this takes an assigned admin, and it is called if
    the random admin is not equal the last_assigned_admin
    :param company:
    :param last_assigned_admin: last admin on a lead or schedule
    :return: random_assigned_admin
    """
    random_assigned_admin = company.companyemployee_set.filter(role="ADMIN").order_by("?").all().first().user
    if company.admins_count() > 1:
        # if the random marker gotten was the last it recall the function
        if random_assigned_admin == last_assigned_admin:
            return get_random_admin_not_last_admin(last_assigned_admin, company)
    return random_assigned_admin


def get_assigned_marketer_from_company_lead(company: Company):
    """
    This function get a user from the company . 
    first it looks for a random user who was not the last assigned marketer on a lead.
    or
    it uses the admin if the company have no  marketers
    or
    it uses the owner of the company
    """
    last_lead = company.leadcontact_set.first()
    if not last_lead:
        # the first lead is managed by the owner
        return company.owner
    if company.marketers_count() > 1:
        # if the company have more than one marketer then we can get a random one
        # check if the last lead have a assigned marketer
        if last_lead.assigned_marketer:
            last_assigned_marketer = last_lead.assigned_marketer
            # get a random assigned marketer
            assigned_marketer = get_random_marketer_not_last_marketer(last_assigned_marketer, company)
            return assigned_marketer
        else:
            return company.first_marketer_user()
    elif company.marketers_count() == 1:
        # company have only one marketer, so we can just use the one we have
        return company.first_marketer_user()
    elif company.admins_count() > 1:
        # if the company have more than one marketer then we can get a random one
        # check if the last lead have a assigned marketer
        if last_lead.assigned_marketer:
            last_assigned_admin = last_lead.assigned_marketer
            # get a random assigned admin
            assigned_admin = get_random_admin_not_last_admin(last_assigned_admin, company)
            return assigned_admin
        else:
            return company.first_admin_user()
    elif company.admins_count() == 1:
        # company have only one admin, so we can just use the one we have
        return company.first_admin_user()
    else:
        return company.owner


def get_assigned_marketer_from_company_user_schedule_call(company: Company):
    """
    This function get a user from the company .
    first it looks for a random user who was not the last assigned markter on a user_schedule_call.
    or
    it uses the admin if the company have no  marketers
    or
    it uses the owner of the company
    """
    last_user_schedule_call = company.userschedulecall_set.first()
    if not last_user_schedule_call:
        # the first user_schedule_call is managed by the owner
        return company.owner
    if company.marketers_count() > 1:
        # if the company have more than one marketer then we can get a random one
        # check if the last user_schedule_call have a assigned marketer
        if last_user_schedule_call.assigned_marketer:
            last_assigned_marketer = last_user_schedule_call.assigned_marketer
            # get a random assigned marketer
            assigned_marketer = get_random_marketer_not_last_marketer(last_assigned_marketer, company)
            return assigned_marketer
        else:
            return company.first_marketer_user()
    elif company.marketers_count() == 1:
        # company have only one marketer, so we can just use the one we have
        return company.first_marketer_user()
    elif company.admins_count() > 1:
        # if the company have more than one marketer then we can get a random one
        # check if the last user_schedule_call have a assigned marketer
        if last_user_schedule_call.assigned_marketer:
            last_assigned_admin = last_user_schedule_call.assigned_marketer
            # get a random   admin from the company
            assigned_admin = get_random_admin_not_last_admin(last_assigned_admin, company)
            return assigned_admin
        else:
            return company.first_admin_user()
    elif company.admins_count() == 1:
        # company have only one admin, so we can just use the one we have
        return company.first_admin_user()
    else:
        return company.owner
