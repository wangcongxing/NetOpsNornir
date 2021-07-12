from netmiko import ConnectHandler
from textfsm import TextFSM
import site
from netmiko import SSHDetect, Netmiko

# print(site.getsitepackages())
import os

os.environ[
    "NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"

'''
textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates"
if os.path.exists(textfsm_ntc_templates):
    for tfile in os.listdir(textfsm_ntc_templates):
        print("tfile",tfile)
'''

dev_info = {
    "device_type": "hp_comware",
    "ip": "10.32.1.3",
    "username": "admin",
    "password": "password123456",
    "port": 22,
    "conn_timeout": 60,
    # "global_delay_factor":0,
    # "fast_cli": False,
}

conn = Netmiko(**dev_info)
print("机器名:", conn.base_prompt)
print("登录成功", dev_info["ip"])
cmds = ['sys', 'vlan 11', 'description  10.10.10.13 32', 'quit', 'quit', 'save', 'y', '', 'y']


for cmd in cmds:
    print("cmd=",cmd)
    output = conn.send_command_timing(cmd)
    print("output=",output)

'''
cmds = ['','vlan 11', 'description  10.10.10.13 32', ]

output = conn.send_config_set(config_commands=cmds)
conn.save_config()

print(output)
'''


'''
with ConnectHandler(**dev_info) as conn:
    output = conn.send_command("display lldp neighbor verbose",delay_factor=5)#display lldp neighbor verbose
    print("output=",output)

'''

'''
        f = open("/Users/congxingwang/pythoncode/NetOpsNornir/ntc_templates/get_device_types.textfsm")
    template = TextFSM(f)
    jsonResult = template.ParseText(cliText)
    '''

'''
from ntc_templates.parse import parse_output

vlan_output = (
    "VLAN Name                             Status    Ports\n"
    "---- -------------------------------- --------- -------------------------------\n"
    "1    default                          active    Gi0/1\n"
    "10   Management                       active    \n"
    "50   VLan50                           active    Fa0/1, Fa0/2, Fa0/3, Fa0/4, Fa0/5,\n"
    "                                                Fa0/6, Fa0/7, Fa0/8\n"
)
vlan_parsed = parse_output(platform="cisco_ios", command="show vlan", data=vlan_output)
print(vlan_parsed)

'''
