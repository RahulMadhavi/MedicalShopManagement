from django.urls import path

from .views import LoginView, LogoutView, SignUpView, VerifyEmailView

app_name = "accounts"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify-email/<str:uidb64>/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
