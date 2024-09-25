from django.db import models
from django.utils import timezone
import os

# To get the name of the file being uploaded, you can use the name attribute of the file field. 
# When a file is uploaded through the FileField, Django stores the file with its original name in 
# the name attribute of the file object.

def upload_to_author_dir(instance, filename):
    return os.path.join('uploads',instance.author,filename)

# Create your models here.
class FileNest(models.Model):
    language = models.CharField(max_length=100) # to store programming language
    author = models.CharField(max_length=100) # to store the username
    docType = models.CharField(max_length=100) # to store type of documentation to be generated
    dateTime = models.DateTimeField(default=timezone.now) # to store the time of upload
    file = models.FileField(upload_to=upload_to_author_dir)
