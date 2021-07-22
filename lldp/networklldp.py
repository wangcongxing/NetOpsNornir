from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from netmiko import SSHDetect, Netmiko
import os
from netmiko import ConnectHandler

# os.environ["NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/ntc_templates"
os.environ[
    "NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"
# export NET_TEXTFSM=$/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates


# 批量写描述信息
'''


nr = InitNornir(config_file="config.yaml")

# display lldp neighbor
results = nr.run(netmiko_send_command, command_string='display lldp neighbor verbose', use_textfsm=True)

for key, item in results.items():
    for info in item:
        print("key={},info={}".format(key, info))

print_result(results)
'''
'''
dev_info = {
    "device_type": 'hp_comware',
    "ip": '10.32.1.1',
    "username": "admin",
    "password": "password123456",
    "conn_timeout": 20,
    "port": 22,
    # 'global_delay_factor': 1
}
'''

'''
guesser = SSHDetect(**dev_info)
best_match = guesser.autodetect()
print("best_match is{}".format(best_match))
print("all guessers is:{}".format(guesser.potential_matches))
dev_info["device_type"] = best_match
print("dev_info=", dev_info)

with ConnectHandler(**dev_info) as conn:
    print("已经成功登陆交换机" + dev_info['ip'])
    result = conn.send_command_timing("display lldp neighbor verbose",
                                      use_textfsm=True)  # display lldp neighbor verbose
    print(result)
    for item in result:
        print("item=", item)
'''

hisList = {}


def lldpTree(ip):
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
    with ConnectHandler(**dev_info) as conn:
        print("已经成功登陆交换机" + dev_info['ip'])
        result = conn.send_command_timing("display lldp neighbor verbose",
                                          use_textfsm=True)  # display lldp neighbor verbose
        print("ip=", ip)
        # result = list(filter(lambda n: n["management_ip"] != ip, result))
        print(result)

        for item in result:
            if item["neighbor"] not in hisList.keys():
                hisList.update({item["neighbor"]: item["neighbor"]})

                lldpTree(item["management_ip"])


lldpTree("10.32.1.1")
