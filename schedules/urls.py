from django.urls import path

from .views import UserScheduleCallListCreateAPIView, UserScheduleCallRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", UserScheduleCallListCreateAPIView.as_view(), name="user_schedule_call_list_create"),
    path("<str:id>/", UserScheduleCallRetrieveUpdateDestroyAPIView.as_view(),
         name="user_schedule_call_ret_updt_delete"),

]
