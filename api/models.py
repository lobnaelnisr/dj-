from django.db import models


class SessionData(models.Model):
    #CaptureTime = models.TimeField(auto_now= True, blank=True)
    CaptureTime = models.CharField(max_length=12, null=True, blank=True)
    SessionEndedAt = models.CharField(max_length=12, null=True, blank=True)
    SessionStartedAt = models.CharField(max_length=12, null=True, blank=True)
    Session_for = models.CharField(max_length=255, default='')
    arousal = models.FloatField()
    attention = models.FloatField()
    dominantEmotion = models.CharField(max_length=50)
    #gender = models.CharField(max_length=10)
    userEmail = models.CharField(max_length=100)
    valence = models.FloatField()
    volume = models.FloatField()
    
    
    def __str__(self):
        return self.userEmail

