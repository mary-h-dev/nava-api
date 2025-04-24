from collections import defaultdict

from django.db import models

# Create your models here.


class FileManagers(models.Model):
    file = models.FileField(upload_to='filemanager/%Y/%m/%d/')
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

