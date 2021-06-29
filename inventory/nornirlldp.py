from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from datetime import date


# 实验1： 调用nornir_napalm来获取设备的facts和interfaces信息
nr = InitNornir(config_file="config.yaml", dry_run=True)
results = nr.run(task=napalm_get, getters=["dis lldp neighbor-information list", "interfaces"])
print_result(results)

#实验2： 调用nornir_netmiko来获取设备信息
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")
results = nr.run(netmiko_send_command, command_string='sh clock')

print_result(results)

