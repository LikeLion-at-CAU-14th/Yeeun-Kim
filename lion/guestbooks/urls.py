from django.contrib import admin
from django.urls import path, include
from guestbooks.views import *

urlpatterns = [
    path('', PostList.as_view()), # 방명록 전체 조회
    path('<int:post_id>/', PostDetail.as_view()), # 방명록 개별 조회
]