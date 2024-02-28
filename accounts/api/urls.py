from django.urls import path

from accounts.api.views import register_user, verify_user_email, resend_email_verification, UserLogin, \
    PasswordResetView, confirm_otp_password_view, resend_password_otp, new_password_reset_view

app_name = 'accounts'

urlpatterns = [
    path('register-user/', register_user, name="register_user"),
    path('verify-user-email/', verify_user_email, name="verify_user_email"),
    path('resend-email-verification/', resend_email_verification, name="resend_email_verification"),
    path('login-user/', UserLogin.as_view(), name="login_user"),

    path('forgot-user-password/', PasswordResetView.as_view(), name="forgot_password"),
    path('confirm-password-otp/', confirm_otp_password_view, name="confirm_otp_password"),
    path('resend-password-otp/', resend_password_otp, name="resend_password_otp"),
    path('new-password-reset/', new_password_reset_view, name="new_password_reset_view"),

]
