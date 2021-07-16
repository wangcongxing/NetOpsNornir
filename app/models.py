from django.db import models
import uuid, os

ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsNornir import pro_settings as config
elif ENV_PROFILE == "test":
    from NetOpsNornir import test_settings as config
else:
    from NetOpsNornir import settings as config


# Create your models here.
def newguid():
    return str(uuid.uuid4())


def newImageName(instance, filename):
    # 日期目录和 随机文件名
    ext = str(filename.split('.')[-1]).upper()
    exts = ['PNG', 'JPG', 'GIF',]
    if ext not in exts:
        ext = "PNG"

    filename = os.path.join(config.MEDIA_ROOT, 'student/{}.{}'.format(uuid.uuid4().hex, ext))
    return filename


task_status_choices = (
    (0, "待处理"),
    (1, "处理中"),
    (2, "已完成"),
    (-1, "执行失败"),
)
device_state_choices = (
    (0, "禁用"),
    (1, "启用"),
)


# 设备类型
class deviceTypes(models.Model):
    deviceKey = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="设备Key", )
    deviceValue = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="设备类型", )
    devlogo = models.ImageField(upload_to=newImageName, blank=True, null=True, verbose_name="设备LOGO", )

    deviceState = models.CharField(max_length=255, default="0", blank=True, null=True, verbose_name="是否禁用",
                                   choices=device_state_choices)
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    class Meta:
        verbose_name = verbose_name_plural = '网络设备类型'

    def __str__(self):
        self.deviceValue


# textFSM 模版配置
class textFsmTemplates(models.Model):
    deviceType = models.ForeignKey(deviceTypes, null=True, blank=True, on_delete=models.SET_NULL,
                                   verbose_name="设备类型", )
    name = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="脚本名称", )
    firstCmds = models.TextField(verbose_name='预置脚本', max_length=500000, blank=True, default="")
    cmds = models.TextField(verbose_name='脚本', max_length=500000, blank=True, default="")
    TextFSMTemplate = models.TextField(verbose_name='TextFSM模版', max_length=500000, blank=True, default="")
    desc = models.TextField(verbose_name='备注', max_length=500000, blank=True, default="")

    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    def deviceValue(self):
        if self.deviceType is not None:
            return self.deviceType.deviceValue
        else:
            return ""

    def deviceKey(self):
        if self.deviceType is not None:
            return self.deviceType.id
        else:
            return ""

    class Meta:
        verbose_name = verbose_name_plural = 'textFSM模版配置'


# 任务列表 网络设备配置文件解析  只读
class taskList(models.Model):
    nid = models.CharField(verbose_name="任务编号", max_length=255, blank=False, null=False, default=newguid)
    eoaNumber = models.CharField(verbose_name="EOA编号", max_length=255, blank=True, null=True, default="")
    taskName = models.CharField(verbose_name="任务名称", max_length=255, blank=True, null=True, default="")
    taskStatus = models.IntegerField(verbose_name="任务状态", default=0, choices=task_status_choices, blank=False,
                                     null=False)
    callbackurl = models.URLField(verbose_name="回调地址", max_length=800, default="",
                                  blank=False, null=False)
    callbackcount = models.IntegerField(verbose_name="回调次数", default=1, blank=False, null=False)
    desc = models.TextField(verbose_name='备注', max_length=500000, blank=True, default="")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    def taskStatusValue(self):
        return task_status_choices[self.taskStatus][1]

    class Meta:
        verbose_name = verbose_name_plural = '任务列表'


# 任务详情表
class taskListDetails(models.Model):
    taskList = models.ForeignKey(taskList, null=True, blank=True, on_delete=models.CASCADE, verbose_name="任务列表", )

    ip = models.GenericIPAddressField(verbose_name="IP", default="", blank=False, null=False, )
    deviceType = models.ForeignKey(deviceTypes, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="设备类型", )
    textfsmtemplates = models.ForeignKey(textFsmTemplates, verbose_name="textFSM模版配置", blank=True, null=True,
                                         on_delete=models.SET_NULL, )
    username = models.CharField(verbose_name="用户名", max_length=255, blank=True, null=True, default="")
    password = models.CharField(verbose_name="密码", max_length=255, blank=True, null=True, default="")
    port = models.IntegerField(verbose_name="端口", blank=True, null=True, default=22)
    executeState = models.CharField(verbose_name="状态", max_length=255, blank=True, null=True, default="未完成")
    oldResult = models.TextField(verbose_name='原始结果', max_length=500000, blank=True, default="")
    jsonResult = models.TextField(verbose_name='解析结果', max_length=500000, blank=True, default="")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    class Meta:
        verbose_name = verbose_name_plural = '任务详情表'


