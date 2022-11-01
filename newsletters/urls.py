from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CompanySubscriberViewSetsAPIView, AddToLeadBoardAPIView

router = DefaultRouter()
#  I am using company_id to filter
router.register(r'', CompanySubscriberViewSetsAPIView,
                basename='newsletters')
urlpatterns =[
    # made it this way because of the string url which exist before
    path("add_to_lead_board/all/",AddToLeadBoardAPIView.as_view(),name="add_to_leadboard")
]
urlpatterns += router.urls
