from django.contrib import admin
from django.urls import path, include
from posts.views import *

urlpatterns = [
    path('', PostList.as_view()), # post 전체 조회
    path('<int:post_id>/', PostDetail.as_view()), # post 개별 조회
    
    path('<int:post_id>/comment/', CommentList.as_view()), # Post의 Comment 전체 조회
    path('<int:post_id>/comment/<int:comment_id>/', CommentDetail.as_view()), # comment 개별 삭제
    path('category/<int:category_id>/', PostListByCategory.as_view()) # Category 별 Post 전체 조회
]