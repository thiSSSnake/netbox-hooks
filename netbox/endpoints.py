import pprint
from netbox.schemas import *
from fastapi import APIRouter
from netbox.services import update_device, create_device

router = APIRouter()


@router.post("/webhook", status_code=200, tags=["webhooks"])
async def handle_netbox_webhook(webhook_data: NetboxWebhook):
    """
    Эндпоинт для приема вебхуков от Netbox.

    FastAPI автоматически преобразует и проверит JSON-тело запроса
    в соответствии с моделью NetboxWebhook.

    :param webhook_data: Экземпляр NetboxWebhook, содержащий данные от Netbox.
    """
    ip_address = (
        str(webhook_data.data.primary_ip4.address).split("/")[0]
        if webhook_data.data.primary_ip4
        else webhook_data.data.custom_fields.get("zabbix_ip")
    )

    if webhook_data.event == "created":
        # Логика создания хоста в Zabbix
        print(
            f"Event 'created' for device: {webhook_data.data.name}/IP:{ip_address}. Creating host on Zabbix."
        )
        create_device(webhook_data)

    elif webhook_data.event == "updated":
        # Логика обновления хоста в Zabbix
        print(
            f"Event 'updated' for device: {webhook_data.data.name}/IP:{ip_address}. Updating host on Zabbix."
        )
        update_device(webhook_data)

    elif webhook_data.event == "deleted":
        # Логика удаление хоста в Zabbix
        print(
            f"Event 'deleted' for device: {webhook_data.data.name}/IP:{ip_address}.. Deleting host on Zabbox."
        )
        # host = zabbix.get_host_by_name(webhook_data.data.name)
        # return host

    return {"message": "Webhook received successfully"}
