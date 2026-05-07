import json
import os
import threading
from typing import Any

from paho.mqtt import client as mqtt
from utils.logger import get_logger

logger = get_logger("mqtt-subscriber")


class MqttSubscriber:
    def __init__(self, client_id: str = "web-mqtt-subscriber"):
        self.host = os.getenv("MQTT_HOST", "mosquitto")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.topic_prefix = os.getenv("MQTT_TOPIC_PREFIX", "")
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self._lock = threading.Lock()
        self._latest: dict[str, Any] = {}

    def _qualify_topic(self, topic: str) -> str:
        if self.topic_prefix:
            return f"{self.topic_prefix}/{topic}".strip("/")
        return topic

    def start(self):
        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()
            logger.info(f"MQTT subscriber connecting to {self.host}:{self.port}")
        except Exception as exc:
            logger.warning(f"Unable to connect to MQTT broker: {exc}")

    def stop(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT subscriber disconnected")
        except Exception as exc:
            logger.warning(f"Error disconnecting MQTT subscriber: {exc}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT subscriber connected")
            self.client.subscribe(self._qualify_topic("motor/telemetry"))
            self.client.subscribe(self._qualify_topic("backend/validation"))
        else:
            logger.warning(f"MQTT subscriber connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        logger.info("MQTT subscriber disconnected from broker")

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = payload

        with self._lock:
            self._latest[msg.topic] = {
                "topic": msg.topic,
                "timestamp": data.get("timestamp") if isinstance(data, dict) else None,
                "payload": data,
            }
            logger.debug(f"Received MQTT message on {msg.topic}")

    def latest(self) -> dict[str, Any]:
        with self._lock:
            return {topic: value.copy() for topic, value in self._latest.items()}
