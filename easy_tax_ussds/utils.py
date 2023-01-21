from rest_framework.response import Response
from .models import EasyTaxUSSDLGA, EasyTaxUSSDState, EasyTaxUSSD


def stage_begin(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this is the beginning of the stage
    """
    # If the command is BEGIN we start the process
    content = "1. Have TIN? Press 1 \n"
    content += "2. To create new account, press 2"
    # Set the last command if the user chooses 1
    easy_tax_ussd.set_command("stage_begin")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_have_tin(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this part is where the user have the tin stage after pressing 1
    """
    # If the User Chose have tin we give the user this response
    content = "1. Pay Tax \n"
    content += "2. Check Balance"
    # Set the last command if the user chooses 1
    easy_tax_ussd.set_command("stage_have_tin")

    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_create_account(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    This is used to create account number
    """
    content = "Enter you full name"
    easy_tax_ussd.set_command("stage_create_account")

    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_pay_tax(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this is where you put in you select the bank
    """
    content = "1. Select Bank \n"
    content += "2. Pay With Voucher \n"

    easy_tax_ussd.set_command("stage_pay_tax")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_select_bank(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this is where you put in you select the bank
    """
    content = "Select Bank \n"
    content += "1. Access \n"
    content += "2. UBA \n"
    content += "3. GTBank \n"
    content += "4. Sterling \n"

    easy_tax_ussd.set_command("stage_select_bank")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_pay_with_voucher(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this is where you put in you select the bank
    """
    content = "Enter Voucher "
    easy_tax_ussd.set_command("stage_pay_with_voucher")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_check_balance(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this is the stage where the user check balance
    """
    content = f"Account Balance: {easy_tax_ussd.balance}"
    easy_tax_ussd.delete_command()
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_enter_voucher(phone_number,
                        service_provider,
                        service_code,
                        easy_tax_ussd):
    content = "Successfully Entered voucher"
    easy_tax_ussd.delete_command()
    return Response({
        "command": "End",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_bank_chosen(
        bank_name,
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this is used when the user have chosen a bank account
    """
    if bank_name == "ACCESS":
        content = "Access 0000000000"
    elif bank_name == "UBA":
        content = "UBA 0000000000"
    elif bank_name == "GTBANK":
        content = "GTBank 0000000000"
    elif bank_name == "STERLING":
        content = "STERLING 0000000000"
    else:
        content = "Please Input the right number"
    easy_tax_ussd.delete_command()
    return Response({
        "command": "End",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_male_or_female(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    The stage where the user chooses either male or female
    """
    content = ""
    if easy_tax_ussd.gender:
        content += "Updating Account"
    content += "If you are a male, press 1 \n "
    content += "If you are a female, press  2 \n "
    easy_tax_ussd.set_command("stage_male_or_female")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_year_of_birth(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    The stage what ask the users his date of birth
    """
    content = "Enter your year of birth.\n "
    easy_tax_ussd.set_command("stage_year_of_birth")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_select_state(
        from_range,
        to_range,
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    this is where the user checks the local government
    """
    content = "Select your State"
    easy_tax_ussd.set_state_range(from_range, to_range)
    for item in EasyTaxUSSDState.objects.all()[from_range:to_range]:
        content += f"{item.id} {item.name} \n"
    content += "Next"
    easy_tax_ussd.set_command("stage_select_state")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_select_local_government(
        from_range,
        to_range,
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd: EasyTaxUSSD):
    """
    this is where the user checks the local government
    """
    content = "Select your Local Government Area"
    easy_tax_ussd.set_lga_range(from_range, to_range)
    # Get the local government in a state with the state the user chose
    for item in easy_tax_ussd.state.easytaxussdlga_set.all()[from_range:to_range]:
        content += f"{item.id}. {item.name} \n"
    # Check if the count is greater than 10
    if easy_tax_ussd.state.easytaxussdlga_set.all().count() > to_range:
        content += "Next"
    easy_tax_ussd.set_command("stage_select_local_government")
    return Response({
        "command": "Continue",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_registration_successful(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    The stage where the user cancel
    """
    content = "Registration Successful"
    easy_tax_ussd.delete_command()
    return Response({
        "command": "End",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)


def stage_cancel(
        phone_number,
        service_provider,
        service_code,
        easy_tax_ussd):
    """
    The stage where the user cancel
    """
    content = "Successfully canceled"
    easy_tax_ussd.delete_command()
    return Response({
        "command": "End",
        "msisdn": phone_number,
        "src": service_provider,
        "serviceCode": service_code,
        "content": content,
    }, status=200)
