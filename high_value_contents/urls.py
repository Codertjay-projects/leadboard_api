from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import HighValueContentViewSetsAPIView, DownloadHighValueContentListCreateAPIView

router = DefaultRouter()
#  the company_id is passed in the params
router.register(r'content', HighValueContentViewSetsAPIView, basename='high_value_contents')

urlpatterns = [
    path('download_content',
         DownloadHighValueContentListCreateAPIView.as_view(),
         name='download_content')
]
urlpatterns += router.urls
