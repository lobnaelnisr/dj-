from django.contrib import admin

# Register your models here.

#from .models import morph_data

#admin.site.register(morph_data)
# Register your models here.
from .models import SessionData

@admin.register(SessionData)
class SessionDataAdmin(admin.ModelAdmin):
    list_display = ['userName','SessionStartedAt', 'arousal', 'attention', 'dominantEmotion', 'gender', 'valence', 'volume']
    search_fields = ['userName']
