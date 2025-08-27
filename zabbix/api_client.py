import asyncio
from zabbix_utils import ZabbixAPI, APIRequestError, ProcessingError
import ssl


class Utils:
    def obj_iterate(list_of_objects: list):
        """Функция-генератор для поочередного обхода списка хостов Zabbix"""
        for object in list_of_objects:
            yield object


class ZabbixAPIClient(Utils):
    """
    Класс для работы с API Zabbix.
    """

    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password

    def connec_to_zabbix(self):
        """Подключение к Zabbix, Получение экземпляра API Клиента"""
        try:
            ssl_ctx = ssl.create_default_context()
            zabbix = ZabbixAPI(
                url=self.host,
                user=self.user,
                password=self.password,
                ssl_context=ssl_ctx,
            )
            zabbix.login(user=self.user, password=self.password)
            self.zabbix = zabbix
            return zabbix
        except (APIRequestError, ProcessingError) as e:
            raise APIRequestError(f"{e}")

    def get_hosts(self) -> list[dict]:
        """Получение хостов"""
        hosts = self.zabbix.host.get(
            output=["hostid", "host"],
            selectInterfaces=["ip"],
            selectHostGroups="extend",
        )

        return list(hosts)

    def dict(self, hosts: list):
        zabbix_dict = {
            host["host"]: {"ip": host["interfaces"][0]["ip"], "hostid": host["hostid"]}
            for host in self.obj_iterate(hosts)
        }
        return zabbix_dict

    def get_host_by_name(self, device_name: str):
        """Получаем хост из Zabbix по имени"""
        host = self.zabbix.host.get(
            output=["hostid", "host", "name", "status"],
            selectInterfaces=["ip"],
            selectHostGroups="extend",
            filter={"host": device_name},
        )
        if host:
            print(f"Find {device_name} in Zabbix, id: {host['hostid']}")
            return host
        else:
            print(f"Not found {device_name} in Zabbix")
            return False
