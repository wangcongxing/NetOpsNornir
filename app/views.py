from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets, serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from app import models, modelFilters, modelSerializers, modelPermission
from utils import APIResponseResult
from utils.CustomViewBase import CustomViewBase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework.views import APIView
import os, uuid, time
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from textfsm import TextFSM
from netmiko import ConnectHandler
import json
from datetime import datetime, timedelta
from django.db import transaction
from rest_framework import generics, mixins, views, viewsets
from django_filters import rest_framework as filters
import ast
import site
import shutil
from nornir.core.task import Result
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.task import Result
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command
from utils.cmdb_inventory_v2 import CMDBInventory
import os
from tempfile import TemporaryFile
from io import BytesIO
from urllib.parse import quote
import ast
import django_excel as excel
import xlwt
from django.http import HttpResponse

ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsNornir import pro_settings as config
elif ENV_PROFILE == "test":
    from NetOpsNornir import test_settings as config
else:
    from NetOpsNornir import settings as config

NTC_TEMPLATES_DIR = config.initConfig["NTC_TEMPLATES_DIR"]


# Create your views here.
def getDeviceType():
    jsonResult = []
    try:
        dev_info = {
            "device_type": "none",
            "ip": "10.32.1.3",
            "username": "",
            "password": "",
            "port": 22
        }
        with ConnectHandler(**dev_info) as conn:
            output = conn.send_command("display version")  # display lldp neighbor verbose
            print(output)
    except Exception as e:
        cliText = e.args[0]
        f = open(os.path.join(NTC_TEMPLATES_DIR, "get_device_types.textfsm"))
        template = TextFSM(f)
        jsonResult = template.ParseText(cliText)
    return jsonResult


# 默认数据初始化
class opsBaseInitDB(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        # 新建超级用户
        superUser, ctime = User.objects.update_or_create(
            defaults={'username': 'admin', 'is_staff': True, 'is_active': True, 'is_superuser': True,
                      'first_name': '管理员',
                      'password': make_password("admin@123")}, username='admin')
        superUser = superUser.username
        jsonResult = getDeviceType()
        for item in jsonResult:
            d, c = models.deviceTypes.objects.update_or_create(
                defaults={"deviceKey": item[0], "deviceValue": item[0],
                          'creator': superUser, 'editor': superUser},
                deviceKey=item[0])
        # 从venv ntc_templates复制模版文件到 项目目录 ntc_templates
        textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates"
        if os.path.exists(textfsm_ntc_templates):
            for tfile in os.listdir(textfsm_ntc_templates):
                shutil.copyfile(textfsm_ntc_templates + "/" + tfile, os.path.join(NTC_TEMPLATES_DIR, tfile))
        return HttpResponse("<h1>数据库初始化成功</h1>")


os.environ[
    "NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"
InventoryPluginRegister.register("cmdb_inventory", CMDBInventory)


def show_cmds(task):
    print(task.host, "=====", task.host.name)
    command_textfsm = task.host.data["data"]["command_textfsm"]
    # Task类通过host属性，读取yaml配置，获取其中设备信息
    # 判断文件是否存在
    # 不存在创建/有直接使用

    # 3.如果自己配置的textFSM报错,则使用系统模版use_textfsm=True
    jsonResult = []

    for item in command_textfsm:
        customeTextFsm = item["textfsm"]
        # 系统虚拟环境路径
        textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates/" + task.host.platform + "_" + \
                                item["cmd"].replace(" ",
                                                    "_") + ".textfsm"
        # 自定TextFSM模版路径
        textFsmTemplate = os.path.join(NTC_TEMPLATES_DIR,
                                       '{}_{}.textfsm'.format(task.host.platform, item["cmd"].replace(" ", "_")))
        try:
            # 自定义textFSM不为空，并且自定义文件夹存在textFSM模版

            if customeTextFsm != "" or os.path.exists(textFsmTemplate):
                # 1.如果配置textFSM就用配置的
                if not os.path.exists(textFsmTemplate):
                    f = open(textFsmTemplate, mode='w+', encoding='UTF-8')
                    # open()打开一个文件，返回一个文件对象
                    f.write(item["textfsm"])  # 写入textfsm
                    f.close()
                # print(cmd)
                # Task类调用run方法，执行任务，如netmiko_send_command、write_file等插件use_textfsm=True
                # 为什么不用use_textfsm=True  自定义模版需要频繁改动index文件 风险高
                cliText = task.run(netmiko_send_command, command_string=item["cmd"])
                # output = result.result
                f = open(textFsmTemplate)
                template = TextFSM(f)
                jsonResult = template.ParseText(cliText[0].result)
                models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).update({
                    "oldResult": cliText[0].result,
                    "jsonResult": jsonResult
                })
            elif os.path.exists(textfsm_ntc_templates):
                # 2.如果没有配置textFSM用系统自带的,use_textfsm=True
                results = task.run(netmiko_send_command, command_string=item["cmd"], use_textfsm=True)
                print_result(results)
                models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).update({
                    "jsonResult": results[0].result
                })

            else:
                # 3.使用netmiko_send_command 模块执行
                cliText = task.run(netmiko_send_command, command_string=item["cmd"])
                models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).update({
                    "oldResult": cliText[0].result
                })
        except Exception as e:
            print("show_cmds=", e.args)
    return jsonResult


