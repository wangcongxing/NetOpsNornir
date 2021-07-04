from rest_framework import viewsets, serializers, status
import requests, os
from app import models
from django.db import transaction

ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsNornir import pro_settings as config
elif ENV_PROFILE == "test":
    from NetOpsNornir import test_settings as config
else:
    from NetOpsNornir import settings as config

NetOpsAssetsUrl = config.initConfig["NetOpsAssetsUrl"]


class taskListSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        print("validated_data=", validated_data)
        org_info = []
        # org_info = filter(lambda x: "layuiTreeCheck" in item, self.initial_data)
        for item in self.initial_data:
            if "layuiTreeCheck" in item:
                org_info.append(self.initial_data[item])
        print("org_info=", org_info)
        cmdids = filter(None, str(self.initial_data["cmdids"]).split(","))
        if cmdids is [] or org_info is []:
            # 如何返回错误信息
            return False
        # 调用查询资产接口 返回
        result = requests.get(
            NetOpsAssetsUrl + "/opsassets/app/networkAssets/get_assets_info/?access_token=" + self.initial_data[
                "access_token"] + "&orgid=" + ",".join(org_info), proxies={'http': None, 'https': None, }).json()
        print("result=", result)
        assetsInfo = result["data"]
        tasklistdetails = []
        with transaction.atomic():
            taskList = super().create(validated_data)
            textfsmtemplates = models.textFsmTemplates.objects.filter(id__in=cmdids)
            for item in assetsInfo:
                print("item", item)
                for tft in textfsmtemplates:
                    if tft.deviceType.id == int(item["deviceType"]):
                        tasklistdetails.append(
                            models.taskListDetails(taskList=taskList,
                                                   ip=item["mip"] if item["mip"] == "" else item["ip"],
                                                   deviceType_id=int(item["deviceType"]),
                                                   executeState="未完成",
                                                   oldResult="",
                                                   jsonResult="",
                                                   textfsmtemplates=tft,
                                                   username=item["username"],
                                                   password=item["password"], port=item["port"], ))
            if tasklistdetails:
                models.taskListDetails.objects.bulk_create(tasklistdetails)
        return taskList

        # 验证code



    class Meta:
        model = models.taskList
        fields = ["id", "nid", "taskName", "taskStatus", "taskStatusValue","callbackurl", "callbackcount", "desc", "creator", "editor",
                  "lastTime", "createTime"]
        # depth = 1


class taskListDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.taskListDetails
        fields = ["id", "taskList", "ip", "device_type", "device_type", "username", "password", "prot", "createTime",
                  "lastTime", "creator", "editor"]
        # depth = 1


class deviceTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.deviceTypes
        fields = ["id", "deviceKey", "deviceValue", "deviceState", "createTime", "lastTime", "creator", "editor"]
        # depth = 1


class textFsmTemplatesSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})
        return super().update(instance, validated_data)

    class Meta:
        model = models.textFsmTemplates
        fields = ["id", "deviceKey", "deviceValue", "name", "cmds", "TextFSMTemplate", "desc", "createTime", "editor",
                  "lastTime", ]
        depth = 1


class textFsmTemplatesSerializerExport(serializers.ModelSerializer):
    class Meta:
        model = models.textFsmTemplates
        fields = ["id", "deviceValue", "name", "cmds", "TextFSMTemplate", "desc", "createTime", "lastTime", "creator",
                  "editor", ]
        depth = 1
