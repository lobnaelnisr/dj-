from django.db import models


class SessionData(models.Model):
    CaptureTime = models.CharField(max_length=12, null=True, blank=True)
    SessionEndedAt = models.CharField(max_length=12, null=True, blank=True)
    SessionStartedAt = models.CharField(max_length=12, null=True, blank=True)
    Session_for = models.CharField(max_length=255, default='')
    arousal = models.IntegerField()
    attention = models.IntegerField()
    dominantEmotion = models.CharField(max_length=50, null=True, blank=True)
    userEmail = models.CharField(max_length=100)
    valence = models.FloatField()
    volume = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.userEmail

