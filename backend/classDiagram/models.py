from django.db import models
from django.utils import timezone
from django.conf import settings
import os

# Define a function to dynamically set the upload path based on the author
def upload_to_author(instance, filename):
    # Structure: uploads/<author>/<dir_name>/<filename>
    return os.path.join(settings.MEDIA_ROOT, instance.class_diagram_nest.author, instance.class_diagram_nest.dir_name, filename)

class ClassDiagramNest(models.Model):
    language = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_to_author)  # Use the function for dynamic path
    generated_at = models.DateTimeField(default=timezone.now)
    dir_name = models.CharField(max_length=100, default='default_class_directory')
    def __str__(self):
        return f'Class Diagram for {self.language} by {self.author}'
    
class ClassDiagramEntry(models.Model):
    sequence_diagram_nest = models.ForeignKey(ClassDiagramNest, on_delete=models.CASCADE, related_name='class_diagram_files')
    file = models.FileField(upload_to=upload_to_author)