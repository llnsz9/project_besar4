from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DataEntry, Analysis, AIModel, Visualization, TrainingSession, Workflow, Collaboration, Insight, Dataset

admin.site.register(User, UserAdmin)
admin.site.register(DataEntry)
admin.site.register(Analysis)
admin.site.register(AIModel)
admin.site.register(Visualization)
admin.site.register(TrainingSession)
admin.site.register(Workflow)
admin.site.register(Collaboration)
admin.site.register(Insight)
admin.site.register(Dataset)

from .models import APIKey, IntelligenceSubmission


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_active', 'usage_count', 'last_used_at', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'key']
    readonly_fields = ['key', 'usage_count', 'last_used_at', 'created_at']

    def save_model(self, request, obj, form, change):
        if not obj.key:
            obj.key = APIKey.generate_key()
        super().save_model(request, obj, form, change)


@admin.register(IntelligenceSubmission)
class IntelligenceSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender_name', 'detected_data_type',
                    'current_stage', 'status', 'received_at']
    list_filter = ['status', 'current_stage', 'detected_data_type']
    search_fields = ['title', 'sender_name', 'sender_email']
    readonly_fields = ['file_size', 'file_name', 'received_at',
                       'started_processing_at', 'completed_at', 'sent_at']
