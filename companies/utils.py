from users.models import User
from companies.models import Group


def check_marketer_and_admin_access_group(user: User, group :Group):
    # check if the user is an admin
    if user in group.company.admins.all():
        return True
    #  if the user is a marketer
    elif user in group.company.marketers.all():
        return True
    # if the user is the owner of the company
    elif user == group.company.owner():
        return True
    # if the user does not have access above
    return False


