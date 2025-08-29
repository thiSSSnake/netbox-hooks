from typing import Any, Dict
import requests


class NetBoxClient:
    def __init__(self, host: str, token: str):
        self.host = host
        self.token = token
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Accept": "application/json",
        }

    def get_details(self, url: str):
        """Получение детальной информации об объекте по id"""
        try:
            response = requests.get(f"{self.host}/{url}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"{e}")

    def set_custom_fields(self, url: str, custom_fields: Dict[str, Any]):
        """Установление hostid из zabbix"""
        try:
            payload = {"custom_fields": custom_fields}
            response = requests.patch(
                url=f"{self.host}{url}", headers=self.headers, json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"{e}")
