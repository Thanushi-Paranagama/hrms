from django.contrib import admin
from .models import Recruitment


@admin.register(Recruitment)
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'position_applied', 'department', 'status', 'interview_date', 'created_at')
    list_filter = ('status', 'department', 'interview_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'position_applied')
    date_hierarchy = 'interview_date'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Candidate Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'resume', 'cover_letter')
        }),
        ('Position Details', {
            'fields': ('position_applied', 'department')
        }),
        ('Recruitment Process', {
            'fields': ('status', 'interview_date', 'notes')
        }),
        ('Hiring', {
            'fields': ('employee', 'hired_date'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Candidate Name'
