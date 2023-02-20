from django.urls import path
from rest_framework.routers import DefaultRouter

from feedbacks.views import LeadContactFeedbackViewSetsAPIView, FeedbackListView, FeedbackCreateView

router = DefaultRouter()
#  I am using lead_contact_id to filter the object_id in the feedback
router.register(r'leads', LeadContactFeedbackViewSetsAPIView,
                basename='lead_contact_feedback')

urlpatterns =[
    path("list/", FeedbackListView.as_view(), name="feedback_list"),
    path("create/<str:c_id>/", FeedbackCreateView.as_view(), name="feedback_create"),
]
urlpatterns += router.urls
