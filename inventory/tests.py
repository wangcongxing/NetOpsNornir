from netmiko import ConnectHandler
from textfsm import TextFSM
import site
print(site.getsitepackages())
import os
os.environ["NET_TEXTFSM"] = "/Users/congxingwang/pythoncode/NetOpsNornir/venv/lib/python3.9/site-packages/ntc_templates/templates"

textfsm_ntc_templates = site.getsitepackages()[0] + "/ntc_templates/templates"
if os.path.exists(textfsm_ntc_templates):
    for tfile in os.listdir(textfsm_ntc_templates):
        print("tfile",tfile)


dev_info = {
    "device_type": "hp_comware1",
    "ip": "10.32.1.3",
    "username": "admin",
    "password": "password123456",
    "port": 22
}
try:
    with ConnectHandler(**dev_info) as conn:
        output = conn.send_command("display version")#display lldp neighbor verbose
        print(output)
except Exception as e:
    cliText = e.args[0]
    f = open("/Users/congxingwang/pythoncode/NetOpsNornir/ntc_templates/get_device_types.textfsm")
    template = TextFSM(f)
    jsonResult = template.ParseText(cliText)

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

