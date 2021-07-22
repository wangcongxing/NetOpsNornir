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
import xlwt, openpyxl
from django.http import HttpResponse
from netmiko import ConnectHandler
from django.db.models import Q
from time import strftime, localtime
from netmiko import SSHDetect, Netmiko
from getpass import getpass
import ast
from utils import rsaEncrypt
from concurrent.futures import ThreadPoolExecutor
import requests

rsaUtil = rsaEncrypt.RsaUtil()

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


# 通过Nornir执行命令
def Nornir_Netmiko_Cmd(task):
    print("task.host=====", task.host)
    print("task.host.name=====", task.host.name)
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
                taskListdetails = models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).first()
                taskListdetails.oldResult = cliText[0].result
                taskListdetails.jsonResult = jsonResult
                taskListdetails.save()
            elif os.path.exists(textfsm_ntc_templates):
                # 2.如果没有配置textFSM用系统自带的,use_textfsm=True
                results = task.run(netmiko_send_command, command_string=item["cmd"], use_textfsm=True)
                print_result(results)
                taskListdetails = models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).first()
                taskListdetails.jsonResult = jsonResult
                taskListdetails.save()

            else:
                # 3.使用netmiko_send_command 模块执行
                cliText = task.run(netmiko_send_command, command_string=item["cmd"])
                taskListdetails = models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).first()
                taskListdetails.oldResult = cliText[0].result
                taskListdetails.save()

        except Exception as e:
            print("Nornir_Netmiko_Cmd Exception=", e)
    return jsonResult


# 通过netmiko 获取数据 只读
def Read_Send_Command(dev):
    nid = dev["nid"]
    taskListdetails = models.readTaskListDetails.objects.filter(id=nid).first()
    if taskListdetails is None:
        return False
    try:
        password = rsaUtil.decrypt_by_private_key(dev["password"])

        dev_info = {
            "device_type": dev["device_type"],
            "ip": dev["ip"],
            "username": dev["username"],
            "password": password,
            "conn_timeout": 20,
            "port": 22,
            # 'global_delay_factor': 1
        }

        firstCmds = dev["firstCmds"]
        cmd = dev["cmd"]
        textfsm = dev["textfsm"]

        # Task类通过host属性，读取yaml配置，获取其中设备信息
        # 判断文件是否存在
        # 不存在创建/有直接使用
        # 3.如果自己配置的textFSM报错,则使用系统模版use_textfsm=True
        jsonResult = []
        # 自定义textFSM不为空，并且自定义文件夹存在textFSM模版
        oldResult = ""
        with ConnectHandler(**dev_info) as conn:
            print("已经成功登陆交换机" + dev_info['ip'])
            print("nid=", nid)
            # 系统虚拟环境路径
            textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates/" + dev_info[
                "device_type"] + "_" + cmd.replace(" ", "_") + ".textfsm"
            # 自定TextFSM模版路径
            textFsmTemplate = os.path.join(NTC_TEMPLATES_DIR,
                                           '{}_{}.textfsm'.format(dev_info["device_type"], cmd.replace(" ", "_")))
            # 记录下来用户回溯
            resultText = []
            cmdInfo = []
            command_cmds = str(firstCmds + "," + cmd).replace("/n", ",").split(',')
            for cmd_text in command_cmds:
                oldResult = conn.send_command_timing(cmd_text)
                resultText.append(
                    {"time": strftime('%Y-%m-%d %H:%M:%S', localtime()),
                     "base_prompt": "<{}>".format(conn.base_prompt),
                     "cmd": "{}".format(cmd),
                     "result": "<{}>{}\n{}".format(conn.base_prompt, cmd, oldResult)})
                cmdInfo.append(
                    "<{}>{}".format(conn.base_prompt, cmd) + "\n" + "<{}>{}".format(conn.base_prompt, oldResult))

            oldResult = resultText[-1]["result"]
            cmd = resultText[-1]["cmd"]

            if textfsm != "" or os.path.exists(textFsmTemplate):
                # 1.如果配置textFSM就用配置的
                if not os.path.exists(textFsmTemplate):
                    f = open(textFsmTemplate, mode='w+', encoding='UTF-8')
                    # open()打开一个文件，返回一个文件对象
                    f.write(textfsm)  # 写入textfsm
                    f.close()
                # print(cmd)
                # Task类调用run方法，执行任务，如netmiko_send_command、write_file等插件use_textfsm=True
                # 为什么不用use_textfsm=True  自定义模版需要频繁改动index文件 风险高
                # output = result.result
                f = open(textFsmTemplate)
                template = TextFSM(f)
                jsonResult = template.ParseTextToDicts(oldResult)  # template.ParseText(oldResult)
                taskListdetails.jsonResult = jsonResult
            else:
                # 2.如果没有配置textFSM用系统自带的,use_textfsm=True

                results = conn.send_command_timing(cmd, use_textfsm=True)
                taskListdetails.jsonResult = results
            conn.disconnect()

            taskListdetails.exceptionInfo = ""
            taskListdetails.cmdInfo = cmdInfo
            taskListdetails.resultText = resultText
            taskListdetails.taskStatus = "已完成"
            taskListdetails.save()

    except Exception as e:
        taskListdetails.exceptionInfo = e.args
        taskListdetails.save()


