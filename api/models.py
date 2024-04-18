from django.db import models
#from djongo import models  # Import from Djongo


# Create your models here.
class MyModel(models.Model):
    username = models.CharField(max_length=200)
    #field2 = models.IntegerField()
    #email = models.CharField(max_length=200)
    major = models.CharField(max_length=100)

    email = models.EmailField(default='example@example.com')

    #class Meta:
        #managed = False
        #db_table = 'my_collection'

    #def __str__(self):                                   #func to show data instead of showing object1 , obj2 ..... 
        #return self.username + ' : ' + self.major                              # u can show more data fields in admin page
    #def _str(self): 
        #return self.username + ' : ' + self.major
    def _str_(self):
        return f"{self.username} : {self.major}"
    
