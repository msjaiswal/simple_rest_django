from django.db import models

# Create your models here.
class SplitUser(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)



