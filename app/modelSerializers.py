from rest_framework import viewsets, serializers, status

from app import models


class taskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.taskList
        fields = ["id", "nid", "taskName", "taskStatus", "callbackurl", "callbackcount", "remarks", ]
        # depth = 1


class taskListDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.taskListDetails
        fields = ["id", "taskList", "ip", "device_type", "device_type", "username", "password", "prot", ]
        # depth = 1


class deviceTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.deviceTypes
        fields = ["id", "deviceKey", "deviceValue", "createTime", "lastTime", "editor"]
        # depth = 1


class textFsmTemplatesSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        username = self.context["request"].user["username"]
        validated_data.update({"creator": username, "editor": username})
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        username = self.context["request"].user["username"]
        validated_data.update({"editor": username})
        validated_data.update({"deviceType_id": int(self.initial_data["deviceType"])})
        return super().update(instance, validated_data)

    class Meta:
        model = models.textFsmTemplates
        fields = ["id", "deviceKey", "deviceValue", "cmds", "TextFSMTemplate", "createTime", "editor", "lastTime", ]
        depth = 1


class textFsmTemplatesSerializerExport(serializers.ModelSerializer):
    class Meta:
        model = models.textFsmTemplates
        fields = ["id", "deviceValue", "cmds", "TextFSMTemplate", "desc", "createTime", "lastTime", "creator",
                  "editor", ]
        depth = 1
