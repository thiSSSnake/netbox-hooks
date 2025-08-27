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

    def get_host_by_name(self, device_name: str):
        """Получаем хост из Zabbix по имени"""
        host = self.zabbix.host.get(
            output=["hostid", "host", "name", "status"],
            selectInterfaces="extend",
            selectHostGroups="extend",
            filter={"host": device_name},
        )
        if host:
            print(f"Find {device_name} in Zabbix, id: {host[0]['hostid']}")
            return host[0]
        else:
            print(f"Not found {device_name} in Zabbix")
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

    # Add new_template_id ?
    def update_host_by_id(
        self,
        new_template_id: str,
        host_id: str,
        new_ip: str,
        interface_id: str,
    ):
        """Обновление хоста по hostid"""
        try:
            self.zabbix.host.update(
                hostid=host_id,
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
