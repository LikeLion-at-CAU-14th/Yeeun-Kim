### Model Serializer case
from rest_framework import serializers
from .models import Post
from .models import Comment
from .models import Image

class PostSerializer(serializers.ModelSerializer):
  image = serializers.ImageField(write_only=True, required=False)

  class Meta:
    model = Post    # serializer가 어떤 모델을 기반으로 만들어지는지 >> post
    fields = "__all__"  # 모델에서 어떤 필드를 가져올지 >> 전체 필드
    read_only_fields = ['writer']

class CommentSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Comment
    fields = "__all__"
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        