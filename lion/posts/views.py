from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods
from .models import *
import json
from django.core.files.storage import default_storage  
from .serializers import ImageSerializer
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
import mimetypes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
### DRF 관련 import - APIView 사용
from .serializers import *

import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from config.permissions import AllowTimePermission, IsOwnerOrReadOnly

class PostList(APIView):
    permission_classes = [AllowTimePermission, IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_summary="게시글 생성",
        operation_description="새로운 게시글을 생성합니다.",
        # Swagger에서 form-data 형식을 테스트 할 수 있도록 함
        consumes=["multipart/form-data"],
        manual_parameters=[
            openapi.Parameter(
                'title', 
                openapi.IN_FORM, 
                description="게시글 제목", 
                type=openapi.TYPE_STRING, 
                required=True 
            ),
            openapi.Parameter(
                'content', 
                openapi.IN_FORM, 
                description="게시글 내용", 
                type=openapi.TYPE_STRING, 
                required=True  
            ),
            openapi.Parameter(
                'image',                  
                openapi.IN_FORM, 
                description="업로드할 이미지 파일", 
                type=openapi.TYPE_FILE,   
                required=False
            ),
        ],
        responses={201: PostSerializer, 400: "잘못된 요청"}
    )
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="게시글 목록 조회",
        operation_description="모든 게시글을 조회합니다.",
        responses={200: PostSerializer(many=True)}
    )
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostDetail(APIView):
    permission_classes = [AllowTimePermission, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_summary="게시글 상세 조회",
        operation_description="게시글을 조회합니다.",
        responses={200: PostSerializer, 400: "잘못된 요청"},
    )
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="게시글 수정",
        operation_description="게시글을 수정합니다.",
        # Swagger에서 form-data 형식을 테스트 할 수 있도록 함
        consumes=["multipart/form-data"],
        manual_parameters=[
            openapi.Parameter(
                'title', 
                openapi.IN_FORM, 
                description="게시글 제목", 
                type=openapi.TYPE_STRING, 
                required=False
            ),
            openapi.Parameter(
                'content', 
                openapi.IN_FORM, 
                description="게시글 내용", 
                type=openapi.TYPE_STRING, 
                required=False
            ),
            openapi.Parameter(
                'image',                   # Post 모델에 정의된 이미지 필드명으로 매칭
                openapi.IN_FORM, 
                description="업로드할 이미지 파일", 
                type=openapi.TYPE_FILE, 
                required=False
            ),
        ],
        responses={200: PostSerializer, 400: "잘못된 요청", 403: "권한 없음", 404: "게시글 찾을 수 없음"}
    )
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid(): # update이니까 유효성 검사 필요
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="게시글 삭제",
        operation_description="게시글을 삭제합니다.",
        responses={200: PostSerializer, 403: "권한 없음", 404: "게시글 찾을 수 없음"}
    )
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(request, post)
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
            serializer.save(post = post_instance)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class CommentDetail(APIView):
    def delete(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, post = post_id, comment = comment_id)
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
    
class ImageUploadView(APIView):
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image file"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        # S3에 파일 저장
        filename, ext = os.path.splitext(image_file.name)
        
        count = 0
        while True:
            if count == 0:
                current_filename = f"{filename}{ext}"
            else:
                current_filename = f"{filename}_{count}{ext}"
            
            file_path = f"uploads/{current_filename}"
            
            try:
                s3_client.head_object(Bucket = settings.AWS_STORAGE_BUCKET_NAME, Key = file_path)
                count +=1
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    break
                else:
                    return Response({"error": f"S3 Check Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
        # 2. S3에 파일 업로드하기 전 파일 종류 알아내기
        content_type, _ = mimetypes.guess_type(current_filename)
        
        # 만약 확장자 추정이 실패하면, 유저가 보낸 원래 파일의 기본 타입을 안전장치로 사용
        if not content_type:
            content_type = image_file.content_type

        # S3에 파일 업로드
        try:
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_path,
                Body=image_file.read(),
                ContentType=content_type,  
            )
        except Exception as e:
            return Response({"error": f"S3 Upload Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 업로드된 파일의 URL 생성
        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
        
        # DB에 저장
        image_instance = Image.objects.create(image_url=image_url)
        serializer = ImageSerializer(image_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
