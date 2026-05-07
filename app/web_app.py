import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from tortoise.contrib.fastapi import register_tortoise

from utils.logger import get_logger
from db import TORTOISE_ORM
from app.models import Device
from app.mqtt_subscriber import MqttSubscriber

logger = get_logger("web")
app = FastAPI(title="Device Registration")

mqtt_subscriber = MqttSubscriber(client_id="webapp-subscriber")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


def get_generate_schemas() -> bool:
    return os.getenv("TORTOISE_GENERATE_SCHEMAS", "true").lower() in ["1", "true", "yes"]


class DeviceCreate(BaseModel):
    name: str = Field(..., title="Nome do dispositivo")
    device_type: str = Field(..., title="Tipo de dispositivo")
    serial_number: str = Field(..., title="Número de série")
    location: str = Field(..., title="Localização")


class DeviceRead(DeviceCreate):
    id: int


@app.on_event("startup")
async def startup_event():
    logger.info("Starting web app and connecting to database")
    mqtt_subscriber.start()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping web app MQTT subscriber")
    mqtt_subscriber.stop()


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/health")
async def health_check():
    try:
        db_ok = await Device.exists()
        return {"status": "ok", "database": "connected" if db_ok else "connected"}
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.post("/api/devices", response_model=DeviceRead)
async def create_device(device: DeviceCreate):
    if not device.name.strip() or not device.device_type.strip():
        raise HTTPException(status_code=400, detail="Nome e tipo são obrigatórios")

    instance = await Device.create(
        name=device.name.strip(),
        device_type=device.device_type.strip(),
        serial_number=device.serial_number.strip(),
        location=device.location.strip(),
    )
    return DeviceRead(
        id=instance.id,
        name=instance.name,
        device_type=instance.device_type,
        serial_number=instance.serial_number,
        location=instance.location,
    )


@app.get("/api/devices", response_model=list[DeviceRead])
async def list_devices():
    devices = await Device.all().order_by("id")
    return [DeviceRead(
        id=device.id,
        name=device.name,
        device_type=device.device_type,
        serial_number=device.serial_number,
        location=device.location,
    ) for device in devices]


@app.get("/api/mqtt/latest")
async def get_latest_mqtt():
    return mqtt_subscriber.latest()


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=get_generate_schemas(),
    add_exception_handlers=True,
)
