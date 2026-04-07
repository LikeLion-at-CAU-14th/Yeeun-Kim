# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods
from .models import *
import json

# 게시글을 Post(Create), Get(Read) 하는 뷰 로직
@require_http_methods(["POST", "GET"])   #함수 데코레이터, 특정 http method 만 허용합니다
def post_list(request):

    if request.method == "POST":

        # request.body의 byte -> 문자열 -> python 딕셔너리
        body = json.loads(request.body.decode('utf-8'))

        # 프론트에게서 user id를 넘겨받는다고 가정.
				# 외래키 필드의 경우, 객체 자체를 전달해줘야하기 때문에
        # id를 기반으로 user 객체를 조회해서 가져옵니다 !
        user_id = body.get('user')
        user = get_object_or_404(User, pk=user_id)

        # 새로운 데이터를 DB에 생성
        new_post = Post.objects.create(
            title = body['title'],
            content = body['content'],
            status = body['status'],
            writer = user
        )

        # Json 형태 반환 데이터 생성
        new_post_json = {
            "id" : new_post.id,
            "title" : new_post.title,
            "content" : new_post.content,
            "status" : new_post.status,
            "writer" : new_post.writer.username
        }

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 생성 성공',
            'data' : new_post_json
        })
        
    if request.method == "GET":
        post_all = Post.objects.all()

        # 각 데이터를 Json 형식으로 변환하여 리스트에 저장 (여러개의 게시글 내용을 담을 거라 리스트를 이용합니다)
        post_all_json = []

        for post in post_all:
            post_json = {
                "id" : post.id,
                "title" : post.title,
                "content" : post.content,
                "status" : post.status,
                "writer" : post.writer.username
            }
            post_all_json.append(post_json)

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 목록 조회 성공',
            'data' : post_all_json
        })

@require_http_methods(["GET"])        
def comment_list(request, post_id):
    
    if request.method == "GET":
        comment_all = Comment.objects.filter(post_id = post_id)
        
        comment_all_json = []
        
        for comment in comment_all:
            comment_json = {
                "comment_id" : comment.comment_id,
                "content" : comment.content,
                "post_id" : comment.post_id.id,
                "user_id" : comment.user_id.username
            }
            comment_all_json.append(comment_json)
            
        return JsonResponse({
            'status' : 200,
            'message' : f'{post_id}번 게시글의 댓글 목록 조회 성공',
            'data' : comment_all_json
        })

@require_http_methods(["GET"]) 
def post_list_by_category(request, category_id):
    category = get_object_or_404(Category, pk = category_id)
    
    if request.method == "GET":
        post_list = category.posts.all().order_by('-created_at')
        
        post_list_json = []
        
        for post in post_list:
            post_json = {
                "post_id" : post.id,
                "title" : post.title,
                "content" : post.content,
                "status" : post.status,
                "writer" : post.writer.username
            }
            post_list_json.append(post_json)
            
        return JsonResponse({
            'status' : 200,
            'message' : f'{category.name}의 게시글 조회 성공',
            'data' : post_list_json
        })
            

# Create your views here.

def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : "Hello likelion-14th!"
        })
        
def index(request):
    return render(request, 'index.html')

# 게시글 단일조회(GET), 수정(PATCH), 삭제(DELETE) 로직
@require_http_methods(["GET", "PATCH", "DELETE"])
def post_detail(request, post_id):
    
    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id) # post_id 에 해당하는 Post 데이터 가져오기
    
        post_detail_json = {
            "id" : post.id,
            "title" : post.title,
            "content" : post.content,
            "status" : post.status,
            "writer" : post.writer.username
        }
        return JsonResponse({
            "status" : 200,
            'message' : '게시글 단일 조회 성공',
            "data": post_detail_json})
        
    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))

        post_update = get_object_or_404(Post, pk=post_id)

        if 'title' in body:
            post_update.title = body['title']
        if 'content' in body:
            post_update.content = body['content']
        if 'status' in body:
            post_update.status = body['status']
        
        post_update.save()

        post_update_json = {
            "id" : post_update.id,
            "title" : post_update.title,
            "content" : post_update.content,
            "status" : post_update.status,
            "writer" : post_update.writer.username
        }

        return JsonResponse({
            'status': 200,
            'message' : '게시글 수정 성공',
            'data' : post_update_json
        })
    
    if request.method == "DELETE":
        post_delete = get_object_or_404(Post, pk=post_id)
        post_delete.delete()

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 삭제 성공',
            'data' : None
        })