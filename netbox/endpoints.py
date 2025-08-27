import os
from dotenv import load_dotenv
from netbox.api_client import NetBoxClient
from netbox.schemas import *
from zabbix.api_client import ZabbixAPIClient
from fastapi import APIRouter

load_dotenv()
router = APIRouter()


@router.post("/webhook", status_code=200, tags=["webhooks"])
async def handle_netbox_webhook(webhook_data: NetboxWebhook):
    """
    Эндпоинт для приема вебхуков от Netbox.

    FastAPI автоматически преобразует и проверит JSON-тело запроса
    в соответствии с моделью NetboxWebhook.

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    # print(
    #     f"Received webhook from NetBox. Event: {webhook_data.event}, Device: {webhook_data.data.name}, Data: {webhook_data}"
    # )
    ip_address = (
        str(webhook_data.data.primary_ip4.address).split("/")[0]
        if webhook_data.data.primary_ip4
        else webhook_data.data.custom_fields.get("zabbix_ip")
    )
    zabbix = ZabbixAPIClient(
        host=os.getenv("ZB_HOST"),
        user=os.getenv("ZB_USER"),
        password=os.getenv("ZB_PASSWORD"),
    )
    netbox = NetBoxClient(host=os.getenv("NB_HOST"), token=os.getenv("NB_TOKEN"))
    zabbix.connec_to_zabbix()

    if webhook_data.event == "created":
        # Логика создания хоста в Zabbix
        print(
            f"Event 'created' for device: {webhook_data.data.name}/IP:{ip_address}. Creating host on Zabbix."
        )
        host = zabbix.get_host_by_name(webhook_data.data.name)
        return host

    elif webhook_data.event == "updated":
        # Логика обновления хоста в Zabbix
        print(
            f"Event 'updated' for device: {webhook_data.data.name}/IP:{ip_address}. Updating host on Zabbix."
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
            raise Exception(f"{e}")

    elif webhook_data.event == "deleted":
        # Логика удаление хоста в Zabbix
        print(
            f"Event 'deleted' for device: {webhook_data.data.name}/IP:{ip_address}.. Deleting host on Zabbox."
        )
        host = zabbix.get_host_by_name(webhook_data.data.name)
        return host

    return {"message": "Webhook received successfully"}
