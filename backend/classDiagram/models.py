from django.db import models
from django.utils import timezone
import os

# Define a function to dynamically set the upload path based on the author
def upload_to_author(instance, filename):
    # Create the path uploads/<author>/<filename>
    return os.path.join('uploads', instance.author, filename)
class ClassDiagram(models.Model):
    language = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_to_author)  # Use the function for dynamic path
    generated_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'Class Diagram for {self.language} by {self.author}'