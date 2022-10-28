from rest_framework.routers import DefaultRouter
from .views import LeadboardStorageViewSetsAPIView

router = DefaultRouter()
#  the company_id is passed in the params
router.register(r'', LeadboardStorageViewSetsAPIView, basename='storages')
urlpatterns = router.urls
