from nornir.core.task import Result
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.task import Result
from nornir_utils.plugins.functions import print_result

from utils.cmdb_inventory_v2 import CMDBInventory

InventoryPluginRegister.register("cmdb_inventory", CMDBInventory)

# ip改为hostname也是兼容的
devs = [
    {'ip': 'sbx-nxos-mgmt.cisco.com', 'username': 'admin', 'password': '1!', 'port': 8181,
     'device_type': 'cisco_nxos'}
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
    return Result(host=task.host,
                  result=f'{task.host.name}: hello ',
                  changed=True
                  )


results = nr.run(task=say)
print_result(results)
