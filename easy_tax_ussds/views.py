from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from easy_tax_ussds.models import EasyTaxUSSD, EasyTaxUSSDLGA, EasyTaxUSSDState
from easy_tax_ussds.utils import stage_begin, stage_have_tin, stage_create_account, stage_pay_tax, stage_check_balance, \
    stage_cancel, stage_select_bank, stage_pay_with_voucher, stage_enter_voucher, stage_bank_chosen, \
    stage_male_or_female, stage_year_of_birth, stage_select_local_government, stage_registration_successful, \
    stage_select_state


class EasyTaxUSSDAPIView(APIView):
    """
    the api allow any request from the server
    """
    permission_classes = [AllowAny]

    def get(self,request):
        return Response(status=200)

    def post(self, request):
        """
        the is a post request that get info from the USSD
        """
        # The datas sent from the service provider
        command = request.data.get("command")
        # the phone number
        phone_number = request.data.get("msisdn")
        # mtn or glo
        service_provider = request.data.get("src")
        # *7003 any service code
        service_code = request.data.get("serviceCode")
        # The content could be 1,2 or text
        content = request.data.get("content")

        print("the requet data ",request.data)
        # Phone number instance
        if not phone_number:
            # Phone number not passed
            return Response({"command": "End", "Content": "Phone number not passed"}, status=200)
        easy_tax_ussd, created = EasyTaxUSSD.objects.get_or_create(phone_number=phone_number)
        print(command)
        print(command == "Begin")
        print(command == "begin")
        if command:
            # The first command the user
            return stage_begin(
                phone_number=phone_number,
                easy_tax_ussd=easy_tax_ussd,
                service_code=service_code,
                service_provider=service_provider
            )
        elif command == "Continue":
            if easy_tax_ussd.get_last_command() == "stage_begin":
                # This means the user have tin
                if content == "1":
                    # If the stage is begun and the user chooses he has tin
                    return stage_have_tin(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content == "2":
                    # This is the stage if the user chooses he wants to create account
                    return stage_create_account(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
            elif easy_tax_ussd.get_last_command() == "stage_have_tin":
                # if the content is 1 and the
                if content == "1":
                    # Return the stage the user is in
                    return stage_pay_tax(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content == "2":
                    # Return the stage check balance
                    return stage_check_balance(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content == "3":
                    # Return the stage cancel
                    return stage_cancel(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
            elif easy_tax_ussd.get_last_command() == "stage_pay_tax":
                # If content is 1 we select bank
                if content == "1":
                    # Return stage for the user to select bank
                    return stage_select_bank(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content == "2":
                    # Return the stage for the user to input voucher
                    return stage_pay_with_voucher(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
            elif easy_tax_ussd.get_last_command() == "stage_pay_with_voucher":
                # The stage where the user enter voucher
                return stage_enter_voucher(
                    phone_number=phone_number,
                    easy_tax_ussd=easy_tax_ussd,
                    service_code=service_code,
                    service_provider=service_provider
                )

            elif easy_tax_ussd.get_last_command() == "stage_select_bank":
                # The create new account
                if content == "1":
                    # The user chose ACCESS
                    return stage_bank_chosen(
                        bank_name="ACCESS",
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content == "2":
                    # The user chose UBA
                    return stage_bank_chosen(
                        bank_name="UBA",
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content == "3":
                    # The user chose GTBANK
                    return stage_bank_chosen(
                        bank_name="GTBANK",
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content == 4:
                    # The user chose STERLING
                    return stage_bank_chosen(
                        bank_name="STERLING",
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )

            elif easy_tax_ussd.get_last_command() == "stage_create_account":
                # If the user chooses to create account
                easy_tax_ussd.full_name = content
                easy_tax_ussd.save()
                return stage_male_or_female(
                    phone_number=phone_number,
                    easy_tax_ussd=easy_tax_ussd,
                    service_code=service_code,
                    service_provider=service_provider
                )
            elif easy_tax_ussd.get_last_command() == "stage_male_or_female":
                # if the user chooses the input for the male and female we then direct the user here
                # If the user chooses to create account
                if content == "1":
                    easy_tax_ussd.gender = "MALE"
                elif content == "2":
                    easy_tax_ussd.gender = "FEMALE"
                easy_tax_ussd.save()
                return stage_year_of_birth(
                    phone_number=phone_number,
                    easy_tax_ussd=easy_tax_ussd,
                    service_code=service_code,
                    service_provider=service_provider
                )
            elif easy_tax_ussd.get_last_command() == "stage_year_of_birth":
                # If the user chooses the year of birth we how the user local government
                easy_tax_ussd.year_of_birth = content
                easy_tax_ussd.save()
                return stage_select_state(
                    from_range=0,
                    to_range=10,
                    phone_number=phone_number,
                    easy_tax_ussd=easy_tax_ussd,
                    service_code=service_code,
                    service_provider=service_provider
                )

            elif easy_tax_ussd.get_last_command() == "stage_select_state":
                if content == "99":
                    # This means the user chose next
                    state_range = easy_tax_ussd.get_state_range()
                    if not state_range:
                        return stage_cancel(
                            phone_number=phone_number,
                            easy_tax_ussd=easy_tax_ussd,
                            service_code=service_code,
                            service_provider=service_provider
                        )
                    # I increase the range
                    new_from_range = int(state_range[0]) + 10
                    new_to_range = int(state_range[1]) + 10
                    return stage_select_local_government(
                        from_range=new_from_range,
                        to_range=new_to_range,
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content:
                    # In here the content could be any number
                    # Convert the content to index
                    try:
                        content_index = int(content)
                    except Exception as a:
                        return stage_cancel(
                            phone_number=phone_number,
                            easy_tax_ussd=easy_tax_ussd,
                            service_code=service_code,
                            service_provider=service_provider
                        )
                    state = EasyTaxUSSDState.objects.filter(id=content_index).first()
                    if not state:
                        # If the index does not exist I cancel it
                        return stage_cancel(
                            phone_number=phone_number,
                            easy_tax_ussd=easy_tax_ussd,
                            service_code=service_code,
                            service_provider=service_provider
                        )
                    easy_tax_ussd.state = state
                    easy_tax_ussd.save()
                    return stage_select_local_government(
                        from_range=0,
                        to_range=10,
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
            elif easy_tax_ussd.get_last_command() == "stage_select_local_government":
                if content == "99":
                    # This means the user chose next
                    if not easy_tax_ussd.get_lga_range():
                        return stage_cancel(
                            phone_number=phone_number,
                            easy_tax_ussd=easy_tax_ussd,
                            service_code=service_code,
                            service_provider=service_provider
                        )
                    # I increase the range
                    new_from_range = int(easy_tax_ussd.get_lga_range()[0]) + 10
                    new_to_range = int(easy_tax_ussd.get_lga_range()[1]) + 10
                    return stage_select_local_government(
                        from_range=new_from_range,
                        to_range=new_to_range,
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
                elif content:
                    # In here the content could be any number
                    # Convert the content to index
                    try:
                        content_index = int(content)
                    except Exception as a:
                        return stage_cancel(
                            phone_number=phone_number,
                            easy_tax_ussd=easy_tax_ussd,
                            service_code=service_code,
                            service_provider=service_provider
                        )
                    lga = EasyTaxUSSDLGA.objects.filter(id=content_index).first()
                    if not lga:
                        # If the index does not exist I cancel it
                        return stage_cancel(
                            phone_number=phone_number,
                            easy_tax_ussd=easy_tax_ussd,
                            service_code=service_code,
                            service_provider=service_provider
                        )
                    easy_tax_ussd.lga = lga
                    easy_tax_ussd.save()
                    return stage_registration_successful(
                        phone_number=phone_number,
                        easy_tax_ussd=easy_tax_ussd,
                        service_code=service_code,
                        service_provider=service_provider
                    )
        return Response({"command": "End", "Content": "Please input the right content"}, status=200)
