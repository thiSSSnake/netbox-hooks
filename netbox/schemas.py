from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DeviceStatus(BaseModel):
    """Модель статуса ус-ва"""

    value: str
    label: str


class DeviceSite(BaseModel):
    """Модель для площадки ус-ва"""

    id: int
    url: str
    name: str
    slug: str
    display: str


class DeviceType(BaseModel):
    """Модель типа ус-ва"""

    id: int
    url: str
    manufacturer: Dict[str, Any]
    model: str
    slug: str
    display: str


class DeviceIPAddress(BaseModel):
    """Модель для IP-адреса"""

    id: int
    url: str
    address: str
    display: str


class DeviceData(BaseModel):
    """Основная модель для данных устройства, отправляемых Netbox."""

    id: int
    url: str
    name: str
    # display: str
    status: DeviceStatus
    device_type: DeviceType
    site: Optional[DeviceSite] = None
    # serial: str
    primary_ip4: Optional[DeviceIPAddress] = None
    # comments: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class NetboxWebhook(BaseModel):
    """Модель вебхука Netbox"""

    event: str
    timestamp: datetime
    model: str
    username: str
    request_id: str
    data: DeviceData
    # custom_fields_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
