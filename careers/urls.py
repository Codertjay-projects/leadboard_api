from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import JobListCreateAPIView, JobRetrieveUpdateDestroyAPIView, JobApplyAPIView, \
    JobApplicantListAPIView, JobAcceptAPIView

router = DefaultRouter()

urlpatterns = [
    path("", JobListCreateAPIView.as_view(), name="job_list_create"),
    path("job/<str:id>/", JobRetrieveUpdateDestroyAPIView.as_view(), name="job_retrieve_update_destroy"),
    path("job_apply/", JobApplyAPIView.as_view(), name="job_apply"),
    path("job_applicants/",JobApplicantListAPIView.as_view(), name="job_applicants_list"),
    path("job_accept/",JobAcceptAPIView.as_view(), name="job_accept")
]

urlpatterns += router.urls
