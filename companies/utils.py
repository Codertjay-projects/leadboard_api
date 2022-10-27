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
