### Model Serializer case
from rest_framework import serializers
from .models import Post
from .models import Comment
from .models import Image
from config.custom_api_exceptions import PostConflictException
from rest_framework.exceptions import ValidationError

class PostSerializer(serializers.ModelSerializer):
  image = serializers.ImageField(write_only=True, required=False)
  title = serializers.CharField(allow_blank=True, required=False)
  content = serializers.CharField(allow_blank=True, required=False)

  class Meta:
    model = Post    # serializer가 어떤 모델을 기반으로 만들어지는지 >> post
    fields = "__all__"  # 모델에서 어떤 필드를 가져올지 >> 전체 필드
    read_only_fields = ['writer']
    
  def validate(self, data):
        # 💡 data['title'] 대신 data.get('title')을 사용해야 안전합니다!
        title = data.get('title')
        content = data.get('content')
        
        if not title or title.strip() == "":
          raise PostConflictException(detail="제목 필드가 누락되었습니다.")
          
        if not content or content.strip() == "":
          raise PostConflictException(detail="내용 필드가 누락되었습니다.")
        
        if Post.objects.filter(title=title).exists():
            raise PostConflictException(detail=f"A post with title: '{title}' already exists.")
        
        return data

class CommentSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Comment
    fields = "__all__"
    
  def validate(self, data):
    content = data.get('content', '')
    
    if len(content) < 15:
      raise ValidationError(
        f"댓글은 최소 15자 이상 작성해야 합니다."
      )
    
    return data
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        