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


# ?????????????????????
class opsBaseInitDB(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        # ??????????????????
        superUser, ctime = User.objects.update_or_create(
            defaults={'username': 'admin', 'is_staff': True, 'is_active': True, 'is_superuser': True,
                      'first_name': '?????????',
                      'password': make_password("admin@123")}, username='admin')
        superUser = superUser.username
        jsonResult = getDeviceType()
        for item in jsonResult:
            d, c = models.deviceTypes.objects.update_or_create(
                defaults={"deviceKey": item[0], "deviceValue": item[0],
                          'creator': superUser, 'editor': superUser},
                deviceKey=item[0])
        # ???venv ntc_templates????????????????????? ???????????? ntc_templates
        textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates"
        if os.path.exists(textfsm_ntc_templates):
            for tfile in os.listdir(textfsm_ntc_templates):
                shutil.copyfile(textfsm_ntc_templates + "/" + tfile, os.path.join(NTC_TEMPLATES_DIR, tfile))
        return HttpResponse("<h1>????????????????????????</h1>")


os.environ[
    "NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"
InventoryPluginRegister.register("cmdb_inventory", CMDBInventory)


# ??????Nornir????????????
def Nornir_Netmiko_Cmd(task):
    print("task.host=====", task.host)
    print("task.host.name=====", task.host.name)
    command_textfsm = task.host.data["data"]["command_textfsm"]
    # Task?????????host???????????????yaml?????????????????????????????????
    # ????????????????????????
    # ???????????????/???????????????

    # 3.?????????????????????textFSM??????,?????????????????????use_textfsm=True
    jsonResult = []

    for item in command_textfsm:
        customeTextFsm = item["textfsm"]
        # ????????????????????????
        textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates/" + task.host.platform + "_" + \
                                item["cmd"].replace(" ",
                                                    "_") + ".textfsm"
        # ??????TextFSM????????????
        textFsmTemplate = os.path.join(NTC_TEMPLATES_DIR,
                                       '{}_{}.textfsm'.format(task.host.platform, item["cmd"].replace(" ", "_")))
        try:
            # ?????????textFSM??????????????????????????????????????????textFSM??????

            if customeTextFsm != "" or os.path.exists(textFsmTemplate):
                # 1.????????????textFSM???????????????
                if not os.path.exists(textFsmTemplate):
                    f = open(textFsmTemplate, mode='w+', encoding='UTF-8')
                    # open()?????????????????????????????????????????????
                    f.write(item["textfsm"])  # ??????textfsm
                    f.close()
                # print(cmd)
                # Task?????????run???????????????????????????netmiko_send_command???write_file?????????use_textfsm=True
                # ???????????????use_textfsm=True  ?????????????????????????????????index?????? ?????????
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
                # 2.??????????????????textFSM??????????????????,use_textfsm=True
                results = task.run(netmiko_send_command, command_string=item["cmd"], use_textfsm=True)
                print_result(results)
                taskListdetails = models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).first()
                taskListdetails.jsonResult = jsonResult
                taskListdetails.save()

            else:
                # 3.??????netmiko_send_command ????????????
                cliText = task.run(netmiko_send_command, command_string=item["cmd"])
                taskListdetails = models.taskListDetails.objects.filter(id=task.host.data["data"]["nid"]).first()
                taskListdetails.oldResult = cliText[0].result
                taskListdetails.save()

        except Exception as e:
            print("Nornir_Netmiko_Cmd Exception=", e)
    return jsonResult


