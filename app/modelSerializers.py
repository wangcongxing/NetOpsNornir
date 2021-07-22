from rest_framework import viewsets, serializers, status
import requests, os, json
from app import models
from django.db import transaction
import ast
from utils import rsaEncrypt

from django.db.models import Q

rsaUtil = rsaEncrypt.RsaUtil()
ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsNornir import pro_settings as config
elif ENV_PROFILE == "test":
    from NetOpsNornir import test_settings as config
else:
    from NetOpsNornir import settings as config

NetOpsAssetsUrl = config.initConfig["NetOpsAssetsUrl"]


class taskListSerializer(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    lastTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    def create(self, validated_data):
        print("validated_data=", validated_data)

        assetsInfo = json.loads(self.initial_data.get("devInfo", "[]"))
        cmdids = list(filter(None, str(self.initial_data["cmdids"]).split(",")))
        if cmdids is []:
            # 如何返回错误信息
            return False

        username = self.initial_data.get("username", "")

        password = str(rsaUtil.encrypt_by_public_key(self.initial_data.get("password", "")), 'utf-8')

        tasklistdetails = []
        with transaction.atomic():
            taskList = super().create(validated_data)
            textfsmtemplates = models.cmdConfig.objects.filter(id__in=cmdids)
            for item in assetsInfo:
                print("item", item)
                for tft in textfsmtemplates:
                    if tft.deviceType.id == int(item["deviceType"]):
                        tasklistdetails.append(
                            models.readTaskListDetails(taskList=taskList,
                                                       ip=item["ip"],
                                                       deviceType_id=int(item["deviceType"]),
                                                       taskStatus="待处理",
                                                       cmdConfig=tft,
                                                       username=username,
                                                       password=password, port=item["port"], ))
            if tasklistdetails:
                models.readTaskListDetails.objects.bulk_create(tasklistdetails)
        return taskList

        # 验证code

    class Meta:
        model = models.readTaskList
        fields = ["id", "nid", "taskName", "taskStatus", "taskStatusValue", "callbackurl", "callbackcount", "desc",
                  "creator", "editor",
                  "lastTime", "createTime"]
        # depth = 1


class taskListDetailsSerializer(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    lastTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = models.readTaskListDetails
        fields = ["id", "taskList", "ip", "deviceType", "username", "password", "port", "createTime",
                  "lastTime", "creator", "editor"]
        depth = 1


class deviceTypesSerializer(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    lastTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = models.deviceTypes
        fields = ["id", "deviceKey", "deviceValue", "deviceState", "createTime", "lastTime", "creator", "editor"]
        # depth = 1


class cmdConfigSerializer(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    lastTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    def create(self, validated_data):
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})
        return super().update(instance, validated_data)

    class Meta:
        model = models.cmdConfig
        fields = ["id", "deviceKey", "deviceValue", "name", "cmds", "TextFSMTemplate", "desc", "createTime", "editor",
                  "lastTime", ]
        depth = 1


class cmdConfigSerializerExport(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    lastTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = models.cmdConfig
        fields = ["id", "deviceValue", "name", "cmds", "TextFSMTemplate", "desc", "createTime", "lastTime", "creator",
                  "editor", ]
        depth = 1


# 日常维护
class netmaintainSerializer(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    lastTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    # 当前任务所有IP
    progress = serializers.SerializerMethodField()

    def get_progress(self, obj):
        taskAll = models.netmaintainIpList.objects.filter(netmaintain=obj, )
        taskOkCount = taskAll.filter(~Q(taskStatus='待处理'))

        return '{:.0%}'.format(len(taskOkCount) / len(taskAll))

    def create(self, validated_data):
        password = validated_data["password"]
        phone = validated_data["phone"]
        # 加密手机号码
        validated_data.update({"phone": str(rsaUtil.encrypt_by_public_key(phone), 'utf-8')})
        # 加密登录设备密码
        validated_data.update({"password": str(rsaUtil.encrypt_by_public_key(password), 'utf-8')})
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})
        if self.initial_data["cmdtemp"]:
            validated_data.update({"nettemp_id": int(self.initial_data["cmdtemp"])})

        netmaintain = super().create(validated_data)

        dataTableKwargsData = json.loads(self.initial_data.get("dataTableKwargsData", "[]"))
        dataTableKwargsData = list(x for x in dataTableKwargsData if x["ip"] != '')
        netTaskList = {}
        for item in dataTableKwargsData:
            netip = str(item["ip"]).strip()
            if netip in netTaskList.keys():
                cmds = netTaskList[netip]
                netTaskList[netip] = cmds + [{"key": str(item["key"]).strip(), "value": str(item["value"])}]
            else:
                cmds = []
                cmds.append({"key": str(item["key"]).strip(), "value": str(item["value"]).strip()})
                netTaskList.update({netip: cmds})

        for key, items in netTaskList.items():
            netmaintainiplist = models.netmaintainIpList.objects.create(netmaintain=netmaintain,
                                                                        ip=key,
                                                                        creator=netmaintain.creator,
                                                                        editor=netmaintain.editor)
            for cmdKwargs in items:
                models.netmaintainIpListKwargs.objects.create(netmaintainIpList_id=netmaintainiplist.id,
                                                              key=cmdKwargs["key"],
                                                              value=cmdKwargs["value"],
                                                              creator=netmaintain.creator,
                                                              editor=netmaintain.editor)

        return netmaintain

    def update(self, instance, validated_data):
        password = validated_data["password"]
        phone = validated_data["phone"]
        # 加密手机号码
        validated_data.update({"phone": str(rsaUtil.encrypt_by_public_key(phone), 'utf-8')})
        validated_data.update({"password": str(rsaUtil.encrypt_by_public_key(password), 'utf-8')})
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})
        if self.initial_data["cmdtemp"]:
            validated_data.update({"nettemp_id": int(self.initial_data["cmdtemp"])})
        netmaintain = super().update(instance, validated_data)
        # 扩展参数
        # 判断id 是guid为新增  数字即修改create_update

        dataTableKwargsData = json.loads(self.initial_data.get("dataTableKwargsData", "[]"))
        dataTableKwargsData = list(x for x in dataTableKwargsData if x["ip"] != '')

        netTaskList = {}
        for item in dataTableKwargsData:
            netip = str(item["ip"]).strip()
            if netip in netTaskList.keys():
                cmds = netTaskList[netip]
                netTaskList[netip] = cmds + [{"key": str(item["key"]).strip(), "value": str(item["value"])}]
            else:
                cmds = []
                cmds.append({"key": str(item["key"]).strip(), "value": str(item["value"]).strip()})
                netTaskList.update({netip: cmds})

        with transaction.atomic():
            # 清空之前上次提交的所有参数
            models.netmaintainIpList.objects.filter(netmaintain__id=netmaintain.id).delete()

            # 批量新增
            for key, items in netTaskList.items():
                netmaintainiplist = models.netmaintainIpList.objects.create(netmaintain=netmaintain,
                                                                            ip=key,
                                                                            creator=netmaintain.creator,
                                                                            editor=netmaintain.editor)
                for cmdKwargs in items:
                    models.netmaintainIpListKwargs.objects.create(netmaintainIpList_id=netmaintainiplist.id,
                                                                  key=cmdKwargs["key"],
                                                                  value=cmdKwargs["value"],
                                                                  creator=netmaintain.creator,
                                                                  editor=netmaintain.editor)

        return netmaintain

    class Meta:
        model = models.netmaintain
        fields = ["id", "name", "deviceType", "progress", 'nettemp', "deviceValue", "username", "password", "port",
                  "phone", "email",
                  "startTime", "cmds",
                  "desc",
                  "enabled",
                  "createTime", "lastTime", "creator", "editor"]
        depth = 1


