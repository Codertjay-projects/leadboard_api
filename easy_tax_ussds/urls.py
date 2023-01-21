from django.urls import path

from .views import EasyTaxUSSDAPIView

urlpatterns = [
    path("", EasyTaxUSSDAPIView.as_view(), name="easy_task"),
]
