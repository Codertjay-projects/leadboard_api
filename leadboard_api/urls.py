"""leaderboard_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import to include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from users.views import LeaderboardRegisterAPIView, LeaderboardLoginAPIView, VerifyEmailOTPAPIView, \
    RequestEmailOTPAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/companies/", include("companies.urls"))
]

# The authentication urls which contains login, register, request otp and verify account
auth_urlpatterns = [
    path("api/v1/auth/login/", LeaderboardLoginAPIView.as_view(), name="Leaderboard_login"),
    path("api/v1/auth/registration/", LeaderboardRegisterAPIView.as_view(), name="Leaderboard_register"),
    #  requesting otp via email
    path("api/v1/auth/request_email_otp/", RequestEmailOTPAPIView.as_view(), name="Leaderboard_request_otp"),
    #  verify account with the otp passed on posted data
    path("api/v1/auth/verify_account/", VerifyEmailOTPAPIView.as_view(), name="Leaderboard_verify_account"),
]

urlpatterns += auth_urlpatterns
