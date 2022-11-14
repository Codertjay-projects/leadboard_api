from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CompanyRetrieveUpdateDeleteAPIView, CompanyListCreateAPIView, CompanyAddUserAPIView, \
    CompanyGroupRetrieveUpdateDestroy, CompanyGroupListCreate, LocationViewSetsAPIView, IndustryViewSetsAPIView, \
    CompanyInviteListCreateAPIView

urlpatterns = [
    path("", CompanyListCreateAPIView.as_view(), name="company_list_create"),
    path("company/<str:id>/", CompanyRetrieveUpdateDeleteAPIView.as_view(), name="company_ret_updt_delete"),
    path("company_action/<str:id>/", CompanyAddUserAPIView.as_view(), name="company_add_user"),
    # groups route
    path("groups/<str:id>/", CompanyGroupListCreate.as_view(), name="company_group_list_create"),
    path("groups/<str:company_id>/<str:group_id>/", CompanyGroupRetrieveUpdateDestroy.as_view(),
         name="company_group_create_retrieve_destroy"),
    path("company_invites/", CompanyInviteListCreateAPIView.as_view(), name="company_invites")
]

router = DefaultRouter()
router.register(r'locations', LocationViewSetsAPIView, basename='locations')
router.register(r'industries', IndustryViewSetsAPIView, basename='industries')
urlpatterns += router.urls
