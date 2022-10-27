from django.urls import path

from .views import LeadBoardRetrieveUpdateDestroyAPIView,LeadContactCreateListAPIView

urlpatterns = [
    path("", LeadBoardRetrieveUpdateDestroyAPIView.as_view(), name="company_list_create"),
    path("<str:id>/", LeadBoardRetrieveUpdateDestroyAPIView.as_view(), name="company_ret_updt_delete"),
]
