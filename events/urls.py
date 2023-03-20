from django.urls import path

from .views import EvenListAPIView, EventCreateAPIView, EventRetrieveUpdateDestroyAPIView, EventRegisterAPIView

urlpatterns = [
    path("", EvenListAPIView.as_view(), name="event_list"),
    path("create/", EventCreateAPIView.as_view(), name="event_create"),
    path("details/<str:slug>/", EventRetrieveUpdateDestroyAPIView.as_view(), name="event_update_delete_retrieve"),
    path("register/", EventRegisterAPIView.as_view(), name="event_register"),

]
