# Create your views here.
from django.http import HttpResponseRedirect
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from email_logs.models import EmailLog


class EmailUpdateViewCountAPIView(APIView):
    """
    This view is used to increase the number of read email by the users on the organisation
    using the organisations ID

    This would be set on the mail as an image
    """

    def get(self, request, *args, **kwargs):
        email_type = self.request.GET.get("email_type")
        email_id = self.request.GET.get("email_id")
        log = EmailLog.objects.filter(id=email_id).first()
        if log:
            log.view_count += 1
            log.save()
        return Response({"message": "Successfully open mail"}, status=200)


class EmailUpdateLinkClickedView(View):
    """
    This update the view counts of email logs  for custom and group emails
    ALso it used to verify the email of the user
    Base on the email_type we set of logic
    if the email_type is custom or group we only need to append the links clicked
    , if it is high_value_content then we set the email to be verified

    """

    def get(self, request, *args, **kwargs):
        email_type = request.GET.get('email_type')
        redirect_url = request.GET.get('redirect_url')
        email_id = request.GET.get('email_id')

        # This is used for tracking all emails sent
        if email_type:
            # filter for the high value content and others emails sent
            email_log = EmailLog.objects.filter(
                id=email_id).first()
            # Verify the user email
            if email_log:
                email_log.links_clicked = f"{email_log.links_clicked},{redirect_url}"
                email_log.links_clicked_count += 1
                email_log.save()

        return HttpResponseRedirect(redirect_url)
