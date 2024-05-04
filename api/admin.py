from django.contrib import admin

# Register your models here.

#from .models import morph_data

#admin.site.register(morph_data)
# Register your models here.
from .models import SessionData

@admin.register(SessionData)
class SessionDataAdmin(admin.ModelAdmin):
    list_display = ['userName','SessionStartedAt', 'arousal', 'attention', 'dominantEmotion', 'gender', 'valence', 'volume','SessionEndedAt']
    search_fields = ['userName']
    def SessionEndedAt(self, obj):
        # Implement logic to generate the value for the custom field
        return "Custom Value"
