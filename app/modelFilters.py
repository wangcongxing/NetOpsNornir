from django_filters import rest_framework as filters
import django_filters
from app import models


class readTaskListFilter(filters.FilterSet):
    # 模糊过滤
    eoaNumber = django_filters.CharFilter(field_name="eoaNumber", lookup_expr='icontains')
    taskName = django_filters.CharFilter(field_name="taskName", lookup_expr='icontains')
    taskStatus = django_filters.CharFilter(field_name="taskStatus", lookup_expr='icontains')
    desc = django_filters.CharFilter(field_name="desc", lookup_expr='icontains')

    class Meta:
        model = models.readTaskList
        fields = ['eoaNumber', 'taskName', 'taskStatus', "desc"]


class deviceTypesFilter(filters.FilterSet):
    # 模糊过滤
    id = django_filters.CharFilter(field_name="id", )
    deviceState = django_filters.CharFilter(field_name="deviceState", )
    deviceValue = django_filters.CharFilter(field_name="deviceValue", lookup_expr='icontains')

    class Meta:
        model = models.deviceTypes
        fields = ['id', 'deviceValue', 'deviceState']


class cmdConfigFilter(filters.FilterSet):
    # 模糊过滤
    deviceType = django_filters.CharFilter(field_name="deviceType", )
    cmds = django_filters.CharFilter(field_name="cmds", lookup_expr='icontains')
    desc = django_filters.CharFilter(field_name="desc", lookup_expr='icontains')

    class Meta:
        model = models.cmdConfig
        fields = ["deviceType", 'cmds', "desc"]


class netmaintainFilter(filters.FilterSet):
    # 模糊过滤
    deviceType = django_filters.CharFilter(field_name="deviceType", )
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    username = django_filters.CharFilter(field_name="username", lookup_expr='icontains')
    desc = django_filters.CharFilter(field_name="desc", lookup_expr='icontains')

    class Meta:
        model = models.netmaintain
        fields = ["deviceType", 'name', "username", "desc"]


class nettempFilter(filters.FilterSet):
    # 模糊过滤
    deviceType = django_filters.CharFilter(field_name="deviceType", )
    title = django_filters.CharFilter(field_name="title", lookup_expr='icontains')
    desc = django_filters.CharFilter(field_name="desc", lookup_expr='icontains')

    class Meta:
        model = models.nettemp
        fields = ["deviceType", 'title', "desc", ]


class netmaintainIpListFilter(filters.FilterSet):
    # 模糊过滤
    netmaintain = django_filters.CharFilter(field_name="netmaintain", )
    ip = django_filters.CharFilter(field_name="ip", lookup_expr='icontains')

    class Meta:
        model = models.netmaintainIpList
        fields = ["netmaintain", 'ip', ]