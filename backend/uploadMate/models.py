import os
from django.db import models
from django.utils import timezone
from django.conf import settings

# # Custom function to handle directory creation
# def upload_to_author(instance, filename):
#     # Define the base uploads directory path
#     base_upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')

#     # Check if the 'uploads' directory exists, if not, create it
#     if not os.path.exists(base_upload_dir):
#         os.makedirs(base_upload_dir)
    
#     # Define the author directory path within uploads
#     author_upload_dir = os.path.join(base_upload_dir, instance.author)

#     # Check if the author's directory exists, if not, create it
#     if not os.path.exists(author_upload_dir):
#         os.makedirs(author_upload_dir)
    
#     # Return the final relative file path for saving
#     return os.path.join('uploads', instance.author, filename)

def upload_to_author(instance, filename):
    # Structure: uploads/<author>/<dir_name>/<filename>
    return os.path.join('uploads', instance.file_nest.author, instance.file_nest.dir_name, filename)

# Create your models here.
class FileNest(models.Model):
    language = models.CharField(max_length=100)  # to store programming language
    author = models.CharField(max_length=100)  # to store the username
    docType = models.CharField(max_length=100)  # to store type of documentation to be generated
    dateTime = models.DateTimeField(default=timezone.now)  # to store the time of upload
    file = models.FileField(upload_to=upload_to_author)  # Store the file using the custom function
    dir_name = models.CharField(max_length=100, default='default_directory')  # Store directory name
    is_directory = models.BooleanField(default=False)

class FileEntry(models.Model):
    file_nest = models.ForeignKey(FileNest, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=upload_to_author)

