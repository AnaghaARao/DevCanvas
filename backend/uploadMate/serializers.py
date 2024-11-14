from rest_framework import serializers
from .models import FileNest, FileEntry
import os

class DocumentUploadSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )
    dir_name = serializers.CharField(required=True)
    docType = serializers.ChoiceField(
        choices=['summary', 'class diagram', 'sequence diagram', 'flowchart'],
        required=True
    )
    author = serializers.CharField(required=True)

    class Meta:
        model = FileNest
        fields = ['language', 'docType', 'author', 'dir_name', 'files']

    def validate_files(self, files):
        # Ensure only allowed file extensions are uploaded
        allowed_extensions = {'.py', '.pyw', '.java'}
        for file in files:
            ext = os.path.splitext(file.name)[1]
            if ext not in allowed_extensions:
                raise serializers.ValidationError(f"Unsupported file type: {file.name}")
        return files

    def create(self, validated_data):
        files = validated_data.pop('files')
        file_nest = FileNest.objects.create(**validated_data)
        for file in files:
            FileEntry.objects.create(file_nest=file_nest, file=file)
        return file_nest
