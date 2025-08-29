from app.netbox.middleware import add_process_time_header
from app.netbox.endpoints import router as WebhookRouter
from fastapi import FastAPI

app = FastAPI()

app.include_router(WebhookRouter)
app.middleware("http")(add_process_time_header)