class taskListViewSet(CustomViewBase):
    queryset = models.taskList.objects.all().order_by('-id')
    serializer_class = modelSerializers.taskListSerializer
    filter_class = modelFilters.taskListFilter
    ordering_fields = ('id',)  # 排序
    permission_classes = [modelPermission.taskListPermission]

    @action(methods=['get'], detail=False, url_path='run')
    def run(self, request, *args, **kwargs):
        device_type_cmds = {}
        # 整合设备类型{"hp_comware":[{"cmd":"","textfsm":""}],"juniper":[{"cmd":"","textfsm":""}]}
        deviceTypes = models.textFsmTemplates.objects.all()
        for ditem in deviceTypes:
            if ditem.deviceType.deviceKey in device_type_cmds.keys():
                device_type_cmds[ditem.deviceType.deviceKey].append(
                    {"cmd": ditem.cmds, "textfsm": ditem.TextFSMTemplate})
            else:
                rlist = []
                rlist.append({"cmd": ditem.cmds, "textfsm": ditem.TextFSMTemplate})
                device_type_cmds.update({ditem.deviceType.deviceKey: rlist})
        print("device_type_cmds=", device_type_cmds)
        taskListResult = models.taskList.objects.filter(taskStatus=0)
        for item in taskListResult:
            taskListDetailsResult = models.taskListDetails.objects.filter(taskList=item)
            devs = []
            for subItem in taskListDetailsResult:
                devs.append(
                    {'ip': subItem.ip, 'username': subItem.username, 'password': subItem.password,
                     'port': subItem.port,
                     'device_type': subItem.deviceType.deviceKey,
                     "data": {"nid": subItem.id,
                              "command_textfsm": device_type_cmds.get(subItem.deviceType.deviceKey)}})
            print("devs=", devs)
            nr = InitNornir(
                runner={
                    "plugin": "threaded",
                    "options": {
                        "num_workers": 100,
                    },
                },
                inventory={
                    "plugin": "cmdb_inventory",
                    "options": {
                        "devices": devs,
                    },
                },
            )
            results = nr.run(task=show_cmds)
            # item.taskStatus = 2
            item.save()
        return APIResponseResult.APIResponse(0, "已启用")

    # 下载执行结果

    @action(methods=['get'], detail=False, url_path='runResult')
    def runResult(self, request, *args, **kwargs):
        nid = request.data.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "参数有无请稍后再试")
        task = models.taskList.objects.get(id=int(nid))
        tasklistdetails = models.taskListDetails.objects.filter(taskList=task)
        downloadResult = {}
        for item in tasklistdetails:
            if item.ip in downloadResult.keys():
                newResult = downloadResult[item.ip]
                newResult.append({"cmds": item.textfsmtemplates.cmds, "jsonResult": item.jsonResult,
                                  "oldResult": item.oldResult})
                downloadResult[item.ip] = newResult
            else:
                downloadResult.update({item.ip: [
                    {"cmds": item.textfsmtemplates.cmds, "jsonResult": item.jsonResult,
                     "oldResult": item.oldResult}]})
        return APIResponseResult.APIResponse(0, 'success', results=downloadResult,
                                             http_status=status.HTTP_200_OK, )

    @action(methods=['get'], detail=False, url_path='downloadResult')
    def downloadResult(self, request, *args, **kwargs):
        nid = request.data.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "参数有无请稍后再试")
        task = models.taskList.objects.get(id=int(nid))
        tasklistdetails = models.taskListDetails.objects.filter(taskList=task)
        sheetNames = tasklistdetails.values("textfsmtemplates__name", "textfsmtemplates_id").distinct()
        print("sheetNames=", sheetNames)
        # 创建工作簿
        wb = xlwt.Workbook()
        # 通过指令新建sheet
        for sheetName in sheetNames:
            wb.add_sheet(sheetName["textfsmtemplates__name"])
        # 通过模版id查询 对应的结果
        for sheetName in sheetNames:
            rows = tasklistdetails.filter(textfsmtemplates_id=sheetName["textfsmtemplates_id"]).values("ip",
                                                                                                       "deviceType__deviceValue",
                                                                                                       "textfsmtemplates__cmds",
                                                                                                       "executeState",
                                                                                                       "oldResult",
                                                                                                       "jsonResult",
                                                                                                       "createTime",
                                                                                                       "lastTime",
                                                                                                       "creator")
            print("rows=", rows)
            listResult = []
            for item in rows:
                jsonResult = item["jsonResult"]
                if jsonResult:
                    rowDict = ast.literal_eval(jsonResult)
                    for listItem in rowDict:
                        cliValueResult = {}
                        cliValueResult.update({"IP": item["ip"], "设备类型": item["deviceType__deviceValue"],
                                               "指令": item["textfsmtemplates__cmds"],
                                               "状态": item["executeState"],
                                               "原始结果": item["oldResult"], "序列化结果": item["jsonResult"],
                                               "创建时间": item["createTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                               "修改时间": item["lastTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                               "创建者": item["creator"]})
                        for k, v in listItem.items():
                            cliValueResult.update({k: v})
                        listResult.append(cliValueResult)
                else:
                    # jsonResult 等于空 或取数发生错误 需要特殊处理
                    cliValueResult = {}
                    cliValueResult.update({"IP": item["ip"], "设备类型": item["deviceType__deviceValue"],
                                           "指令": item["textfsmtemplates__cmds"],
                                           "状态": item["executeState"],
                                           "原始结果": item["oldResult"], "序列化结果": item["jsonResult"],
                                           "创建时间": item["createTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                           "修改时间": item["lastTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                           "创建者": item["creator"]})
            sheet = wb.get_sheet(sheetName["textfsmtemplates__name"])
            # 写入对应的列名
            if listResult:
                firstItem = listResult[0]
                colnames = firstItem.keys()
                # 向Excel表单中写入表头
                for index, name in enumerate(colnames):
                    sheet.write(0, index, name)
            # 写入结果
            i = 1
            for data in listResult:
                for j, k in enumerate(data.keys()):
                    sheet.write(i, j, data[k])
                i = i + 1

        # 保存Excel
        buffer = BytesIO()
        wb.save(buffer)
        # 将二进制数据写入响应的消息体中并设置MIME类型
        resp = HttpResponse(buffer.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # 中文文件名需要处理成百分号编码 文件名需要编码去掉特殊字符
        filename = quote('{}.xls'.format(task.taskName))
        # 通过响应头告知浏览器下载该文件以及对应的文件名
        resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
        return resp

    # 下载excel 实例
    # https://cloud.tencent.com/developer/article/1518588
    @action(methods=['get'], detail=False, url_path='downLoadFile')
    def downLoadFile(self, request, *args, **kwargs):
        sheet = excel.pe.Sheet([[1, 2], [3, 4]])
        return excel.make_response(sheet, "xlsx")

        # TextFSM验证

    @action(methods=['post'], detail=False, url_path='TextFSMCheck')
    def TextFSMCheck(self, request, *args, **kwargs):
        CLIText = request.data.get("CLIText", "")
        fsmtext = request.data.get("fsmtext", "")
        if CLIText == "" or fsmtext == "":
            return APIResponseResult.APIResponse(-1, '参数有误,请检查后在重试', )
        result = []
        try:
            with TemporaryFile('w+t') as f:
                # Read/write to the file
                f.write(fsmtext)
                # Seek back to beginning and read the data
                f.seek(0)
                template = TextFSM(f)
                result = template.ParseText(CLIText)
        except Exception as e:
            result.append({"msg": e.args})
        return APIResponseResult.APIResponse(0, 'success', results=result,
                                             http_status=status.HTTP_200_OK, )


class taskListDetailsViewSet(CustomViewBase):
    queryset = models.taskListDetails.objects.all().order_by('-id')
    serializer_class = modelSerializers.taskListDetailsSerializer


class deviceTypesViewSet(CustomViewBase):
    queryset = models.deviceTypes.objects.all().order_by('-id')
    serializer_class = modelSerializers.deviceTypesSerializer
    filter_class = modelFilters.deviceTypesFilter
    ordering_fields = ('id',)  # 排序
    permission_classes = [modelPermission.deviceTypesPermission]


class textFsmTemplatesViewSet(CustomViewBase):
    queryset = models.textFsmTemplates.objects.all().order_by('-id')
    serializer_class = modelSerializers.textFsmTemplatesSerializer
    filter_class = modelFilters.textFsmTemplatesFilter
    ordering_fields = ('id',)  # 排序
    permission_classes = [modelPermission.textFsmTemplatesPermission]
