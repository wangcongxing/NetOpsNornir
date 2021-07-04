from rest_framework.routers import DefaultRouter
from django.urls import path, include

from app import views, modeExport

router = DefaultRouter()  # 可以处理视图的路由器
router.register(r'deviceTypes', views.deviceTypesViewSet)  # 任务详情
router.register(r'deviceTypesExport', modeExport.deviceTypesExport)  # 设备类型导出

router.register(r'textFsmTemplates', views.textFsmTemplatesViewSet)  # 任务详情
router.register(r'textFsmTemplatesExport', modeExport.textFsmTemplatesExport)  # 任务详情

router.register(r'taskList', views.taskListViewSet)  # 任务管理
router.register(r'taskListDetails', views.taskListDetailsViewSet)  # 任务详情

urlpatterns = [
    # 默认数据初始化
    path('opsBaseInit', views.opsBaseInitDB.as_view()),

]

urlpatterns += router.urls
