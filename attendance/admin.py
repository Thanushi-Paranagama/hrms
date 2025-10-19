from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status', 'hours_worked', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('employee__employee_id', 'employee__first_name', 'employee__last_name', 'notes')
    date_hierarchy = 'date'
    ordering = ('-date', '-check_in')
    readonly_fields = ('created_at', 'updated_at', 'hours_worked')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Attendance Details', {
            'fields': ('date', 'check_in', 'check_out', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'attendance_image', 'hours_worked')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def hours_worked(self, obj):
        hours = obj.get_hours_worked()
        if hours is not None:
            return f"{hours:.2f} hours"
        return "N/A"
    hours_worked.short_description = 'Hours Worked'
