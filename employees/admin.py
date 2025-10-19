from django.contrib import admin
from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'phone_number', 'department', 'role', 'is_active', 'date_joined')
    list_filter = ('department', 'role', 'is_active', 'date_joined')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email', 'phone_number')
    readonly_fields = ('employee_id', 'date_joined', 'updated_at')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'user', 'date_of_birth', 'phone_number', 'address', 'emergency_contact')
        }),
        ('Employment Details', {
            'fields': ('department', 'role', 'date_joined', 'salary_base', 'floor_number', 'cabin_number', 'is_active')
        }),
        ('Face Recognition', {
            'fields': ('face_image', 'face_encoding'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