# 日常维护写入配置操作
def Write_Send_Command(nid):
    try:
        item = models.netmaintainIpList.objects.get(id=int(nid))
        netTask = item.netmaintain
        password = rsaUtil.decrypt_by_private_key(netTask.password)
        dev_info = {
            "device_type": netTask.deviceType.deviceKey,
            "ip": item.ip,
            "username": netTask.username,
            "password": password,
            "conn_timeout": 20,
            "port": netTask.port,
        }
        cmds = netTask.cmds
        nid = item.id
        netmaintainiplistkwargs = models.netmaintainIpListKwargs.objects.filter(netmaintainIpList=item)
        for cmdInfo in netmaintainiplistkwargs:
            cmds = str(cmds).replace(cmdInfo.key, cmdInfo.value)
        cmds = str(cmds).replace("\n", ",").replace(";", ",").split(",")  # 根据回撤逗号分割
        print("cmds=", cmds)
        resultText = []
        cmdInfo = []
        with ConnectHandler(**dev_info) as conn:
            print("已经成功登陆交换机" + dev_info['ip'])
            print("nid=", nid)
            for cmd in cmds:
                result = conn.send_command_timing(str(cmd).strip())
                resultText.append(
                    {"time": strftime('%Y-%m-%d %H:%M:%S', localtime()),
                     "cmd": "<{}>{}".format(conn.base_prompt, cmd),
                     "result": "<{}>{}".format(conn.base_prompt, result)})
                cmdInfo.append(
                    "<{}>{}".format(conn.base_prompt, cmd) + "\n" + "<{}>{}".format(conn.base_prompt, result))
            conn.disconnect()

            item.exceptionInfo = ""
            item.cmdInfo = "\n".join(cmdInfo)
            item.resultText = ast.literal_eval(item.resultText) + resultText
            item.taskStatus = "已完成"

    except Exception as e:
        item.taskStatus = "执行失败"
        item.exceptionInfo = e.args
    finally:
        item.save()


# 获取网络拓扑图
hisList = {}


