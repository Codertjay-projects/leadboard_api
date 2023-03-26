from django.urls import path

from .views import UserScheduleCallListCreateAPIView, UserScheduleCallRetrieveUpdateDestroyAPIView, \
    ScheduleCallDetailView, ScheduleCallListCreateAPIView

urlpatterns = [
    path("schedule_call/list_create/", ScheduleCallListCreateAPIView.as_view(), name="schedule_call_list_create"),
    path("schedule_call/<company>/<slug>/", ScheduleCallDetailView.as_view(), name="schedule_call_details"),
    path("", UserScheduleCallListCreateAPIView.as_view(), name="user_schedule_call_list_create"),
    path("<str:id>/", UserScheduleCallRetrieveUpdateDestroyAPIView.as_view(),
         name="user_schedule_call_ret_updt_delete"),

]