# ??????netmiko ???????????? ??????
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

        # Task?????????host???????????????yaml?????????????????????????????????
        # ????????????????????????
        # ???????????????/???????????????
        # 3.?????????????????????textFSM??????,?????????????????????use_textfsm=True
        jsonResult = []
        # ?????????textFSM??????????????????????????????????????????textFSM??????
        oldResult = ""
        with ConnectHandler(**dev_info) as conn:
            print("???????????????????????????" + dev_info['ip'])
            print("nid=", nid)
            # ????????????????????????
            textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates/" + dev_info[
                "device_type"] + "_" + cmd.replace(" ", "_") + ".textfsm"
            # ??????TextFSM????????????
            textFsmTemplate = os.path.join(NTC_TEMPLATES_DIR,
                                           '{}_{}.textfsm'.format(dev_info["device_type"], cmd.replace(" ", "_")))
            # ????????????????????????
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
                # 1.????????????textFSM???????????????
                if not os.path.exists(textFsmTemplate):
                    f = open(textFsmTemplate, mode='w+', encoding='UTF-8')
                    # open()?????????????????????????????????????????????
                    f.write(textfsm)  # ??????textfsm
                    f.close()
                # print(cmd)
                # Task?????????run???????????????????????????netmiko_send_command???write_file?????????use_textfsm=True
                # ???????????????use_textfsm=True  ?????????????????????????????????index?????? ?????????
                # output = result.result
                f = open(textFsmTemplate)
                template = TextFSM(f)
                jsonResult = template.ParseTextToDicts(oldResult)  # template.ParseText(oldResult)
                taskListdetails.jsonResult = jsonResult
                f.close()
            else:
                # 2.??????????????????textFSM??????????????????,use_textfsm=True

                results = conn.send_command_timing(cmd, use_textfsm=True)
                taskListdetails.jsonResult = results
            conn.disconnect()

            taskListdetails.exceptionInfo = ""
            taskListdetails.cmdInfo = cmdInfo
            taskListdetails.resultText = resultText
            taskListdetails.taskStatus = "?????????"
            taskListdetails.save()

    except Exception as e:
        print("nid={},ip={}".format(nid,dev["ip"]))
        taskListdetails.exceptionInfo = e.args
        taskListdetails.save()


# ??????????????????????????????
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
        cmds = str(cmds).replace("\n", ",").replace(";", ",").split(",")  # ????????????????????????
        print("cmds=", cmds)
        resultText = []
        cmdInfo = []
        with ConnectHandler(**dev_info) as conn:
            print("???????????????????????????" + dev_info['ip'])
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
            item.taskStatus = "?????????"

    except Exception as e:
        item.taskStatus = "????????????"
        item.exceptionInfo = e.args
    finally:
        item.save()


# ?????????????????????
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
            print("???????????????????????????" + dev_info['ip'])
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


# ?????????????????????json
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


