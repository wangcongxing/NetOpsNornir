from rest_framework.routers import DefaultRouter
from django.urls import path, include

from app import views

router = DefaultRouter()  # 可以处理视图的路由器


urlpatterns = [
    # 默认数据初始化
    path('opsBaseInit', views.opsBaseInitDB.as_view()),


]

urlpatterns += router.urls
