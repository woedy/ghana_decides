from django.urls import path

from accounts.api.views import register_user, verify_user_email, resend_email_verification, UserLogin, \
    PasswordResetView, confirm_otp_password_view, resend_password_otp, new_password_reset_view, get_all_users, \
    get_user_detail, edit_user_view, delete_user_view, register_data_admin, DataAdminLogin, check_email_exist_view, \
    register_correspondent, register_presenter, PresenterLogin

app_name = 'accounts'

urlpatterns = [
    path('register-user/', register_user, name="register_user"),
    path('register-data-admin/', register_data_admin, name="register_data_admin"),
    path('register-presenter/', register_presenter, name="register_presenter"),
    path('register-correspondent/', register_correspondent, name="register_correspondent"),
    path('check-email-exists/', check_email_exist_view, name="check_email_exist_view"),

    path('verify-user-email/', verify_user_email, name="verify_user_email"),
    path('resend-email-verification/', resend_email_verification, name="resend_email_verification"),
    path('login-user/', UserLogin.as_view(), name="login_user"),
    path('login-data-admin/', DataAdminLogin.as_view(), name="login_data_admin"),
    path('login-presenter/', PresenterLogin.as_view(), name="login_presenter"),

    path('forgot-user-password/', PasswordResetView.as_view(), name="forgot_password"),
    path('confirm-password-otp/', confirm_otp_password_view, name="confirm_otp_password"),
    path('resend-password-otp/', resend_password_otp, name="resend_password_otp"),
    path('new-password-reset/', new_password_reset_view, name="new_password_reset_view"),



    path('get-all-users/', get_all_users, name="get_all_users"),
    path('user-details/', get_user_detail, name="get_user_detail"),
    path('edit-user/', edit_user_view, name="edit_user_view"),
    path('delete-user/', delete_user_view, name="delete_user_view"),

]
