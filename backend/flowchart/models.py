from django.db import models
from django.utils import timezone
import os

# Define a function to dynamically set the upload path based on the author
def upload_to_author(instance, filename):
    # Structure: uploads/<author>/flowcharts/<dir_name>/<filename>
    return os.path.join('uploads', instance.flowchart_nest.author, 'flowcharts', instance.flowchart_nest.dir_name, filename)

class FlowchartNest(models.Model):
    language = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_to_author)  # Use the function for dynamic path
    generated_at = models.DateTimeField(default=timezone.now)
    dir_name = models.CharField(max_length=100, default='default_flowchart_directory')
    def __str__(self):
        return f'Flowchart for {self.language} by {self.author}'
    
class FlowchartEntry(models.Model):
    flowchart_nest = models.ForeignKey(FlowchartNest, on_delete=models.CASCADE, related_name='flowchart_files')
    file = models.FileField(upload_to=upload_to_author)