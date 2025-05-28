from django.db import models

class Offender(models.Model):
    plate_number = models.CharField(max_length=32, primary_key=True)
    total_violations = models.IntegerField(default=1)
    last_violation = models.DateTimeField(null=True, blank=True)
    is_repeat_offender = models.BooleanField(default=False)

    def __str__(self):
        return self.plate_number

class Violation(models.Model):
    plate_number = models.ForeignKey(Offender, on_delete=models.CASCADE, to_field='plate_number')
    violation_type = models.CharField(max_length=64)
    date_time = models.DateTimeField(auto_now_add=True)
    image_path = models.CharField(max_length=256, blank=True, null=True)
    confidence = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.plate_number} - {self.violation_type} - {self.date_time}"
