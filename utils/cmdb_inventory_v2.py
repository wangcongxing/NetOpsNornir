import logging
import pathlib
from typing import Any, Dict, Type, List

from nornir.core.inventory import (
    Inventory,
    Group,
    Groups,
    Host,
    Hosts,
    Defaults,
    ConnectionOptions,
    HostOrGroup,
    ParentGroups,
)


def _get_connection_options(data: Dict[str, Any]) -> Dict[str, ConnectionOptions]:
    cp = {}
    for cn, c in data.items():
        cp[cn] = ConnectionOptions(
            hostname=c.get("hostname"),
            port=c.get("port"),
            username=c.get("username"),
            password=c.get("password"),
            platform=c.get("platform"),
            extras=c.get("extras"),
        )
    return cp


def _get_defaults(data: Dict[str, Any]) -> Defaults:
    return Defaults(
        hostname=data.get("hostname"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        connection_options=_get_connection_options(data.get("connection_options", {})),
    )


def _get_inventory_element(
        typ: Type[HostOrGroup], data: Dict[str, Any], name: str, defaults: Defaults
) -> HostOrGroup:
    return typ(
        name=name,
        hostname=data.get("hostname") or data.get("ip"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        groups=data.get(
            "groups"
        ),  # this is a hack, we will convert it later to the correct type
        defaults=defaults,
        connection_options=_get_connection_options(data.get("connection_options", {})),
    )


class CMDBInventory:
    def __init__(
            self,
            devices: List[dict],
    ) -> None:
        """
        根据devices的字典列表加载所有网络主机
        Args:

          devices: 网络设备信息字典的列表，形如 [
                    {'ip': '192.168.1.1',
                    'username': 'admin',
                    'password': '1!',
                    'port': 8181,
                    platform': 'cisco_nxos',
                    'vendor':'cisco',
                    'region': '北京XX园区'
                    }
            ]
        """
        # 将host_info中的字段的数据保留，其他的都放到整形后的dict数据的data字段中去。
        host_info = ['hostname', 'username', 'password', 'port', 'platform', 'ip', 'secret', 'device_type']
        # 对数据进行整形，将整形的数据放到reshape_devices中去。
        reshape_devices = []
        for device in devices:
            # 初始化一个整形后的数据
            reshape_device = {
                'data': {}
            }
            for k, v in device.items():
                # 数据在host_info中，则保留，对platform做一下处理，netmiko中是device_type，所以兼容了一下这个字段，将其转为platform
                if k in host_info:
                    if k == 'device_type':
                        reshape_device['platform'] = v
                    else:
                        reshape_device[k] = v
                # 数据不在host_info中，则放到data中去
                else:
                    reshape_device['data'][k] = v
            reshape_devices.append(reshape_device)
        # 完成初始化，self.deivces后续构建inventory对象
        self.deivces = reshape_devices

    def load(self) -> Inventory:
        # 初始化三个对象，分别是Hosts、Groups和Defaults的实例
        hosts = Hosts()
        groups = Groups()
        defaults = Defaults()
        # 我们本例只使用了hosts，大家如果真有需要，按需去添加其他两个对象的属性
        # 从原生的inventory我们实际能看出，inventory的hosts是一个类似dict的对象，所以我们通过dict的方式构建或添加设备。
        # 所以我们将原有的列表进行了一层转化，用ip作为每个host的name，在这段就是用ip作为字典的key值，value是之前构建的字典
        hosts_dict = {i['ip']: i for i in self.deivces}
        # 以上这行代码等于以下三行代码
        # hosts_dict = {}
        # for i in self.deivces:
        #     hosts_dict[i['ip']] = i

        # 我们准备好了添加网络设备的字典，然后在hosts中添加每个
        for name, host_dict in hosts_dict.items():
            hosts[name] = _get_inventory_element(Host, host_dict, name, defaults)
        return Inventory(hosts=hosts, groups=groups, defaults=defaults)