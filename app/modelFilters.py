from django_filters import rest_framework as filters
import django_filters
from app import models


class taskListFilter(filters.FilterSet):
    # 模糊过滤
    eoaNumber = django_filters.CharFilter(field_name="eoaNumber", lookup_expr='icontains')
    taskName = django_filters.CharFilter(field_name="taskName", lookup_expr='icontains')
    taskStatus = django_filters.CharFilter(field_name="taskStatus", lookup_expr='icontains')

    class Meta:
        model = models.taskList
        fields = ['eoaNumber', 'taskName', 'taskStatus']


class deviceTypesFilter(filters.FilterSet):
    # 模糊过滤
    deviceKey = django_filters.CharFilter(field_name="deviceKey", lookup_expr='icontains')
    deviceValue = django_filters.CharFilter(field_name="deviceValue", lookup_expr='icontains')

    class Meta:
        model = models.deviceTypes
        fields = ['deviceKey', 'deviceValue', ]


class textFsmTemplatesFilter(filters.FilterSet):
    # 模糊过滤
    deviceType = django_filters.CharFilter(field_name="deviceType",)
    cmds = django_filters.CharFilter(field_name="cmds", lookup_expr='icontains')
    desc = django_filters.CharFilter(field_name="desc", lookup_expr='icontains')

    class Meta:
        model = models.textFsmTemplates
        fields = ["deviceType", 'cmds', "desc"]
