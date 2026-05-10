from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import datetime 

class IsAuthenticatedUserAndAllowTime(BasePermission):    
    message = "게시판 이용이 제한되는 시간입니다."
    
    def has_permission(self, request, view):
        now = datetime.datetime.now().time()
        
        start_banned = datetime.time(22, 0)
        end_banned = datetime.time(7, 0)
        
        if now >= start_banned or now <= end_banned:
            return False
       
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.writer == request.user