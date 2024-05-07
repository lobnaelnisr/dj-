from django.db import models

# Create your models here.
class SessionData(models.Model):
    #CaptureTime = models.TimeField(auto_now= True, blank=True)
    CaptureTime = models.CharField(max_length=12, null=True, blank=True)
    SessionEndedAt = models.CharField(max_length=12, null=True, blank=True)
    SessionStartedAt = models.CharField(max_length=12, null=True, blank=True)
    arousal = models.IntegerField()
    attention = models.IntegerField()
    dominantEmotion = models.CharField(max_length=50)
    feature_1 = models.CharField(max_length=50)
    feature_2 = models.CharField(max_length=50)
    feature_3 = models.CharField(max_length=50)
    feature_4 = models.CharField(max_length=50)
    feature_5 = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    userEmail = models.CharField(max_length=100)
    valence = models.FloatField()
    volume = models.FloatField()
    #SessionEndedAt = models.CharField(max_length=12, null=True, blank=True)
    def __str__(self):
        return self.userEmail

