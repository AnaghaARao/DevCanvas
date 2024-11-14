import os
from django.db import models
from django.utils import timezone
from django.conf import settings

# Function to handle file storage in a structured directory
def upload_to_author(instance, filename):
    # Structure: uploads/<author>/<dir_name>/<filename>
    return os.path.join('uploads', instance.file_nest.author, instance.file_nest.dir_name, filename)

class FileNest(models.Model):
    language = models.CharField(max_length=100)  # Programming language
    author = models.CharField(max_length=100)  # Username or author of the files
    docType = models.CharField(max_length=100)  # Documentation type (e.g., summary, class diagram)
    dateTime = models.DateTimeField(default=timezone.now)  # Time of upload
    dir_name = models.CharField(max_length=100, default='default_directory')  # Directory name for structuring uploads

    def __str__(self):
        return f"FileNest {self.id} - {self.docType} by {self.author}"

class FileEntry(models.Model):
    file_nest = models.ForeignKey(FileNest, on_delete=models.CASCADE, related_name='files')  # Relationship with FileNest
    file = models.FileField(upload_to=upload_to_author)  # File field for each file in the directory

    def __str__(self):
        return f"FileEntry {self.id} for {self.file_nest}"
