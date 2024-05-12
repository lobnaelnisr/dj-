from django.contrib import admin
from .models import SessionData

@admin.register(SessionData)
class SessionDataAdmin(admin.ModelAdmin):
    list_display = ['userEmail', 'CaptureTime', 'SessionStartedAt', 'arousal', 'attention', 'dominantEmotion', 'gender', 'valence', 'volume','SessionEndedAt']
    search_fields = ['userName']
    
