#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from utils.config_loader import ConfigLoader
from validators.cpu_validator import CPUValidator
from validators.memory_validator import MemoryValidator
from validators.disk_validator import DiskValidator
from validators.network_validator import NetworkValidator
from validators.services_validator import ServicesValidator


def main():
    config_path = os.getenv('CONFIG_FILE', './configs/expected_config.yaml')
    if not Path(config_path).exists():
        raise FileNotFoundError(f'Config file not found: {config_path}')

    config_loader = ConfigLoader(config_path)
    config = config_loader.load_config()

    # Ensure validators can initialize without running full checks
    CPUValidator(config.get('cpu', {}))
    MemoryValidator(config.get('memory', {}))
    DiskValidator(config.get('disk', {}))
    NetworkValidator(config.get('network', {}))
    ServicesValidator(config.get('services', {}))
    print('validator healthy')


if __name__ == '__main__':
    main()
