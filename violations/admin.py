from django.contrib import admin
from .models import Offender, Violation

@admin.register(Offender)
class OffenderAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "total_violations", "last_violation", "is_repeat_offender")
    search_fields = ("plate_number",)
    list_filter = ("is_repeat_offender",)

@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "violation_type", "date_time", "image_path", "confidence")
    search_fields = ("plate_number__plate_number", "violation_type")
    list_filter = ("violation_type",)
