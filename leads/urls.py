from django.urls import path

from .views import LeadContactRetrieveUpdateDestroyAPIView, LeadContactCreateListAPIView

#  if you realized we are using the company id that's which is the only way to access the leads
urlpatterns = [
    path("<str:company_id>/", LeadContactCreateListAPIView.as_view(), name="lead_list_create"),
    path("<str:company_id>/<str:id>/", LeadContactRetrieveUpdateDestroyAPIView.as_view(),
         name="lead_ret_updt_delete"),

]
