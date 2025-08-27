from typing import Union
from netbox.endpoints import router as WebhookRouter
from fastapi import FastAPI

app = FastAPI()

app.include_router(WebhookRouter)


@app.get("/")
async def read_root():
    return {"Hello": "world"}
