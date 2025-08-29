import json
import pprint
from typing import Awaitable, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse


async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Проверяем что в данных NetboxWebhook
    Есть поле zabbix_sync = True

    :param request:
    :param call_next:
    """
    if request.url.path == "/webhook" and request.method == "POST":
        try:
            body = await request.json()
            if body["data"]["custom_fields"]["zabbix_sync"] != True:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Поле (zabbix_sync) == False, пропуск"},
                )
        except json.JSONDecodeError:
            return JSONResponse(status=400, content={"detail": "Uncorrect format JSON"})
        except Exception as e:
            return JSONResponse(
                status_code=400, content={"detail": f"Ошибка валидации данных: {e}"}
            )
    respone = await call_next(request)
    return respone
