import asyncio
from copy import copy
from typing import Dict
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

    def get_host_by_hostid(self, hostid: str):
        """
        Получаем хост из Zabbix по его hostid
        """
        host = self.zabbix.host.get(
            output=["hostid", "host", "name", "status"],
            selectInterfaces="extend",
            selectHostGroups="extend",
            filter={"hostid": hostid},
        )
        if host:
            print(f"Find device in Zabbix, id: {host[0]['hostid']}")
            return host[0]
        else:
            print(f"Not found device with hostid:{hostid} in Zabbix")
            return None

    def get_interface_id(self, host: Dict):
        """Получение Id существующего интерфейса"""
        if host.get("interfaces"):
            interface_id = host["interfaces"][0]["interfaceid"]
        return interface_id

    def get_zabbix_template(self, template_name: str):
        """Получение id шаблона ус-ва Zabbix"""
        template = self.zabbix.template.get(filter={"name": template_name})
        template_id = template[0]["templateid"]
        return template_id

    def get_hostgroup(self, name: str):
        """
        Получение ID хост-группы.
        """
        try:
            response = self.zabbix.hostgroup.get(filter={"name": name})
            if response:
                return [{"groupid": response[0]["groupid"]}]
            else:
                return False
        except (APIRequestError, ProcessingError) as e:
            raise Exception(f"Failed to fetch Zabbix hostgroup: {e}")

    def create_hostgroup(self, name: str):
        """
        Создание новой хост-группы
        """
        try:
            response = self.zabbix.hostgroup.create(name=name)
            print(
                f"Successfully created Zabbix hostgroup with id {response['groupids'][0]}"
            )
            return [{"groupid": response["groupids"][0]}]
        except (APIRequestError, ProcessingError) as e:
            raise Exception(f"Failed to create Zabbix hostgroup: {e}")

    def create_host(
        self,
        name: str,
        status: int,
        template_id: str,
        ip: str,
        hostgroup_id: list,
    ):
        """Создание хоста в Zabbix"""
        try:
            response = self.zabbix.host.create(
                host=name,
                status=status,
                groups=hostgroup_id,
                interfaces=[
                    {
                        "type": 2,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "161",
                        "details": {
                            "version": 2,
                            "community": "public",
                        },
                    }
                ],
                templates=[{"templateid": template_id}],
            )
            print(f"Successfully created Zabbix host with id {response}")
            return response["hostids"][0]
        except (APIRequestError, ProcessingError) as e:
            raise Exception(f"Failed to create Zabbix host: {e}")

    def update_host_by_id(
        self,
        host_id: str,
        new_ip: str,
        new_template_id: str,
        interface_id: str,
        status: int,
        name: str,
        hostgroup_id: list,
    ):
        """Обновление хоста по hostid"""
        try:
            self.zabbix.host.update(
                hostid=host_id,
                status=status,
                name=name,
                groups=hostgroup_id,
                interfaces=[
                    {
                        "interfaceid": interface_id,
                        "type": 2,
                        "main": 1,
                        "useip": 1,
                        "ip": new_ip,
                        "dns": "",
                        "port": "161",
                        "details": {
                            "version": 2,
                            "community": "public",
                        },
                    }
                ],
                templates=[{"templateid": new_template_id}],
            )
            print(f"Successfully updated Zabbix host with id {host_id}")
        except (APIRequestError, ProcessingError) as e:
            raise Exception(f"Failed to update Zabbix host: {e}")
