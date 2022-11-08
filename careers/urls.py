from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import JobListCreateAPIView, JobRetrieveUpdateDestroyAPIView, JobScheduleViewSetsAPIView, JobApplyAPIView

router = DefaultRouter()
router.register(r'job_schedules', JobScheduleViewSetsAPIView)
urlpatterns = [
    path("", JobListCreateAPIView.as_view(), name="job_list_create"),
    path("job/<str:id>/", JobRetrieveUpdateDestroyAPIView.as_view(), name="job_retrieve_update_destroy"),
    path("job_apply/", JobApplyAPIView.as_view(), name="job_apply"),
]

urlpatterns += router.urls
