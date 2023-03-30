from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import HighValueContentViewSetsAPIView, DownloadHighValueContentListCreateAPIView, \
    LeadsDownloadedHighValueContentRetrieveAPIView, DownloadHighValueDetailsAPIView, ListSchedulesBasicAPIView

router = DefaultRouter()
#  the company_id is passed in the params
router.register(r'content', HighValueContentViewSetsAPIView, basename='high_value_contents')

urlpatterns = [
    path('content_basic/',
         ListSchedulesBasicAPIView.as_view(),
         name='download_content'),
     path('download_content/',
         DownloadHighValueContentListCreateAPIView.as_view(),
         name='download_content'),
    path('lead_download_content/',
         LeadsDownloadedHighValueContentRetrieveAPIView.as_view()),
    path('details/<uuid:id>/',
         DownloadHighValueDetailsAPIView.as_view(),
         name='details'),
]
urlpatterns += router.urls
