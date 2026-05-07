import yaml
import os
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Load configuration from YAML file"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.getenv('CONFIG_FILE', './configs/expected_config.yaml')
        self.config_path = Path(config_path)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")