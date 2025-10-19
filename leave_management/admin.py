from django.contrib import admin
from .models import LeaveType, LeaveRequest


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_days_per_year', 'is_paid', 'requires_approval', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_paid', 'requires_approval', 'created_at')
    ordering = ('name',)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'status', 'created_at')
    list_filter = ('status', 'leave_type', 'start_date', 'created_at')
    search_fields = ('employee__employee_id', 'employee__user__first_name', 'employee__user__last_name', 'reason')
    date_hierarchy = 'start_date'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'approval_date')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'start_date', 'end_date', 'days_requested', 'reason')
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approval_date', 'rejection_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