def Get_lldp_Info(lldpinfo, parent, ip):
    print("hisList=", hisList)
    dev_info = {
        "device_type": 'hp_comware',
        "ip": ip,
        "username": "admin",
        "password": "password123456",
        "conn_timeout": 20,
        "port": 22,
        # 'global_delay_factor': 1
    }
    try:
        with ConnectHandler(**dev_info) as conn:
            print("已经成功登陆交换机" + dev_info['ip'])
            result = conn.send_command_timing("display lldp neighbor verbose",
                                              use_textfsm=True)  # display lldp neighbor verbose
            print("ip=", ip)
            # result = list(filter(lambda n: n["management_ip"] != ip, result))
            print(result)
            for item in result:
                if item["neighbor"] not in hisList.keys():
                    hisList.update({item["neighbor"]: item["neighbor"]})
                    pObj = models.lldpDetailsInfo.objects.create(lldpInfo=lldpinfo, parent=parent,
                                                                 local_interface=item["local_interface"],
                                                                 chassis_id=item["chassis_id"],
                                                                 neighbor_port_id=item["neighbor_port_id"],
                                                                 neighbor_interface=item["neighbor_interface"],
                                                                 neighbor=item["neighbor"],
                                                                 management_ip=item["management_ip"],
                                                                 vlan=item["vlan"], )
                    Get_lldp_Info(lldpinfo, pObj, item["management_ip"])
    except Exception as e:
        print("e=", e.args)


# 将拓扑图转化成json
def get_lldp_sub(childs):
    children = []
    if childs:
        for child in childs:
            data = {"lldpInfo": child.lldpInfo.title, "parent": child.parent.id,
                    "local_interface": child.local_interface,
                    "chassis_id": child.chassis_id,
                    "neighbor_port_id": child.neighbor_port_id,
                    "neighbor_interface": child.neighbor_interface,
                    "neighbor": child.neighbor,
                    "management_ip": child.management_ip,
                    "vlan": child.vlan,
                    "list": []}
            _childs = models.lldpDetailsInfo.objects.filter(parent=child)
            if _childs:
                data["list"] = get_lldp_sub(_childs)
            children.append(data)
    return children


