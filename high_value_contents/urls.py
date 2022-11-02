from rest_framework.routers import DefaultRouter
from .views import HighValueContentViewSetsAPIView

router = DefaultRouter()
#  the company_id is passed in the params
router.register(r'', HighValueContentViewSetsAPIView, basename='high_value_contents')
urlpatterns = router.urls
