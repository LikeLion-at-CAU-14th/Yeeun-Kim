from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True) # 객체 생성 시간 저장
    updated_at = models.DateTimeField(auto_now=True) #  객체 저장 날짜와 시간 갱신
    
    class Meta:
        abstract = True

class Post(BaseModel):
    id = models.AutoField(primary_key=True) 
    title = models.CharField(max_length=100)
    content = models.TextField()
    password = models.CharField(max_length=20)
    writer = models.CharField(max_length=10)

    def __str__(self):
        return self.title