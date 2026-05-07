import subprocess
import os
from typing import Dict, Any
from utils.logger import get_logger

class ServicesValidator:
    """Validate system services"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    def validate(self) -> Dict[str, Any]:
        """Validate system services"""
        try:
            self.logger.info("Validating system services")

            required_services = self.config.get('required', [])
            optional_services = self.config.get('optional', [])

            missing_required = []

            # Check required services
            for service in required_services:
                if not self._is_service_running(service):
                    missing_required.append(service)

            if missing_required:
                return {
                    'status': 'fail',
                    'message': f'Required services not running: {", ".join(missing_required)}'
                }

            # Check optional services (just log)
            for service in optional_services:
                if not self._is_service_running(service):
                    self.logger.warning(f"Optional service {service} is not running")

            return {
                'status': 'pass',
                'message': 'Services validation passed'
            }

        except Exception as e:
            self.logger.error(f"Services validation error: {e}")
            return {
                'status': 'error',
                'message': f'Services validation failed: {str(e)}'
            }

    def _is_service_running(self, service_name: str) -> bool:
        """Check if a service is running"""
        try:
            # Try systemctl first (systemd)
            result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip() == 'active':
                return True

            # Try service command (SysV init)
            result = subprocess.run(
                ['service', service_name, 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True

            # Try pgrep for process-based check
            result = subprocess.run(
                ['pgrep', '-f', service_name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: check if process exists
            try:
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return service_name in result.stdout
            except:
                return False