# 日常维护 写入配置
class netmaintain(models.Model):
    name = models.CharField(verbose_name="事务名称", max_length=255, blank=True, default="")
    deviceType = models.ForeignKey(deviceTypes, null=True, blank=True, on_delete=models.SET_NULL,
                                   verbose_name="设备类型", )
    username = models.CharField(verbose_name="用户名", max_length=255, blank=True, default="")
    password = models.CharField(verbose_name="密码", max_length=255, blank=True, default="")
    port = models.IntegerField(verbose_name="端口", blank=True, null=True, default=22)
    phone = models.CharField(verbose_name="手机通知", max_length=255, blank=True, default="")
    email = models.CharField(verbose_name="邮箱通知", max_length=255, blank=True, default="")
    startTime = models.CharField(verbose_name="开始时间", max_length=255, blank=True, default="")
    enabled = models.BooleanField(max_length=255, default=False, blank=True, null=True, verbose_name="是否禁用")
    cmds = models.TextField(verbose_name="CMDS", max_length=500000, blank=True, default="")
    desc = models.TextField(verbose_name='备注', max_length=500000, blank=True, default="")

    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    def deviceValue(self):
        if self.deviceType is not None:
            return self.deviceType.deviceValue
        else:
            return ""

    class Meta:
        verbose_name = verbose_name_plural = '日常维护'


# 日常维护设备IP
class netmaintainIpList(models.Model):
    netmaintain = models.ForeignKey(netmaintain, null=True, blank=True, on_delete=models.CASCADE, verbose_name="日常运维", )
    ip = models.GenericIPAddressField(verbose_name="IP", max_length=255, blank=True, null=True, default="")

    resultText = models.TextField(verbose_name="运行结果Json", max_length=500000, blank=True, default="[]")
    cmdInfo = models.TextField(verbose_name="运行结果", max_length=500000, blank=True, default="[]")
    taskStatus = models.IntegerField(verbose_name="任务状态", default=0, choices=task_status_choices, blank=False,
                                     null=False)
    exceptionInfo = models.TextField(verbose_name="异常信息", max_length=500000, blank=True, default="")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    class Meta:
        verbose_name = verbose_name_plural = '日常维护设备IP'


# 扩展参数

class netmaintainIpListKwargs(models.Model):
    netmaintainIpList = models.ForeignKey(netmaintainIpList, null=True, blank=True, on_delete=models.CASCADE,
                                          verbose_name="日常运维", )
    key = models.CharField(verbose_name="参数名称", max_length=255, blank=True, null=True, default="")
    value = models.CharField(verbose_name="参数值", max_length=255, blank=True, null=True, default="")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    class Meta:
        verbose_name = verbose_name_plural = '扩展参数'


# 运维模版
class nettemp(models.Model):
    title = models.CharField(verbose_name="名称", max_length=255, blank=True, default="")
    deviceType = models.ForeignKey(deviceTypes, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="设备类型", )
    cmds = models.TextField(verbose_name="CMDS", max_length=500000, blank=True, default="")
    desc = models.TextField(verbose_name='备注', max_length=500000, blank=True, default="")
    useCount = models.IntegerField(verbose_name="使用次数", default=0, blank=False, null=False)

    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="创建者", )
    editor = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="修改者", )

    def deviceValue(self):
        if self.deviceType is not None:
            return self.deviceType.deviceValue
        else:
            return ""

    def deviceTypeId(self):
        if self.deviceType is not None:
            return self.deviceType.id
        else:
            return ""

    class Meta:
        verbose_name = verbose_name_plural = '扩展参数'
