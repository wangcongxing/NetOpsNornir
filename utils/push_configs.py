from nornir import InitNornir
from nornir.core.task import Result
from nornir_netmiko import netmiko_send_config, netmiko_save_config, netmiko_commit
from nornir_utils.plugins.functions import print_result
import netmiko

nornir_devs = InitNornir(config_file="nornir.yaml")


def push_and_save_configs(task):
    # 配置保存 不通的平台不太一样 有的有commit  有的是save
    # config_file = task.host['data'].get('config_file','configs.txt')
    save_type = 'save'
    for group in task.host.groups:
        if group.data.get('save_config_type'):
            save_type = group.data.get('save_config_type')
            break

    config_push_result = task.run(task=netmiko_send_config, config_file='configs.txt')

    if save_type =='save':
        config_save_result = task.run(netmiko_save_config)
    elif save_type == 'commit':
        config_save_result = task.run(netmiko_commit)
    else:
        raise Exception('不支持的save_type')

    if (not config_push_result.failed)  and (not config_save_result.failed):
        return Result(host=task.host,
                      result=f'配置成功推送到设备:{task.host.name}',
                      changed=True,
                      name = '配置推送到设备'
                      )
    else:
        return Result(host=task.host,
                      result=f'设备:{task.host.name}失败',
                      changed=True
                      )

results = nornir_devs.run(task=push_and_save_configs)
print_result(results)
