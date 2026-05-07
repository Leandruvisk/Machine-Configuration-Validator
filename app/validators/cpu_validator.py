import psutil
from typing import Dict, Any
from utils.logger import get_logger

class CPUValidator:
    """Validate CPU configuration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    def validate(self) -> Dict[str, Any]:
        """Validate CPU configuration"""
        try:
            self.logger.info("Validating CPU configuration")

            # Get CPU information
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()

            min_cores = self.config.get('min_cores', 1)
            min_frequency_ghz = self.config.get('min_frequency_ghz', 1.0)

            # Check core count
            if cpu_count < min_cores:
                return {
                    'status': 'fail',
                    'message': f'Insufficient CPU cores: {cpu_count} < {min_cores} required'
                }

            # Check frequency if available
            if cpu_freq and cpu_freq.current:
                current_freq_ghz = cpu_freq.current / 1000.0
                if current_freq_ghz < min_frequency_ghz:
                    return {
                        'status': 'fail',
                        'message': f'CPU frequency too low: {current_freq_ghz:.1f}GHz < {min_frequency_ghz}GHz required'
                    }

            return {
                'status': 'pass',
                'message': f'CPU validation passed. Cores: {cpu_count} ({cpu_count_physical} physical), Freq: {current_freq_ghz:.1f}GHz'
            }

        except Exception as e:
            self.logger.error(f"CPU validation error: {e}")
            return {
                'status': 'error',
                'message': f'CPU validation failed: {str(e)}'
            }