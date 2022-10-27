from rest_framework.routers import DefaultRouter

from feedbacks.views import LeadContactFeedbackViewSetsAPIView

router = DefaultRouter()
#  I am using lead_contact_id to filter the object_id in the feedback
router.register('leads/<str:lead_contact_id>', LeadContactFeedbackViewSetsAPIView,
                basename='lead_contact_feedback')
urlpatterns = router.urls
