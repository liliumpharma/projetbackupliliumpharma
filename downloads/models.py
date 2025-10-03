from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Downloadable(models.Model):
    attachement = models.FileField(upload_to="downloadable", max_length=100)
    link_name = models.CharField(max_length=100)
    users = models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.link_name    