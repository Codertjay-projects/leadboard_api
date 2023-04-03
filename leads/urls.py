from django.urls import path

from .views import LeadContactRetrieveUpdateDestroyAPIView, LeadContactCreateListAPIView, LeadStatsRetrieveAPIView, \
    LeadUploadAPIView

#  if you realized we are using the company id that's which is the only way to access the leads

urlpatterns = [
    path("", LeadContactCreateListAPIView.as_view(), name="lead_list_create"),
    path("<str:id>/", LeadContactRetrieveUpdateDestroyAPIView.as_view(), name="lead_ret_updt_delete"),

    path("stats/<str:id>/", LeadStatsRetrieveAPIView.as_view(), name="lead_stats"),
    path("lead/upload/", LeadUploadAPIView.as_view(), name="lead_stats"),

]
