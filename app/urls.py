from rest_framework.routers import DefaultRouter
from django.urls import path, include
from app import views, modeExport
router = DefaultRouter()  # 可以处理视图的路由器
router.register(r'deviceTypes', views.deviceTypesViewSet)  # 任务详情
router.register(r'deviceTypesExport', modeExport.deviceTypesExport)  # 设备类型导出
router.register(r'textFsmTemplates', views.cmdConfigViewSet)  # 指令配置
router.register(r'textFsmTemplatesExport', modeExport.cmdConfigExport)  # 指令配置
router.register(r'readTaskList', views.readTaskListViewSet)  # 任务管理
router.register(r'taskListDetails', views.taskListDetailsViewSet)  # 任务详情
router.register(r'netmaintain', views.netmaintainViewSet)  # 日常维护
router.register(r'netmaintainIpList', views.netmaintainIpListViewSet)  # 日常维护
router.register(r'netmaintainExport', modeExport.netmaintainExport)  # 日常维护导出
router.register(r'netmaintainIpListExport', modeExport.netmaintainIpListExport)  # 日常维护导出
router.register(r'nettemp', views.nettempViewSet)  # 运维模版
router.register(r'lldpInfo', views.lldpInfoViewSet)  # 网络拓扑
urlpatterns = [
    # 默认数据初始化
    path('opsBaseInit', views.opsBaseInitDB.as_view()),
]

urlpatterns += router.urls
