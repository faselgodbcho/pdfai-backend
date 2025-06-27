from django.urls import path
from .tokens import CustomTokenObtainPairView, CustomTokenRefreshView
from rest_framework_simplejwt.views import (
    TokenVerifyView
)

from . import views

urlpatterns = [
    path("register/", views.register_user_view, name='user-registration'),
    path("token/", CustomTokenObtainPairView.as_view(),
         name='token-obtain-pair'),
    path("token/refresh/",
         CustomTokenRefreshView.as_view(), name='token-refresh'),
    path("token/verify/", TokenVerifyView.as_view(), name='token-verify'),
    path("logout/", views.logout_user_view, name='user-logout'),
    path("user/", views.user_detail_view, name='user-details'),
]
