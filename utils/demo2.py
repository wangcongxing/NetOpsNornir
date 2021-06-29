from nornir.core.task import Result
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.task import Result
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command

from utils.cmdb_inventory_v2 import CMDBInventory
import os

os.environ[
    "NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"


#os.environ["NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/ntc_templates"

InventoryPluginRegister.register("cmdb_inventory", CMDBInventory)

# ip改为hostname也是兼容的
devs = [
    {'ip': '10.32.1.1', 'username': 'admin', 'password': 'password123456', 'port': 22,
     'device_type': 'hp_comware', "data": {"id": "1"}},
    {'ip': '10.32.1.2', 'username': 'admin', 'password': 'password123456', 'port': 22,
     'device_type': 'hp_comware', "data": {"id": "2"}},
    {'ip': '10.32.1.3', 'username': 'admin', 'password': 'password123456', 'port': 22,
     'device_type': 'hp_comware', "data": {"id": "3"}},
    {'ip': '10.32.4.1', 'username': 'admin', 'password': 'password123456', 'port': 22,
     'device_type': 'hp_comware', "data": {"id": "4"}}
]
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


def say(task):
    print(task)
    return Result(host=task.host,
                  result=f'{task.host.name}: hello ',
                  changed=True
                  )
results = nr.run(task=say)
print_result(results)


'''
# display lldp neighbor
results = nr.run(netmiko_send_command, command_string='display lldp neighbor verbose', use_textfsm=True)

print_result(results)
'''