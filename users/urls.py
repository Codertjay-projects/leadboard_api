from django.urls import path

from users.views import UserProfileUpdateAPIView, UserUpdateAPIView, LeaderboardRegisterAPIView, LeaderboardLoginAPIView, VerifyEmailOTPAPIView, \
    RequestEmailOTPAPIView, ForgotPasswordWithOTPAPIView, ChangePasswordAPIView, LeadboardVerifyTokenAPIView

urlpatterns = [
    path("profile_update/", UserProfileUpdateAPIView.as_view(), name="profile_update"),
    path("user_update/", UserUpdateAPIView.as_view(), name="user_update"),
]

# The authentication urls which contains login, register, request otp and verify account
auth_urlpatterns = [
    path("auth/login/", LeaderboardLoginAPIView.as_view(), name="Leaderboard_login"),
    path("auth/registration/", LeaderboardRegisterAPIView.as_view(), name="Leaderboard_register"),
    #  requesting otp via email
    path("auth/request_email_otp/", RequestEmailOTPAPIView.as_view(), name="Leaderboard_request_otp"),
    #  verify account with the otp passed on posted data
    path("auth/verify_account/", VerifyEmailOTPAPIView.as_view(), name="Leaderboard_verify_account"),
    path('auth/forgot_password/', ForgotPasswordWithOTPAPIView.as_view(), name='forgot_password'),
    path('auth/change_password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('auth/verify_token/', LeadboardVerifyTokenAPIView.as_view(), name='verify_token'),
]

urlpatterns += auth_urlpatterns