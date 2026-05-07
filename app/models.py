from tortoise import fields, models


class ValidationResult(models.Model):
    id = fields.IntField(pk=True)
    validator_name = fields.CharField(max_length=128)
    status = fields.CharField(max_length=32)
    message = fields.TextField(null=True)
    run_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "validation_results"

    def __str__(self) -> str:
        return f"{self.validator_name} - {self.status}"


class MotorTelemetry(models.Model):
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField()
    rpm = fields.IntField()
    temperature = fields.FloatField()
    vibration = fields.FloatField()
    voltage = fields.FloatField()
    current = fields.FloatField()
    status = fields.CharField(max_length=32)

    class Meta:
        table = "motor_telemetry"

    def __str__(self) -> str:
        return f"Telemetry {self.timestamp.isoformat()} - {self.status}"


class Device(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    device_type = fields.CharField(max_length=128)
    serial_number = fields.CharField(max_length=128, null=True)
    location = fields.CharField(max_length=128, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "devices"

    def __str__(self) -> str:
        return f"Device {self.name} [{self.device_type}]"
