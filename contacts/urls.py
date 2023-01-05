from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ContactUsViewSetsAPIView, AddToLeadBoardAPIView, NewsletterListCreateAPIView, \
    NewsletterDeleteAPIView, UnSubscribeAPIView

router = DefaultRouter()
#  I am using company_id to filter
router.register(r'contactus', ContactUsViewSetsAPIView,
                basename='contactus')
urlpatterns = [
    # made it this way because of the string url which exist before
    path("add_to_lead_board/", AddToLeadBoardAPIView.as_view(), name="add_to_leadboard"),
    path("unsubscribe/", UnSubscribeAPIView.as_view(), name="unsubscribe"),
    path("newsletter/", NewsletterListCreateAPIView.as_view(), name="newsletter"),
    path("newsletter/<str:id>/", NewsletterDeleteAPIView.as_view(), name="newsletter_delete"),
]
urlpatterns += router.urls
