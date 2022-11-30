from django.urls import path

from communications.views import SendGroupsEmailSchedulerListCreateAPIView, SendCustomEmailSchedulerListCreateAPIView, \
    EmailUpdateViewCountAPIView, EmailUpdateLinkClickedView

urlpatterns = [
    path("send_groups_email/", SendGroupsEmailSchedulerListCreateAPIView.as_view(), name="send_groups_email"),
    path("send_custom_email/", SendCustomEmailSchedulerListCreateAPIView.as_view(), name="send_custom_email"),
    path("update_view_count/", EmailUpdateViewCountAPIView.as_view(), name="update_view_count"),
    path("update_links_clicked/", EmailUpdateLinkClickedView.as_view(), name="update_links_clicked"),

]
