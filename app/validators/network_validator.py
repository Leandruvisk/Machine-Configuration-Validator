import psutil
import subprocess
from typing import Dict, Any
from utils.logger import get_logger

class NetworkValidator:
    """Validate network configuration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    def validate(self) -> Dict[str, Any]:
        """Validate network configuration"""
        try:
            self.logger.info("Validating network configuration")

            interfaces = self.config.get('interfaces', [])

            for interface in interfaces:
                name = interface.get('name')
                required = interface.get('required', False)
                min_speed_mbps = interface.get('min_speed_mbps', 0)

                if name:
                    try:
                        # Check if interface exists
                        net_if_stats = psutil.net_if_stats()
                        if name not in net_if_stats:
                            if required:
                                return {
                                    'status': 'fail',
                                    'message': f'Required network interface {name} not found'
                                }
                            continue

                        # Check interface speed
                        stats = net_if_stats[name]
                        if hasattr(stats, 'speed') and stats.speed:
                            speed_mbps = stats.speed
                            if speed_mbps < min_speed_mbps:
                                return {
                                    'status': 'fail',
                                    'message': f'Network interface {name} speed too low: {speed_mbps}Mbps < {min_speed_mbps}Mbps required'
                                }

                    except Exception as e:
                        self.logger.warning(f"Could not check interface {name}: {e}")
                        if required:
                            return {
                                'status': 'fail',
                                'message': f'Error checking required interface {name}: {str(e)}'
                            }

            return {
                'status': 'pass',
                'message': 'Network validation passed'
            }

        except Exception as e:
            self.logger.error(f"Network validation error: {e}")
            return {
                'status': 'error',
                'message': f'Network validation failed: {str(e)}'
            }