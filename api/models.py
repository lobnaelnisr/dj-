from django.db import models

# Create your models here.
class SessionData(models.Model):
    session_started_at = models.CharField(max_length=8, null=True, blank=True)
    #SessionStartedAt = models.TimeField(auto_now= True, blank=True)
    arousal = models.IntegerField()
    attention = models.IntegerField()
    dominantEmotion = models.CharField(max_length=50)
    feature_1 = models.CharField(max_length=50)
    feature_2 = models.CharField(max_length=50)
    feature_3 = models.CharField(max_length=50)
    feature_4 = models.CharField(max_length=50)
    feature_5 = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    userName = models.CharField(max_length=100)
    valence = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        return self.userName
#def create_student(request, name, email):
    #student = student_data(name=name, email=email)
    #student.save()
    #return student


#def get_students():
    #return student_data.objects.all()


#def delete_student(id):
    #student = student_data.objects.get(pk=id)
    #student.delete()
    #return student


#def update_student(id, name, email):
    #student = student_data.objects.get(pk=id)
    #student.name = name
    #student.email = email
    #student.save()
    #return student
    
