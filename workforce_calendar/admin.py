from django.contrib import admin
from .models import WorkforceEvent


@admin.register(WorkforceEvent)
class WorkforceEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_date', 'end_date', 'is_all_day', 'created_by', 'created_at')
    list_filter = ('event_type', 'is_all_day', 'start_date', 'created_at')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('employees',)
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'event_type')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date', 'is_all_day')
        }),
        ('Location & Participants', {
            'fields': ('location', 'employees')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
