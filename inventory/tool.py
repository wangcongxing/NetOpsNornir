from textfsm import TextFSM
import tempfile

output = '''
Chassis ID : * -- -- Nearest nontpmr bridge neighbor
             # -- -- Nearest customer bridge neighbor
             Default -- -- Nearest bridge neighbor
System Name          Local Interface Chassis ID      Port ID
sw1                  GE1/0           7425-8ae3-e836  GigabitEthernet1/0         
sw3                  GE2/0           7425-8ae3-5b88  GigabitEthernet1/0         
--------------------------------------------
 '''

#f = open('show_vlan.textfsm')

f = open(r'show_vlan.textfsm', mode='w+', encoding='UTF-8')
# open()打开一个文件，返回一个文件对象
f.write('Value device_id (\S+)\nValue local_intf (\w+[\/|\d]{3})\nValue remote_inft (\w+[\/|\d]{3})\n\nStart\n  ^System Name          Local Interface Chassis ID      Port ID\n  ^${device_id}\s+${local_intf}\s+\S+\s+${remote_inft} -> Record\n\nEOF')  # 写入文件
f.close()
f = open('show_vlan.textfsm')
template = TextFSM(f)

print(template.ParseText(output))
