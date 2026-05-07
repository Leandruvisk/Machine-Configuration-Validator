import psutil
from typing import Dict, Any
from utils.logger import get_logger

class MemoryValidator:
    """Validate memory configuration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    def validate(self) -> Dict[str, Any]:
        """Validate memory configuration"""
        try:
            self.logger.info("Validating memory configuration")

            # Get memory information
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)

            min_gb = self.config.get('min_gb', 1)

            # Check total memory
            if total_gb < min_gb:
                return {
                    'status': 'fail',
                    'message': f'Insufficient memory: {total_gb:.1f}GB < {min_gb}GB required'
                }

            return {
                'status': 'pass',
                'message': f'Memory validation passed. Total: {total_gb:.1f}GB, Available: {available_gb:.1f}GB'
            }

        except Exception as e:
            self.logger.error(f"Memory validation error: {e}")
            return {
                'status': 'error',
                'message': f'Memory validation failed: {str(e)}'
            }