class netmaintainIpListSerializer(serializers.ModelSerializer):
    executionInfo = serializers.SerializerMethodField()

    def get_executionInfo(self, obj):
        cmds = obj.netmaintain.cmds
        netmaintainiplistkwargs = models.netmaintainIpListKwargs.objects.filter(netmaintainIpList=obj)
        for cmdInfo in netmaintainiplistkwargs:
            cmds = str(cmds).replace(cmdInfo.key, cmdInfo.value)
        cmds = str(cmds).replace("\n", ",").replace(";", ",").split(",")  # 根据回撤逗号分割

        return cmds

    class Meta:
        model = models.netmaintainIpList
        fields = ["id", "ip", "executionInfo", "resultText", "cmdInfo", "exceptionInfo",
                  "createTime", "lastTime", "creator", "editor"]


class netmaintainExportSerializer(serializers.ModelSerializer):
    enabledShow = serializers.SerializerMethodField()

    def get_enabledShow(self, obj):
        return "已启用" if obj.enabled else "已禁用"

    class Meta:
        model = models.netmaintain
        fields = ["id", "name", "deviceValue", "username", "port", "email",
                  "startTime", "cmds",
                  "desc",
                  "enabledShow",
                  "createTime", "lastTime", "creator", "editor"]


class nettempSerializer(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    lastTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    def create(self, validated_data):
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})
        return super().update(instance, validated_data)

    class Meta:
        model = models.nettemp
        fields = ["id", "title", "deviceType", "deviceValue", "deviceTypeId", "cmds", "desc", "useCount", "createTime",
                  "lastTime", "creator",
                  "editor"]

        depth = 1


class lldpInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.lldpInfo
        fields = ["__all__"]
