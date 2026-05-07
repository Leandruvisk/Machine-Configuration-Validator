import json
import os
from typing import Any

from paho.mqtt import client as mqtt
from utils.logger import get_logger

logger = get_logger("mqtt")


class MqttClient:
    def __init__(self, client_id: str = "machine-validator"):
        self.host = os.getenv("MQTT_HOST", "mosquitto")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.topic_prefix = os.getenv("MQTT_TOPIC_PREFIX", "")

        self.client = mqtt.Client(client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_log = self._on_log

        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        if username:
            self.client.username_pw_set(username, password)

        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()
        except Exception as exc:
            logger.warning(f"Unable to connect to MQTT broker at {self.host}:{self.port}: {exc}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")
        else:
            logger.warning(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        logger.info("Disconnected from MQTT broker")

    def _on_log(self, client, userdata, level, buf):
        logger.debug(f"MQTT log: {buf}")

    def _qualify_topic(self, topic: str) -> str:
        if self.topic_prefix:
            return f"{self.topic_prefix}/{topic}".strip("/")
        return topic

    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False):
        topic_name = self._qualify_topic(topic)
        payload_json = json.dumps(payload, default=str)
        logger.debug(f"Publishing MQTT message to {topic_name}: {payload_json}")
        result = self.client.publish(topic_name, payload_json, qos=qos, retain=retain)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.warning(f"Failed to publish MQTT message: {result}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
