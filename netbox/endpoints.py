import os
from dotenv import load_dotenv
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
    print(
        f"Received webhook from NetBox. Event: {webhook_data.event}, Device: {webhook_data.data.name}, Data: {webhook_data}"
    )
    ip_address = (
        webhook_data.data.primary_ip4.address
        if webhook_data.data.primary_ip4
        else webhook_data.data.custom_fields.get("zabbix_ip")
    )
    zabbix = ZabbixAPIClient(
        host=os.getenv("ZB_HOST"),
        user=os.getenv("ZB_USER"),
        password=os.getenv("ZB_PASSWORD"),
    )
    await zabbix.connec_to_zabbix()

    if webhook_data.event == "created":
        # Логика создания хоста в Zabbix
        print(
            f"Event 'created' for device: {webhook_data.data.name}/IP:{ip_address}. Creating host on Zabbix."
        )
        host = await zabbix.get_host_by_name(webhook_data.data.name)
        return host

    elif webhook_data.event == "updated":
        # Логика обновления хоста в Zabbix
        print(
            f"Event 'updated' for device: {webhook_data.data.name}/IP:{ip_address}.. Updating host on Zabbix."
        )
        host = await zabbix.get_host_by_name(webhook_data.data.name)
        return host

    elif webhook_data.event == "deleted":
        # Логика удаление хоста в Zabbix
        print(
            f"Event 'deleted' for device: {webhook_data.data.name}/IP:{ip_address}.. Deleting host on Zabbox."
        )
        host = await zabbix.get_host_by_name(webhook_data.data.name)
        return host

    return {"message": "Webhook received successfully"}
