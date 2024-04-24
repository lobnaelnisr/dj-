from django.db import models

# Create your models here.
class morph_data(models.Model):
    username = models.CharField(max_length=200)
    arousal = models.SmallIntegerField(default='')
    attention = models.IntegerField(default='')
    valence = models.FloatField( default= '')
    volume = models.FloatField(default='')
    dominantEmotion = models.CharField(max_length=100)
    time = models.TimeField(auto_now= True, blank=True)   #.timezone.now
    date = models.DateField(auto_now=True, blank=True)  #.date.today
    #class Meta:
        #managed = False
        #db_table = 'my_collection'

    def __str__(self):
        return self.username 

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
    
