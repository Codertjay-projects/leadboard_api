from rest_framework.routers import DefaultRouter

from .views import CompanySubscriberViewSetsAPIView

router = DefaultRouter()
#  I am using company_id to filter
router.register(r'', CompanySubscriberViewSetsAPIView,
                basename='newsletters')
urlpatterns = router.urls
