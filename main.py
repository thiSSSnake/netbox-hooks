from typing import Union
from netbox.middleware import add_process_time_header
from netbox.endpoints import router as WebhookRouter
from fastapi import FastAPI

app = FastAPI()

app.include_router(WebhookRouter)
app.middleware("http")(add_process_time_header)
