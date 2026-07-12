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

import uuid
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from config.permissions import AllowTimePermission, IsOwnerOrReadOnly

from config.custom_exceptions import PostNotFoundException # 추가 - 커스텀 예외처리 실습용
from config.custom_api_exceptions import PostConflictException
from django.utils import timezone


class PostList(APIView):
    permission_classes = [AllowTimePermission, IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_summary="게시글 생성",
        operation_description="새로운 게시글을 생성합니다.",
        request_body=PostSerializer,
        responses={201: PostSerializer, 400: "잘못된 요청"}
    )
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            writer_id = request.data.get('writer')
            
            import datetime
            today = datetime.date.today()
            
            if writer_id:
                already_exists = Post.objects.filter(
                    writer_id=writer_id,
                    created_at__date=today
                ).exists()
                
                if already_exists:
                    raise PostConflictException(detail="게시글은 하루에 하나만 올릴 수 있습니다. 내일 다시 시도해주세요.")
            serializer.save(writer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
        operation_summary="게시글 목록 조회",
        operation_description="모든 게시글을 조회합니다.",
        responses={200: PostSerializer(many=True)}
    )
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

# @require_http_methods(["GET"])
# def get_post_detail(reqeust, id):
#     try:
#         post = Post.objects.get(id=id)
#         post_detail_json = {
#             "id" : post.id,
#             "title" : post.title,
#             "content" : post.content,
#             "status" : post.status,
#             "user" : post.user.username
#         }
#         return JsonResponse({
#             "status" : 200,
#             "data": post_detail_json})
#     except Post.DoesNotExist:
#         raise PostNotFoundException
    
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
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            image_file = request.FILES.get('image')
            image_url = None
            
            if image_file:
                try:
                    image_url = upload_image_to_s3(image_file)
                except Exception as e:
                    return Response({"error": f"S3 업로드 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if image_url:
                serializer.save(image_url=image_url)
            else:
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

        try:
            image_url = upload_image_to_s3(image_file)
        except Exception as e:
            return Response({"error": f"S3 Upload Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # DB에 저장
        image_instance = Image.objects.create(image_url=image_url)
        serializer = ImageSerializer(image_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
def upload_image_to_s3(image_file):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    _, ext = os.path.splitext(image_file.name)
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = f"uploads/{unique_filename}"
   
    content_type, _ = mimetypes.guess_type(unique_filename)
    if not content_type:
        content_type = image_file.content_type

    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_path,
        Body=image_file.read(),
        ContentType=content_type,  
    )

    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"