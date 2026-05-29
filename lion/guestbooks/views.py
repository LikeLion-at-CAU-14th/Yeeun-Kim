from django.shortcuts import render
from django.http import JsonResponse 
from django.shortcuts import get_object_or_404 
from django.views.decorators.http import require_http_methods
from .models import *
import json

from .serializers import PostSerializer

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
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostDetail(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        get_password = request.data.get('password')
        if get_password == post.password:
            post.delete()
            return Response(
                {
                    "message": "방명록이 성공적으로 삭제되었습니다.",
	                "post_id": post_id
                },
                status = status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "error": "비밀번호가 일치하지 않습니다.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    