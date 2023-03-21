from django.urls import path

from email_logs.views import EmailUpdateViewCountAPIView, EmailUpdateLinkClickedView

urlpatterns = [
    path("update_view_count/", EmailUpdateViewCountAPIView.as_view(), name="update_view_count"),
    path("update_links_clicked/", EmailUpdateLinkClickedView.as_view(), name="update_links_clicked"),
]
