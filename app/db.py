import asyncio
import os
from tortoise import Tortoise
from utils.logger import get_logger

logger = get_logger("db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgres://validator:validator@db:5432/validator"
)

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
}


async def init_db(retries: int = 10, delay: int = 3) -> None:
    logger.info("Initializing database connection")

    generate_schemas = os.getenv("TORTOISE_GENERATE_SCHEMAS", "true").lower() in ["1", "true", "yes"]

    for attempt in range(1, retries + 1):
        try:
            await Tortoise.init(config=TORTOISE_ORM)
            if generate_schemas:
                await Tortoise.generate_schemas()
            logger.info("Database initialized successfully")
            return
        except Exception as exc:
            logger.warning(
                f"Database connection attempt {attempt}/{retries} failed: {exc}"
            )
            if attempt == retries:
                raise
            await asyncio.sleep(delay)


async def close_db() -> None:
    logger.info("Closing database connection")
    await Tortoise.close_connections()
