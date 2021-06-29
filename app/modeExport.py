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
class textFsmTemplatesExport(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = models.textFsmTemplates.objects.all().order_by('-id')
    serializer_class = modelSerializers.textFsmTemplatesSerializerExport
    renderer_classes = (XLSXRenderer,)
    filename = '{}.xlsx'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    column_header = {
        'titles': [
            "ID",
            "设备类型",
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
