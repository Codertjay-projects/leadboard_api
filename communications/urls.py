from django.urls import path

from communications.views import SendEmailSchedulerListCreateAPIView

urlpatterns = [
    path("send_email/", SendEmailSchedulerListCreateAPIView.as_view(), name="send_groups_email"),

]
