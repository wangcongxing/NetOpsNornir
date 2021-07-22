from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from datetime import date

'''
# 实验1： 调用nornir_napalm来获取设备的facts和interfaces信息
nr = InitNornir(config_file="config.yaml", dry_run=True)
results = nr.run(task=napalm_get, getters=["dis lldp neighbor-information list", "interfaces"])
print_result(results)

'''


#实验2： 调用nornir_netmiko来获取设备信息
'''

'''


from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import os
#os.environ["NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/ntc_templates"
os.environ["NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"
#export NET_TEXTFSM=$/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates

nr = InitNornir(config_file="config.yaml")
results = nr.run(netmiko_send_command, command_string='dis lldp neighbor-information list', use_textfsm=True)

print_result(results)