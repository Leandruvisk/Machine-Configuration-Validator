import psutil
from typing import Dict, Any
from utils.logger import get_logger

class DiskValidator:
    """Validate disk configuration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    def validate(self) -> Dict[str, Any]:
        """Validate disk configuration"""
        try:
            self.logger.info("Validating disk configuration")

            # Check total disk space
            disk_usage = psutil.disk_usage('/')
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)

            min_free_gb = self.config.get('min_free_gb', 10)

            if free_gb < min_free_gb:
                return {
                    'status': 'fail',
                    'message': f'Insufficient free disk space: {free_gb:.1f}GB < {min_free_gb}GB required'
                }

            # Check partitions if specified
            partitions = self.config.get('partitions', [])
            for partition in partitions:
                mount_point = partition.get('mount_point')
                min_free = partition.get('min_free_gb', 0)

                if mount_point:
                    try:
                        usage = psutil.disk_usage(mount_point)
                        part_free_gb = usage.free / (1024**3)

                        if part_free_gb < min_free:
                            return {
                                'status': 'fail',
                                'message': f'Insufficient free space on {mount_point}: {part_free_gb:.1f}GB < {min_free}GB required'
                            }
                    except Exception as e:
                        self.logger.warning(f"Could not check partition {mount_point}: {e}")

            return {
                'status': 'pass',
                'message': f'Disk validation passed. Total: {total_gb:.1f}GB, Free: {free_gb:.1f}GB'
            }

        except Exception as e:
            self.logger.error(f"Disk validation error: {e}")
            return {
                'status': 'error',
                'message': f'Disk validation failed: {str(e)}'
            }