from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command
import pandas

# 加载config，创建一个nornir对象
nr = InitNornir(config_file="config.yaml")

outputs = []
sn_tables = []


def show_cmds(task):
    # Task类通过host属性，读取yaml配置，获取其中设备信息
    cmds = task.host.data['cmds']

    for cmd in cmds:
        # print(cmd)
        # Task类调用run方法，执行任务，如netmiko_send_command、write_file等插件
        result = task.run(netmiko_send_command, command_string=cmd)
        output = result.result
        sn_number = (f'{output}'.replace(' ', '@')).split('@')[-1]
        hostname = f'{task.host.hostname}'
        print(hostname + ' ' + 'SN ' + sn_number)
        outputs.append(output)
        sn_table = [hostname, sn_number]
        sn_tables.append(sn_table)

    return outputs


results = nr.run(task=show_cmds)
print(results)
print_result(results)
columns = ['hostname', 'SN号']
tables = pandas.DataFrame(sn_tables, columns=columns)
namestr = 'host_sn.xlsx'
tables.to_excel(namestr, index=0)
print('{name} created!'.format(name=namestr))
