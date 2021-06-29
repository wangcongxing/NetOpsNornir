from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from datetime import date

# https://zhuanlan.zhihu.com/p/345775895

# 实验1： 调用nornir_napalm来获取设备的lldp和interfaces信息 使用napalm_get 报错
'''
nr = InitNornir(config_file="config.yaml", dry_run=True)
results = nr.run(task=napalm_get, getters=["facts", "interfaces"])
print_result(results)
'''
from importlib.resources import path as importresources_path
import os
#os.environ["NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/ntc_templates"
os.environ["NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"
#export NET_TEXTFSM=$/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates

# 实验2： 调用nornir_netmiko来获取设备信息
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result

'''

'''
nr = InitNornir(config_file="config.yaml")
#display lldp neighbor
results = nr.run(netmiko_send_command, command_string='display device', use_textfsm=True)

print_result(results)
'''


# 创建第三个实验脚本nornir3.py，脚本代码内容如下：
from nornir.core.filter import F

nr = InitNornir(config_file="config.yaml")
group1 = nr.filter(F(groups__contains="cisco_group1"))
group2 = nr.filter(~F(groups__contains="cisco_group1"))
results = group1.run(netmiko_send_command, command_string='sh ip int brief')

print_result(results)

# 创建第三个实验脚本nornir3.py，脚本代码内容如下：
from nornir.core.filter import F

nr = InitNornir(config_file="config.yaml")
group1 = nr.filter(F(groups__contains="cisco_group1"))
group2 = nr.filter(~F(groups__contains="cisco_group1"))
results = group1.run(netmiko_send_command, command_string='sh ip int brief')
# results = group1.run(netmiko_send_command, command_string='sh ip int brief')
print_result(results)

# 第四个实验脚本
nr = InitNornir(config_file="config.yaml")
targets = nr.filter(building='1')
results = targets.run(netmiko_send_command, command_string='sh ip arp ')
print_result(results)

# 实验5： 在filter()中使用lambda来过滤单个或多个设备
nr = InitNornir(config_file="config.yaml")
sw4 = nr.filter(filter_func=lambda host: host.name == 'sw4')
results = sw4.run(netmiko_send_command, command_string='sh ip arp')
# 同样的原理，如果你想使用IP地址来过滤，只需要将代码稍作修改如下即可：
# switches = ['192.168.2.11', '192.168.2.12', '192.168.2.13']
# sw1_sw2_sw3 = nr.filter(filter_func=lambda host: host.hostname in switches)

print_result(results)

# 实验6： 用Nornir给设备做配置
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result, print_title

nr = InitNornir(config_file="config.yaml")


def config(cisco):
    cisco.run(task=netmiko_send_config, config_file='commands.cfg')
    cisco.run(task=netmiko_send_command, command_string='show vlan brief')


print_title('正在配置VLAN999')
results = nr.run(task=config)

print_result(results)

# 实验7： 用Nornir保存设备配置

from nornir_utils.plugins.tasks.files import write_file
from datetime import date


def backup_configurations(task):
    r = task.run(task=napalm_get, getters=["config"])
    task.run(task=write_file, content=r.result["config"]["running"],
             filename=str(task.host.name) + "-" + str(date.today()) + ".txt")


nr = InitNornir(config_file="config.yaml")
result = nr.run(name="正在备份交换机配置", task=backup_configurations)

print_result(result)

'''