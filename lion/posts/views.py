# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods
from .models import *
import json

### DRF 관련 import - APIView 사용
from .serializers import PostSerializer
from .serializers import CommentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

class PostList(APIView):
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostDetail(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid(): # update이니까 유효성 검사 필요
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response(
	        {
	            "message": "게시글이 성공적으로 삭제되었습니다.",
	            "post_id": post_id
	        },
	        status=status.HTTP_200_OK
	    )

class CommentList(APIView):
    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id = post_id)
        serializer = CommentSerializer(comments, many = True)
        return Response(serializer.data)
    
    def post(self, request, post_id, format = None):
        post_instance = get_object_or_404(Post, pk = post_id)
        serializer = CommentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(post_id = post_instance)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class CommentDetail(APIView):
    def delete(self, request, post_id, comment_id):
        comment = Comment.objects.get(post_id = post_id, comment_id = comment_id)
        comment.delete()
        return Response(
            {
                "message": "댓글이 성공적으로 삭제되었습니다.",
                "deleted_id": comment_id,
                "post_id": post_id
            },
            status = status.HTTP_200_OK
        )
        
class PostListByCategory(APIView):
    def get(self, request, category_id):
        category = get_object_or_404(Category, pk = category_id)
        post_list = category.posts.all().order_by('-created_at')
        serializer = PostSerializer(post_list, many = True)
        return Response(serializer.data)