from app import models
from rest_framework.permissions import BasePermission

class taskListPermission(BasePermission):
    def has_permission(self, request, view):
        """让所有用户都有权限"""
        print("has_permission=",request.user)
        return True

    def has_object_permission(self, request, view, obj):
        """用户是否有权限访问添加了权限控制类的数据对象"""
        # 需求：用户能够访问id为1，3的对象，其他的不能够访问
        '''
        if obj.id in (1, 3):
            return True
        else:
            return False
        '''
        return True

class deviceTypesPermission(BasePermission):
    def has_permission(self, request, view):
        """让所有用户都有权限"""
        print("has_permission=",request.user)
        return True

    def has_object_permission(self, request, view, obj):
        """用户是否有权限访问添加了权限控制类的数据对象"""
        # 需求：用户能够访问id为1，3的对象，其他的不能够访问
        '''
        if obj.id in (1, 3):
            return True
        else:
            return False
        '''
        return True


class textFsmTemplatesPermission(BasePermission):
    def has_permission(self, request, view):
        """让所有用户都有权限"""
        print("has_permission=",request.user)
        return True

    def has_object_permission(self, request, view, obj):
        """用户是否有权限访问添加了权限控制类的数据对象"""
        # 需求：用户能够访问id为1，3的对象，其他的不能够访问
        '''
        if obj.id in (1, 3):
            return True
        else:
            return False
        '''
        return True