from rest_framework import serializers
from .models import FileNest, FileEntry

class FileEntrySerializer(serializers.ModelSerializer):
    # Serializer for individual files within a FileNest
    file = serializers.FileField()

    class Meta:
        model = FileEntry
        fields = ['file']

class DocumentUploadSerializer(serializers.ModelSerializer):
    # Accepts multiple files, now handled by FileEntry model
    files = FileEntrySerializer(many=True, write_only=True)  # Accepts a list of FileEntry objects
    dir_name = serializers.CharField(required=True)  # Directory name for structuring the file upload path
    docType = serializers.ChoiceField(
        choices=['summary', 'class diagram', 'sequence diagram', 'flowchart'],
        required=True
    )  # Documentation type
    author = serializers.CharField(required=True)  # Author name or ID (can be linked to user model later)
    language = serializers.CharField(required=True)  # Programming language used

    class Meta:
        model = FileNest
        fields = ['language', 'docType', 'author', 'dir_name', 'files']

    def create(self, validated_data):
        # Extract 'files' from validated data to handle them separately
        files_data = validated_data.pop('files')
        
        # Create the FileNest instance
        file_nest = FileNest.objects.create(**validated_data) 
        
        # Create FileEntry instances for each file and associate them with the FileNest instance
        for file_data in files_data:
            FileEntry.objects.create(file_nest=file_nest, **file_data)

        return file_nest
