# https://pypi.org/project/drf-renderer-xlsx/
# 为了避免流传输的文件没有文件名(浏览器通常将其默认为没有扩展名的 download)
# 需要使用 mixin 覆盖 Content-Disposition标头
# 如果未提供文件名则默认为 data.xlsx。
from app import models, modelSerializers
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet
import os, uuid, time


# 导出任务信息
class cmdConfigExport(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = models.cmdConfig.objects.all().order_by('-id')
    serializer_class = modelSerializers.cmdConfigSerializerExport
    renderer_classes = (XLSXRenderer,)
    filename = '{}.xlsx'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    column_header = {
        'titles': [
            "ID",
            "设备类型",
            "名称",
            "指令",
            "TextFSM模版",
            "备注",
            "创建时间",
            "修改时间",
            "创建者",
            "修改者",
        ],
        'column_width': [5, 30, 30, 40, 40, 40, 50, 50, 50, ],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }


# 导出设备类型
class deviceTypesExport(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = models.deviceTypes.objects.all().order_by('-id')
    serializer_class = modelSerializers.deviceTypesSerializer
    renderer_classes = (XLSXRenderer,)
    filename = '{}.xlsx'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    column_header = {
        'titles': [
            "ID",
            "设备类型",
            "设备类型显示",
            "创建时间",
            "修改时间",
            "创建者",
            "修改者",
        ],
        'column_width': [5, 30, 30, 40, 40, 40, 50, ],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }


# 导出日常维护任务
class netmaintainExport(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = models.netmaintain.objects.all().order_by('-id')
    serializer_class = modelSerializers.netmaintainExportSerializer
    renderer_classes = (XLSXRenderer,)
    filename = '{}.xlsx'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    column_header = {
        'titles': [
            "ID",
            "事务名称",
            '场景模版',
            '设备类型',
            '登录用户',
            '端口',
            '邮箱',
            '开始时间',
            '指令',
            '备注',
            '状态',
            "创建时间",
            "修改时间",
            "创建者",
            "修改者",
        ],
        'column_width': [5, 30, 30, 40, 40, 40, 50, 50, 50, 50, 50, 50, 50, 50, 50],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }


# 导出日常维护任务
class netmaintainIpListExport(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = models.netmaintainIpList.objects.all().order_by('createTime')
    serializer_class = modelSerializers.netmaintainIpListSerializer
    renderer_classes = (XLSXRenderer,)
    filename = '{}.xlsx'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    column_header = {
        'titles': [
            "ID",
            "IP",
            '指令',
            '运行结果',
            '运行指令',
            '异常信息',
            "创建时间",
            "修改时间",
            "创建者",
            "修改者",
        ],
        'column_width': [5, 30, 30, 40, 40, 40, 50, 50, 50, 50, 50, 50, 50, 50, 50],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }
