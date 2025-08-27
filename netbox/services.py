import os
from .schemas import NetboxWebhook
from dotenv import load_dotenv
from zabbix.api_client import ZabbixAPIClient
from netbox.api_client import NetBoxClient

load_dotenv()

zabbix = ZabbixAPIClient(
    host=os.getenv("ZB_HOST"),
    user=os.getenv("ZB_USER"),
    password=os.getenv("ZB_PASSWORD"),
)
zabbix.connec_to_zabbix()
netbox = NetBoxClient(host=os.getenv("NB_HOST"), token=os.getenv("NB_TOKEN"))


def update_device_info(webhook_data: NetboxWebhook):
    """
    Логика обновления хоста в Zabbix
    """
    print(webhook_data)
    ip_address = (
        str(webhook_data.data.primary_ip4.address).split("/")[0]
        if webhook_data.data.primary_ip4
        else webhook_data.data.custom_fields.get("zabbix_ip")
    )
    try:
        device_type_details = netbox.get_details(webhook_data.data.device_type.url)
        device_type_template = device_type_details["custom_fields"].get(
            "config_template"
        )
        device_type_template_id = zabbix.get_zabbix_template(device_type_template)

        host_info = zabbix.get_host_by_name(webhook_data.data.name)
        interface_id = zabbix.get_interface_id(host_info)

        if host_info:
            zabbix.update_host_by_id(
                host_id=host_info["hostid"],
                new_ip=ip_address,
                new_template_id=device_type_template_id,
                interface_id=interface_id,
            )
    except Exception as e:
        print(f"Error: {e}")
