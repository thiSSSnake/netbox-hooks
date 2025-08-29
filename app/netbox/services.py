import os

from .schemas import NetboxWebhook
from dotenv import load_dotenv
from app.zabbix.api_client import ZabbixAPIClient
from app.netbox.api_client import NetBoxClient

load_dotenv()

zabbix = ZabbixAPIClient(
    host=os.getenv("ZB_HOST"),
    user=os.getenv("ZB_USER"),
    password=os.getenv("ZB_PASSWORD"),
)
zabbix.connec_to_zabbix()
netbox = NetBoxClient(host=os.getenv("NB_HOST"), token=os.getenv("NB_TOKEN"))


def get_ip_address(webhook_data: NetboxWebhook):
    """
    Получение IP Адреса устройства

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    ip_address = (
        str(webhook_data.data.primary_ip4.address).split("/")[0]
        if webhook_data.data.primary_ip4
        else webhook_data.data.custom_fields.get("zabbix_ip")
    )
    return ip_address


def normalize_url(url: str) -> str:
    """
    Нормализация url для доступа к api методу.
    Возвращает относительный путь, начиная с "/api/".
    """
    api_path_start = url.find("/api/")
    if api_path_start != -1:
        return url[api_path_start:]
    return ""


def get_parent_region(region: dict) -> list[str]:
    """
    Получение списка регионов устройства
    Начиная от родительского - заканчивая дочерним.

    :param region: Словарь с детальной информацией о последнем дочернем регионе устройства.
    """
    if region is None:
        return []

    parent = region.get("parent")
    if parent and "url" in parent:
        region_url = normalize_url(parent["url"])
        parent_region = netbox.get_details(region_url)
        regions = get_parent_region(parent_region)
    else:
        regions = []

    regions.append(region.get("slug"))
    return regions


def get_region_info(site_data: dict) -> list:
    """
    Получение информации о
    первом дочернем регионе
    для далнейшей обработки.

    :param site_data: Словарь детальных данных площадки устройства.
    """
    region_url = normalize_url(site_data["region"].get("url"))
    region_info = netbox.get_details(region_url)
    regions = get_parent_region(region_info)
    return regions


def get_site_info(webhook_data: NetboxWebhook):
    """
    Получение названия хост-группы, на основе регионов устройства.
    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    site_url = webhook_data.data.site.url
    site_info = netbox.get_details(url=site_url)
    return site_info


def get_hostgroup_name(webhook_data: NetboxWebhook):
    """
    Получение названия хост-группы устройства,
    которое составляется из всех регионов в иерархии устройства.

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    site_info = get_site_info(webhook_data)
    regions = get_region_info(site_data=site_info)
    return regions
    # return "-".join(regions[:-1])


def get_template_id(webhook_data: NetboxWebhook):
    """
    Получение ID шаблона настройки устройства в Zabbix.

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    device_type_details = netbox.get_details(webhook_data.data.device_type.url)
    device_type_template = device_type_details["custom_fields"].get("config_template")
    device_type_template_id = zabbix.get_zabbix_template(device_type_template)
    return device_type_template_id


def get_device_status(webhook_data: NetboxWebhook):
    """
    Получение статуса устройства.

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    device_status = 0 if webhook_data.data.status.value == "active" else 1
    return device_status


def get_device_name(webhook_data: NetboxWebhook):
    """
    Получение имени устройства.

    :param webhook_data: Экземлпяр NetboxWebhook, содержащий данный от Netbox.
    """
    device_name = webhook_data.data.name
    return device_name


def get_or_create_hostgroup(webhook_data: NetboxWebhook):
    """
    Логика получения либо создания хост-группы

    :param webhook_data: Экземлпяр NetboxWebhook, содержащий данный от Netbox.
    """
    hostgroup_names = get_hostgroup_name(webhook_data)
    hostgroup_ids = []
    for hostgroup_name in hostgroup_names:
        hostgroup_ids.append(
            zabbix.get_hostgroup(hostgroup_name)
            if zabbix.get_hostgroup(hostgroup_name)
            else zabbix.create_hostgroup(hostgroup_name)
        )
    print(hostgroup_ids)
    return hostgroup_ids


def create_device(webhook_data: NetboxWebhook):
    """
    Логика добавления хоста в Zabbix

    :param webhook_data: Экземлпяр NetboxWebhook, содержащий данный от Netbox.
    """
    url = webhook_data.data.url
    ip_address = get_ip_address(webhook_data)
    device_name = get_device_name(webhook_data)
    status = get_device_status(webhook_data)
    hostgroup_ids = get_or_create_hostgroup(webhook_data)
    template_id = get_template_id(webhook_data)
    try:
        hostid = zabbix.create_host(
            name=device_name,
            status=status,
            template_id=template_id,
            ip=ip_address,
            hostgroup_ids=hostgroup_ids,
        )

        netbox.set_custom_fields(url=url, custom_fields={"zabbix_hostid": hostid})
    except Exception as e:
        print(f"Error: {e}")


def update_device(webhook_data: NetboxWebhook):
    """
    Логика обновления хоста в Zabbix

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    try:
        ip_address = get_ip_address(webhook_data)
        template_id = get_template_id(webhook_data)
        status = get_device_status(webhook_data)
        device_name = get_device_name(webhook_data)
        host_info = zabbix.get_host_by_hostid(
            webhook_data.data.custom_fields.get("zabbix_hostid")
        )
        hostgroup_ids = get_or_create_hostgroup(webhook_data)

        if host_info:
            interface_id = zabbix.get_interface_id(host_info)
            zabbix.update_host_by_id(
                host_id=host_info["hostid"],
                new_ip=ip_address,
                new_template_id=template_id,
                interface_id=interface_id,
                status=status,
                name=device_name,
                hostgroup_ids=hostgroup_ids,
            )
    except Exception as e:
        print(f"Error: {e}")


def delete_device(webhook_data: NetboxWebhook):
    """
    Удаление устройства в Zabbix

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    host_info = zabbix.get_host_by_hostid(
        webhook_data.data.custom_fields.get("zabbix_hostid")
    )
    if host_info:
        host_id = host_info["hostid"]
        zabbix.delete_host_by_id(host_id=host_id)
