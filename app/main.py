#!/usr/bin/env python3
"""
Machine Configuration Validator
Valida configurações de máquinas industriais
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validators.cpu_validator import CPUValidator
from validators.memory_validator import MemoryValidator
from validators.disk_validator import DiskValidator
from validators.network_validator import NetworkValidator
from validators.services_validator import ServicesValidator

import asyncio

from utils.logger import get_logger
from utils.config_loader import ConfigLoader
from db import init_db, close_db
from models import ValidationResult
from mqtt_client import MqttClient

logger = get_logger()

def run_validations(expected_config):
    validators = [
        CPUValidator(expected_config.get('cpu', {})),
        MemoryValidator(expected_config.get('memory', {})),
        DiskValidator(expected_config.get('disk', {})),
        NetworkValidator(expected_config.get('network', {})),
        ServicesValidator(expected_config.get('services', {})),
    ]

    results = {}
    for validator in validators:
        try:
            result = validator.validate()
            results[validator.__class__.__name__] = result
            logger.info(f"{validator.__class__.__name__}: {'PASS' if result['status'] == 'pass' else 'FAIL'}")
        except Exception as e:
            logger.error(f"Error in {validator.__class__.__name__}: {str(e)}")
            results[validator.__class__.__name__] = {'status': 'error', 'message': str(e)}

    return results


async def main():
    logger = get_logger()
    logger.info("Starting Machine Configuration Validator")

    mqtt = MqttClient(client_id="validator-backend")
    await init_db()
    try:
        config_loader = ConfigLoader()
        expected_config = config_loader.load_config()
        validation_interval = float(os.getenv("VALIDATION_INTERVAL", "10"))

        while True:
            results = run_validations(expected_config)
            await save_results(results)
            generate_report(results)

            mqtt.publish(
                "backend/validation",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "results": results,
                },
            )
            logger.info("Published validation results to MQTT")
            await asyncio.sleep(validation_interval)
    finally:
        await close_db()
        mqtt.disconnect()


async def save_results(results):
    for validator_name, result in results.items():
        await ValidationResult.create(
            validator_name=validator_name,
            status=result.get('status', 'unknown'),
            message=result.get('message', ''),
        )


def generate_report(results):
    """Generate validation report"""
    report_path = Path(os.getenv('REPORTS_DIR', './reports')) / 'validation_report.txt'

    with open(report_path, 'w') as f:
        f.write("Machine Configuration Validation Report\n")
        f.write("=" * 50 + "\n\n")

        for validator_name, result in results.items():
            f.write(f"{validator_name}:\n")
            f.write(f"  Status: {result.get('status', 'unknown')}\n")
            if 'message' in result:
                f.write(f"  Message: {result['message']}\n")
            f.write("\n")

    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())