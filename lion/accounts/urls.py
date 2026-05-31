from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("join/", RegisterView.as_view()),
    path("login/", AuthView.as_view()),
    path("logout/", LogoutView.as_view()),
    # 토큰 관련 url 추가
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # 구글 소셜로그인
    path("google/login/", google_login, name="google_login"), # 프론트 협업 시 삭제
    path("google/callback/", google_callback, name="google_callback"),
    # 카카오 소셜로그인
    path("kakao/login/", kakao_login, name="kakao_login"), # 프론트 협업 시 삭제
    path("kakao/login/callback/", kakao_callback, name="kakao_callback")
]