from rest_framework import serializers
from .models import *

# 회원가입용 시리얼라이저
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User

        # 필요한 필드값 지정, 회원가입은 email까지 필요하므로 email도 추가
        fields = ['username', 'email', 'password']
        
    # create() 함수를 재정의(오버라이딩)
    def create(self, validated_data):

        # 비밀번호 분리
        password = validated_data.pop('password')

        # user 객체 생성
        user = User(**validated_data)

        # 비밀번호는 해싱해서 저장
        user.set_password(password)
        user.save()

        return user
    
    # email 유효성 검사 함수
    def validate_email(self,input):

        # 이메일 형식이 맞는지 검사
        if not "@" in input:
            raise serializers.ValidationError("Invalid email format")
        
        # 이메일 중복 여부 검사
        if User.objects.filter(email=input).exists():
            raise serializers.ValidationError("Email already exists.")
        
        return input
    
# 로그인용 시리얼라이저
class AuthSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
    class Meta:
        model = User

        # 로그인은 username과 password만 필요
        fields = ['username', 'password']
        
    # 로그인 유효성 검사 함수
    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
		    
		# username으로 사용자 찾는 모델 함수
        user = User.get_user_by_username(username=username)
        
        # 존재하는 회원인지 확인
        if user is None:
            raise serializers.ValidationError("User does not exist.")
        else:
			# 비밀번호 일치 여부 확인
            if not user.check_password(password):
                raise serializers.ValidationError("Wrong password.")
        
        # 딕셔너리로 변환
        data['user'] = user

        return data