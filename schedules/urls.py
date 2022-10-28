from django.urls import path

from .views import UserScheduleCallListCreateAPIView, UserScheduleCallRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("<str:company_id>/", UserScheduleCallListCreateAPIView.as_view(), name="user_schedule_call_list_create"),
    path("<str:company_id>/<str:id>/", UserScheduleCallRetrieveUpdateDestroyAPIView.as_view(),
         name="user_schedule_call_ret_updt_delete"),

]
