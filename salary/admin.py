from django.contrib import admin
from .models import SalaryRecord


@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'base_salary', 'total_salary', 'is_paid', 'payment_date', 'created_at')
    list_filter = ('is_paid', 'month', 'year', 'payment_date')
    search_fields = ('employee__employee_id', 'employee__user__first_name', 'employee__user__last_name')
    date_hierarchy = 'payment_date'
    ordering = ('-year', '-month', 'employee')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Period', {
            'fields': ('month', 'year')
        }),
        ('Salary Components', {
            'fields': ('base_salary', 'bonuses', 'deductions', 'total_salary')
        }),
        ('Attendance', {
            'fields': ('days_worked', 'days_absent', 'days_leave')
        }),
        ('Payment', {
            'fields': ('is_paid', 'payment_date', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