class taskListViewSet(CustomViewBase):
    queryset = models.readTaskList.objects.all().order_by('-id')
    serializer_class = modelSerializers.taskListSerializer
    filter_class = modelFilters.taskListFilter
    ordering_fields = ('id',)  # 排序
    permission_classes = [modelPermission.taskListPermission]

    @action(methods=['get'], detail=False, url_path='run')
    def run(self, request, *args, **kwargs):
        # print("device_type_cmds=", device_type_cmds)
        nid = request.GET.get("nid", None)
        if nid is None:
            taskListResult = models.readTaskList.objects.filter(taskStatus='待处理').order_by("createTime")[0:3]
        else:
            taskListResult = models.readTaskList.objects.filter(id=int(nid), taskStatus='待处理')
        command_list = []
        for item in taskListResult:
            taskListDetailsResult = models.readTaskListDetails.objects.filter(Q(taskStatus='待处理'), taskList=item, )  #
            devs = []
            for subItem in taskListDetailsResult:
                devs.append(
                    {'nid': subItem.id, 'ip': subItem.ip, 'username': subItem.username, 'password': subItem.password,
                     'port': subItem.port,
                     'device_type': subItem.deviceType.deviceKey,
                     "nid": subItem.id,
                     "firstCmds": subItem.cmdConfig.firstCmds,
                     "cmd": subItem.cmdConfig.cmds,
                     "textfsm": subItem.cmdConfig.TextFSMTemplate})
            command_list.append({"devs": devs})
        runInfo = []
        runInfo.append({"start": strftime('%Y-%m-%d %H:%M:%S', localtime())})
        print("command_list=", command_list)
        with ThreadPoolExecutor(max_workers=20) as executor:
            for commandList in command_list:
                executor.map(Read_Send_Command, commandList["devs"])
        '''
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
        results = nr.run(task=Nornir_Netmiko_Cmd)
        # item.taskStatus = 2
        '''
        # item.taskStatus = 2
        # item.save()

        runInfo.append({"end": strftime('%Y-%m-%d %H:%M:%S', localtime())})
        return APIResponseResult.APIResponse(0, "success", runInfo)

    # 下载执行结果
    @action(methods=['get'], detail=False, url_path='runResult')
    def runResult(self, request, *args, **kwargs):
        nid = request.data.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "参数有无请稍后再试")
        task = models.readTaskList.objects.get(id=int(nid))
        tasklistdetails = models.readTaskListDetails.objects.filter(taskList=task)
        downloadResult = {}
        for item in tasklistdetails:
            if item.ip in downloadResult.keys():
                newResult = downloadResult[item.ip]
                newResult.append({"cmds": item.cmdConfig.cmds, "TextFSM": item.cmdConfig.TextFSMTemplate,
                                  "resultText": item.resultText,
                                  "cmdInfo": item.cmdInfo,
                                  "jsonResult": item.jsonResult,
                                  "exceptionInfo": item.exceptionInfo,
                                  "createTime": item.createTime,
                                  "lastTime": item.createTime, })
                downloadResult[item.ip] = newResult
            else:
                downloadResult.update({item.ip: [
                    {"cmds": item.cmdConfig.cmds, "TextFSM": item.cmdConfig.TextFSMTemplate,
                     "resultText": item.resultText,
                     "cmdInfo": item.cmdInfo,
                     "jsonResult": item.jsonResult,
                     "exceptionInfo": item.exceptionInfo,
                     "createTime": item.createTime,
                     "lastTime": item.createTime, }]})
        return APIResponseResult.APIResponse(0, 'success', results=downloadResult,
                                             http_status=status.HTTP_200_OK, )

    @action(methods=['get'], detail=False, url_path='downloadResult')
    def downloadResult(self, request, *args, **kwargs):
        nid = request.data.get("nid", 0)
        task = models.readTaskList.objects.get(id=int(nid))
        tasklistdetails = models.readTaskListDetails.objects.filter(taskList=task)
        sheetNames = tasklistdetails.values("cmdConfig__name", "cmdConfig_id").distinct()
        # 创建工作簿
        # wb = openpyxl.Workbook()
        wb = xlwt.Workbook()
        # 通过指令新建sheet
        for sheetName in sheetNames:
            # wb.create_sheet(sheetName["cmdConfig__name"])
            wb.add_sheet(sheetName["cmdConfig__name"])
        # 通过模版id查询 对应的结果
        for sheetName in sheetNames:
            rows = tasklistdetails.filter(cmdConfig_id=sheetName["cmdConfig_id"]).values("ip",
                                                                                         "deviceType__deviceValue",
                                                                                         "cmdConfig__cmds",
                                                                                         "taskStatus",
                                                                                         "cmdInfo",
                                                                                         "jsonResult",
                                                                                         "createTime",
                                                                                         "lastTime",
                                                                                         "creator")
            print("rows=", rows)
            listResult = []
            for item in rows:
                jsonResult = item["jsonResult"]
                if jsonResult:
                    if jsonResult == "[]":
                        cliValueResult = {}
                        cliValueResult.update({"IP": item["ip"], "设备类型": item["deviceType__deviceValue"],
                                               "指令": item["cmdConfig__cmds"],
                                               "状态": item["taskStatus"],
                                               "原始结果": item["cmdInfo"], "序列化结果": item["jsonResult"],
                                               "创建时间": item["createTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                               "修改时间": item["lastTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                               "创建者": item["creator"]})
                        listResult.append(cliValueResult)
                    else:
                        rowDict = ast.literal_eval(jsonResult)
                        for listItem in rowDict:
                            cliValueResult = {}
                            cliValueResult.update({"IP": item["ip"], "设备类型": item["deviceType__deviceValue"],
                                                   "指令": item["cmdConfig__cmds"],
                                                   "状态": item["taskStatus"],
                                                   "原始结果": item["cmdInfo"], "序列化结果": item["jsonResult"],
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
                                           "指令": item["cmdConfig__cmds"],
                                           "状态": item["taskStatus"],
                                           "原始结果": item["cmdInfo"], "序列化结果": item["jsonResult"],
                                           "创建时间": item["createTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                           "修改时间": item["lastTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                           "创建者": item["creator"]})
                    listResult.append(cliValueResult)
            # sheet = wb[sheetName["cmdConfig__name"]]
            sheet = wb.get_sheet(sheetName["cmdConfig__name"])
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
                    value = data[k]
                    if len(value) > 32000:
                        value = value[0:32000]
                    sheet.write(i, j, value)
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
    queryset = models.readTaskListDetails.objects.all().order_by('-id')
    serializer_class = modelSerializers.taskListDetailsSerializer


class deviceTypesViewSet(CustomViewBase):
    queryset = models.deviceTypes.objects.all().order_by('-id')
    serializer_class = modelSerializers.deviceTypesSerializer
    filter_class = modelFilters.deviceTypesFilter
    ordering_fields = ('-deviceState',)  # 排序
    permission_classes = [modelPermission.deviceTypesPermission]
    # 指定默认的排序字段
    ordering = ('-deviceState',)

    # 修改状态
    @action(methods=['put'], detail=False, url_path='resetEnabled')
    def resetEnabled(self, request, *args, **kwargs):
        nid = request.data.get('nid', None)
        if nid is None:
            return APIResponseResult.APIResponse(-1, '请求发生错误,请稍后再试!')
        deviceType = models.deviceTypes.objects.filter(id=nid).first()
        if deviceType is None:
            return APIResponseResult.APIResponse(-2, '请求数据不存在,请稍后再试!')
        deviceType.deviceState = 0 if int(deviceType.deviceState) else 1
        deviceType.save()
        return APIResponseResult.APIResponse(0, "已启用" if deviceType.deviceState else "已禁用")


class cmdConfigViewSet(CustomViewBase):
    queryset = models.cmdConfig.objects.all().order_by('-id')
    serializer_class = modelSerializers.cmdConfigSerializer
    filter_class = modelFilters.cmdConfigFilter
    ordering_fields = ('id',)  # 排序
    permission_classes = [modelPermission.cmdConfigPermission]


class netmaintainViewSet(CustomViewBase):
    queryset = models.netmaintain.objects.all().order_by('-id')
    serializer_class = modelSerializers.netmaintainSerializer
    filter_class = modelFilters.netmaintainFilter
    ordering_fields = ('id',)  # 排序
    permission_classes = [modelPermission.netmaintainTemplatesPermission]

    # 修改状态
    @action(methods=['put'], detail=False, url_path='resetEnabled')
    def resetEnabled(self, request, *args, **kwargs):
        nid = request.data.get('nid', None)
        if nid is None:
            return APIResponseResult.APIResponse(-1, '请求发生错误,请稍后再试!')
        netTask = models.netmaintain.objects.filter(id=nid).first()
        if netTask is None:
            return APIResponseResult.APIResponse(-2, '请求数据不存在,请稍后再试!')
        netTask.enabled = False if netTask.enabled else True
        netTask.save()
        return APIResponseResult.APIResponse(0, "已启用" if netTask.enabled else "已禁用")

    # 日常维护
    @action(methods=['get'], detail=False, url_path='run')
    def run(self, request, *args, **kwargs):
        netmaintainIpLists = models.netmaintainIpList.objects.filter(Q(taskStatus='待处理'),
                                                                     netmaintain__startTime__lte=strftime(
                                                                         '%Y-%m-%d %H:%M:%S', localtime()),
                                                                     netmaintain__enabled=True).order_by(
            '-lastTime', )
        runInfo = []
        cmdInfo = []
        runInfo.append({"start": strftime('%Y-%m-%d %H:%M:%S', localtime())})
        with ThreadPoolExecutor(max_workers=20) as executor:
            for item in netmaintainIpLists:
                infos = {item.id}
                executor.map(Write_Send_Command, infos)
        runInfo.append({"end": strftime('%Y-%m-%d %H:%M:%S', localtime())})
        return APIResponseResult.APIResponse(0, "success", runInfo)

    # 下载
    @action(methods=['get'], detail=False, url_path='download')
    def download(self, request, *args, **kwargs):
        nid = request.GET.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "参数有无请稍后再试!!!")
        result = models.netmaintainIpList.objects.filter(netmaintain__id=nid, ).values("netmaintain__name", "ip",
                                                                                       "cmdInfo",
                                                                                       "resultText",
                                                                                       "taskStatus", "exceptionInfo",
                                                                                       "createTime", "lastTime",
                                                                                       "creator",
                                                                                       "editor")

        return APIResponseResult.APIResponse(0, "ok", result)

    # 返回扩展参数
    @action(methods=['get'], detail=False, url_path='dataIpInfo')
    def dataIpInfo(self, request, *args, **kwargs):
        nid = request.GET.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "参数有无请稍后再试!!!")
        datainfo = []
        result = models.netmaintainIpList.objects.filter(netmaintain__id=nid, ).order_by("ip").values("id", "ip")
        for item in result:
            netmaintainiplistkwargs = models.netmaintainIpListKwargs.objects.filter(netmaintainIpList__id=item["id"])
            for kInfo in netmaintainiplistkwargs:
                datainfo.append({
                    "id": kInfo.id,
                    "pid": item["id"],
                    "ip": item["ip"],
                    "key": kInfo.key,
                    "value": kInfo.value
                })
        return APIResponseResult.APIResponse(0, "ok", datainfo)


