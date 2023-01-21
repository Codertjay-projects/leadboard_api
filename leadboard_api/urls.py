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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users.views import LeaderboardRegisterAPIView, LeaderboardLoginAPIView, VerifyEmailOTPAPIView, \
    RequestEmailOTPAPIView, ForgotPasswordWithOTPAPIView, ChangePasswordAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/companies/", include("companies.urls")),
    path("api/v1/leads/", include("leads.urls")),
    path("api/v1/schedules/", include("schedules.urls")),
    path("api/v1/feedbacks/", include("feedbacks.urls")),
    path("api/v1/high_value_contents/", include("high_value_contents.urls")),
    path("api/v1/events/", include("events.urls")),
    path("api/v1/contacts/", include("contacts.urls")),
    path("api/v1/careers/", include("careers.urls")),
    path("api/v1/communications/", include("communications.urls")),
    path('api/v1/easy_tax_ussds/', include('easy_tax_ussds.urls')),
]

# The authentication urls which contains login, register, request otp and verify account
auth_urlpatterns = [
    path("api/v1/auth/login/", LeaderboardLoginAPIView.as_view(), name="Leaderboard_login"),
    path("api/v1/auth/registration/", LeaderboardRegisterAPIView.as_view(), name="Leaderboard_register"),
    #  requesting otp via email
    path("api/v1/auth/request_email_otp/", RequestEmailOTPAPIView.as_view(), name="Leaderboard_request_otp"),
    #  verify account with the otp passed on posted data
    path("api/v1/auth/verify_account/", VerifyEmailOTPAPIView.as_view(), name="Leaderboard_verify_account"),
    path('api/v1/auth/forgot_password/', ForgotPasswordWithOTPAPIView.as_view(), name='forgot_password'),
    path('api/v1/auth/change_password/', ChangePasswordAPIView.as_view(), name='change_password'),
]

urlpatterns += auth_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