class readTaskListViewSet(CustomViewBase):
    queryset = models.readTaskList.objects.all().order_by('-id')
    serializer_class = modelSerializers.readTaskListSerializer
    filter_class = modelFilters.readTaskListFilter
    ordering_fields = ('id',)  # ??????
    permission_classes = [modelPermission.readTaskListPermission]

    @action(methods=['get'], detail=False, url_path='run')
    def run(self, request, *args, **kwargs):
        # print("device_type_cmds=", device_type_cmds)
        nid = request.GET.get("nid", None)
        if nid is None:
            taskListResult = models.readTaskList.objects.filter(taskStatus='?????????').order_by("createTime")[0:3]
        else:
            taskListResult = models.readTaskList.objects.filter(id=int(nid), taskStatus='?????????')
        command_list = []
        for item in taskListResult:
            taskListDetailsResult = models.readTaskListDetails.objects.filter(Q(taskStatus='?????????'), taskList=item, )  #
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
        #print("command_list=", command_list)
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

    # ??????????????????
    @action(methods=['get'], detail=False, url_path='runResult')
    def runResult(self, request, *args, **kwargs):
        nid = request.data.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "???????????????????????????")
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
        # ???????????????
        # wb = openpyxl.Workbook()
        wb = xlwt.Workbook()
        # ??????????????????sheet
        for sheetName in sheetNames:
            # wb.create_sheet(sheetName["cmdConfig__name"])
            wb.add_sheet(sheetName["cmdConfig__name"])
        # ????????????id?????? ???????????????
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
                        cliValueResult.update({"IP": item["ip"], "????????????": item["deviceType__deviceValue"],
                                               "??????": item["cmdConfig__cmds"],
                                               "??????": item["taskStatus"],
                                               "????????????": item["cmdInfo"], "???????????????": item["jsonResult"],
                                               "????????????": item["createTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                               "????????????": item["lastTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                               "?????????": item["creator"]})
                        listResult.append(cliValueResult)
                    else:
                        rowDict = ast.literal_eval(jsonResult)
                        for listItem in rowDict:
                            cliValueResult = {}
                            cliValueResult.update({"IP": item["ip"], "????????????": item["deviceType__deviceValue"],
                                                   "??????": item["cmdConfig__cmds"],
                                                   "??????": item["taskStatus"],
                                                   "????????????": item["cmdInfo"], "???????????????": item["jsonResult"],
                                                   "????????????": item["createTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                                   "????????????": item["lastTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                                   "?????????": item["creator"]})
                            for k, v in listItem.items():
                                cliValueResult.update({k: v})
                            listResult.append(cliValueResult)
                else:
                    # jsonResult ????????? ????????????????????? ??????????????????
                    cliValueResult = {}
                    cliValueResult.update({"IP": item["ip"], "????????????": item["deviceType__deviceValue"],
                                           "??????": item["cmdConfig__cmds"],
                                           "??????": item["taskStatus"],
                                           "????????????": item["cmdInfo"], "???????????????": item["jsonResult"],
                                           "????????????": item["createTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                           "????????????": item["lastTime"].strftime("%Y-%m-%d %H:%M:%S"),
                                           "?????????": item["creator"]})
                    listResult.append(cliValueResult)
            # sheet = wb[sheetName["cmdConfig__name"]]
            sheet = wb.get_sheet(sheetName["cmdConfig__name"])
            # ?????????????????????
            if listResult:
                resultLength = []
                for i in listResult:
                    resultLength.append(len(i))
                m = resultLength.index(max(resultLength))
                firstItem = listResult[m]
                colnames = firstItem.keys()
                # ???Excel?????????????????????
                for index, name in enumerate(colnames):
                    sheet.write(0, index, name)
            # ????????????
            i = 1
            for data in listResult:
                for j, k in enumerate(data.keys()):
                    value = data[k]
                    if len(value) > 32000:
                        value = value[0:32000]
                    sheet.write(i, j, value)
                i = i + 1

        # ??????Excel
        buffer = BytesIO()
        wb.save(buffer)
        # ??????????????????????????????????????????????????????MIME??????
        resp = HttpResponse(buffer.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # ????????????????????????????????????????????? ???????????????????????????????????????
        filename = quote('{}.xls'.format(task.taskName))
        # ?????????????????????????????????????????????????????????????????????
        resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
        return resp

    # ??????excel ??????
    # https://cloud.tencent.com/developer/article/1518588
    @action(methods=['get'], detail=False, url_path='downLoadFile')
    def downLoadFile(self, request, *args, **kwargs):
        sheet = excel.pe.Sheet([[1, 2], [3, 4]])
        return excel.make_response(sheet, "xlsx")

    # TextFSM??????
    @action(methods=['post'], detail=False, url_path='TextFSMCheck')
    def TextFSMCheck(self, request, *args, **kwargs):
        CLIText = request.data.get("CLIText", "")
        fsmtext = request.data.get("fsmtext", "")
        if CLIText == "" or fsmtext == "":
            return APIResponseResult.APIResponse(-1, '????????????,?????????????????????', )
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

    @action(methods=['get'], detail=False, url_path='cliFormat')
    def cliFormat(self, request, *args, **kwargs):
        netmaintainiplist = models.readTaskListDetails.objects.filter(jsonResult='[]')
        for item in netmaintainiplist:
            # ??????TextFSM????????????
            textFsmTemplate = os.path.join(NTC_TEMPLATES_DIR,
                                           '{}_{}.textfsm'.format(item.deviceType.deviceKey,item.cmdConfig.cmds.replace(" ", "_")))

            with open(textFsmTemplate) as f:
                template = TextFSM(f)
                oldResult = ast.literal_eval(item.resultText)[-1]["result"]
                jsonResult = template.ParseTextToDicts(oldResult)  # template.ParseText(oldResult)
                print(jsonResult)
                item.jsonResult = jsonResult
                item.save()
                f.close()

class taskListDetailsViewSet(CustomViewBase):
    queryset = models.readTaskListDetails.objects.all().order_by('-id')
    serializer_class = modelSerializers.readTaskListDetailsSerializer


class deviceTypesViewSet(CustomViewBase):
    queryset = models.deviceTypes.objects.all().order_by('-id')
    serializer_class = modelSerializers.deviceTypesSerializer
    filter_class = modelFilters.deviceTypesFilter
    ordering_fields = ('-deviceState',)  # ??????
    permission_classes = [modelPermission.deviceTypesPermission]
    # ???????????????????????????
    ordering = ('-deviceState',)

    # ????????????
    @action(methods=['put'], detail=False, url_path='resetEnabled')
    def resetEnabled(self, request, *args, **kwargs):
        nid = request.data.get('nid', None)
        if nid is None:
            return APIResponseResult.APIResponse(-1, '??????????????????,???????????????!')
        deviceType = models.deviceTypes.objects.filter(id=nid).first()
        if deviceType is None:
            return APIResponseResult.APIResponse(-2, '?????????????????????,???????????????!')
        deviceType.deviceState = 0 if int(deviceType.deviceState) else 1
        deviceType.save()
        return APIResponseResult.APIResponse(0, "?????????" if deviceType.deviceState else "?????????")


class cmdConfigViewSet(CustomViewBase):
    queryset = models.cmdConfig.objects.all().order_by('-id')
    serializer_class = modelSerializers.cmdConfigSerializer
    filter_class = modelFilters.cmdConfigFilter
    ordering_fields = ('id',)  # ??????
    permission_classes = [modelPermission.cmdConfigPermission]


class netmaintainViewSet(CustomViewBase):
    queryset = models.netmaintain.objects.all().order_by('-id')
    serializer_class = modelSerializers.netmaintainSerializer
    filter_class = modelFilters.netmaintainFilter
    ordering_fields = ('id',)  # ??????
    permission_classes = [modelPermission.netmaintainTemplatesPermission]

    # ????????????
    @action(methods=['put'], detail=False, url_path='resetEnabled')
    def resetEnabled(self, request, *args, **kwargs):
        nid = request.data.get('nid', None)
        if nid is None:
            return APIResponseResult.APIResponse(-1, '??????????????????,???????????????!')
        netTask = models.netmaintain.objects.filter(id=nid).first()
        if netTask is None:
            return APIResponseResult.APIResponse(-2, '?????????????????????,???????????????!')
        netTask.enabled = False if netTask.enabled else True
        netTask.save()
        return APIResponseResult.APIResponse(0, "?????????" if netTask.enabled else "?????????")

    # ????????????
    @action(methods=['get'], detail=False, url_path='run')
    def run(self, request, *args, **kwargs):
        netmaintainIpLists = models.netmaintainIpList.objects.filter(Q(taskStatus='?????????'),
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


    # ??????
    @action(methods=['get'], detail=False, url_path='download')
    def download(self, request, *args, **kwargs):
        nid = request.GET.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "???????????????????????????!!!")
        result = models.netmaintainIpList.objects.filter(netmaintain__id=nid, ).values("netmaintain__name", "ip",
                                                                                       "cmdInfo",
                                                                                       "resultText",
                                                                                       "taskStatus", "exceptionInfo",
                                                                                       "createTime", "lastTime",
                                                                                       "creator",
                                                                                       "editor")

        return APIResponseResult.APIResponse(0, "ok", result)

    # ??????????????????
    @action(methods=['get'], detail=False, url_path='dataIpInfo')
    def dataIpInfo(self, request, *args, **kwargs):
        nid = request.GET.get("nid", 0)
        if nid == 0:
            return APIResponseResult.APIResponse(-1, "???????????????????????????!!!")
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
    ordering_fields = ['useCount', '-id', ]  # ??????
    permission_classes = [modelPermission.netmaintainIpListPermission]


# ????????????
class nettempViewSet(CustomViewBase):
    queryset = models.nettemp.objects.all().order_by('-useCount', '-id', )
    serializer_class = modelSerializers.nettempSerializer
    filter_class = modelFilters.nettempFilter
    ordering_fields = ['useCount', '-id', ]  # ??????
    permission_classes = [modelPermission.nettempPermission]


# ????????????
class lldpInfoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.lldpInfo.objects.all().order_by('createTime', )
    serializer_class = modelSerializers.lldpInfoSerializer

    # ????????????
    @action(methods=['get'], detail=False, url_path='run')
    def run(self, request, *args, **kwargs):
        coreDeviceInfo = [{"ip": "10.32.1.1"}, ]
        runInfo = []
        runInfo.append({"start": strftime('%Y-%m-%d %H:%M:%S', localtime())})
        for item in coreDeviceInfo:
            lldpinfo = models.lldpInfo.objects.create()
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