class netmaintainIpListViewSet(CustomViewBase):
    queryset = models.netmaintainIpList.objects.all().order_by('-id', )
    serializer_class = modelSerializers.netmaintainIpListSerializer
    filter_class = modelFilters.netmaintainIpListFilter
    ordering_fields = ['useCount', '-id', ]  # 排序
    permission_classes = [modelPermission.netmaintainIpListPermission]


# 运维场景
class nettempViewSet(CustomViewBase):
    queryset = models.nettemp.objects.all().order_by('-useCount', '-id', )
    serializer_class = modelSerializers.nettempSerializer
    filter_class = modelFilters.nettempFilter
    ordering_fields = ['useCount', '-id', ]  # 排序
    permission_classes = [modelPermission.nettempPermission]


# 网络拓扑
class lldpInfoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.lldpInfo.objects.all().order_by('createTime', )
    serializer_class = modelSerializers.lldpInfoSerializer

    # 日常维护
    @action(methods=['get'], detail=False, url_path='run')
    def run(self, request, *args, **kwargs):
        coreDeviceInfo = [{"ip": "10.32.1.1"}, ]
        runInfo = []
        runInfo.append({"start": strftime('%Y-%m-%d %H:%M:%S', localtime())})
        for item in coreDeviceInfo:
            lldpinfo = models.lldpInfo.objects.create(title="2020")
            pObj = models.lldpDetailsInfo.objects.create(lldpInfo=lldpinfo, parent=None,
                                                         local_interface="",
                                                         chassis_id="",
                                                         neighbor_port_id="",
                                                         neighbor_interface="",
                                                         neighbor="",
                                                         management_ip=item["ip"],
                                                         vlan="", )
            Get_lldp_Info(lldpinfo, pObj, item["ip"])
        runInfo.append({"end": strftime('%Y-%m-%d %H:%M:%S', localtime())})
        return APIResponseResult.APIResponse(0, "success", runInfo)

    @action(methods=['get'], detail=False, url_path='getlldp')
    def getlldp(self, request, *args, **kwargs):
        firstmenus = models.lldpDetailsInfo.objects.filter(parent=None).distinct().order_by('-id')
        # print(menus.query)
        tree = []

        for menu in firstmenus:
            menu_data = {"lldpInfo": menu.lldpInfo.title, "parent": menu.id,
                         "local_interface": menu.local_interface,
                         "chassis_id": menu.chassis_id,
                         "neighbor_port_id": menu.neighbor_port_id,
                         "neighbor_interface": menu.neighbor_interface,
                         "neighbor": menu.neighbor,
                         "management_ip": menu.management_ip,
                         "vlan": menu.vlan,
                         "list": []}
            childs = models.lldpDetailsInfo.objects.filter(parent=menu).order_by('-id')
            if childs:
                menu_data["list"] = get_lldp_sub(childs)
            tree.append(menu_data)
            # tree = [x for x in tree if x["list"] != []]
        return APIResponseResult.APIResponse(0, 'success', results=tree)
