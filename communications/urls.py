from django.urls import path

from communications.views import SendGroupsEmailSchedulerListCreateAPIView, SendCustomEmailSchedulerListCreateAPIView

urlpatterns = [
    path("send_groups_email/", SendGroupsEmailSchedulerListCreateAPIView.as_view(), name="send_groups_email"),
    path("send_custom_email/", SendCustomEmailSchedulerListCreateAPIView.as_view(), name="send_custom_email"),

]
