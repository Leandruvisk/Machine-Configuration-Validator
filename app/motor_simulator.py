import asyncio
import random
from datetime import datetime
from tortoise import Tortoise
from dotenv import load_dotenv

from utils.logger import get_logger
from db import TORTOISE_ORM
from models import MotorTelemetry

load_dotenv()
logger = get_logger("MotorSimulator")


class MotorSimulator:
    def __init__(self, record_interval: float = 2.0):
        self.record_interval = record_interval
        self.metrics = {
            "rpm": 1500,
            "temperature": 70.0,
            "vibration": 0.8,
            "voltage": 220.0,
            "current": 35.0,
        }
        self.lock = asyncio.Lock()

    async def init_db(self) -> None:
        logger.info("Initializing Tortoise ORM for motor simulator")
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()

    async def close_db(self) -> None:
        logger.info("Closing Tortoise ORM connections")
        await Tortoise.close_connections()

    async def run(self) -> None:
        await self.init_db()
        try:
            tasks = [
                self._simulate_rpm(),
                self._simulate_temperature(),
                self._simulate_vibration(),
                self._simulate_voltage(),
                self._simulate_current(),
                self._record_telemetry(),
            ]
            await asyncio.gather(*tasks)
        finally:
            await self.close_db()

    async def _simulate_rpm(self) -> None:
        while True:
            await asyncio.sleep(0.6)
            rpm = max(0, int(random.gauss(1500, 60)))
            async with self.lock:
                self.metrics["rpm"] = rpm
            logger.debug(f"Updated rpm={rpm}")

    async def _simulate_temperature(self) -> None:
        while True:
            await asyncio.sleep(1.0)
            temperature = max(0.0, random.gauss(70.0, 4.5))
            async with self.lock:
                self.metrics["temperature"] = round(temperature, 2)
            logger.debug(f"Updated temperature={temperature:.2f}")

    async def _simulate_vibration(self) -> None:
        while True:
            await asyncio.sleep(0.8)
            vibration = max(0.0, random.gauss(0.8, 0.18))
            async with self.lock:
                self.metrics["vibration"] = round(vibration, 3)
            logger.debug(f"Updated vibration={vibration:.3f}")

    async def _simulate_voltage(self) -> None:
        while True:
            await asyncio.sleep(1.2)
            voltage = max(0.0, random.gauss(220.0, 3.5))
            async with self.lock:
                self.metrics["voltage"] = round(voltage, 2)
            logger.debug(f"Updated voltage={voltage:.2f}")

    async def _simulate_current(self) -> None:
        while True:
            await asyncio.sleep(1.1)
            current = max(0.0, random.gauss(35.0, 5.0))
            async with self.lock:
                self.metrics["current"] = round(current, 2)
            logger.debug(f"Updated current={current:.2f}")

    async def _record_telemetry(self) -> None:
        while True:
            await asyncio.sleep(self.record_interval)
            async with self.lock:
                payload = dict(self.metrics)

            status = self._compute_status(payload)
            timestamp = datetime.utcnow()

            await MotorTelemetry.create(
                timestamp=timestamp,
                rpm=payload["rpm"],
                temperature=payload["temperature"],
                vibration=payload["vibration"],
                voltage=payload["voltage"],
                current=payload["current"],
                status=status,
            )

            logger.info(
                f"Telemetry saved at {timestamp.isoformat()} - rpm={payload['rpm']} "
                f"temperature={payload['temperature']:.1f}C vibration={payload['vibration']:.3f}"
            )

    def _compute_status(self, payload: dict) -> str:
        if payload["temperature"] > 90 or payload["vibration"] > 1.5:
            return "alarme"
        if payload["rpm"] < 1200 or payload["rpm"] > 2000:
            return "atenção"
        return "normal"
