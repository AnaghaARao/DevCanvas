from rest_framework import serializers
from .models import FileNest, FileEntry

class DocumentUploadSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True  # Only for input, not included in output
    )
    dir_name = serializers.CharField(required=True)  # Directory name for structuring the upload path

    class Meta:
        model = FileNest
        fields = ['language', 'docType', 'author', 'dir_name', 'files']

    def create(self, validated_data):
        # Pop 'files' from validated data to handle them separately
        files = validated_data.pop('files')
        file_nest = FileNest.objects.create(**validated_data)  # Create FileNest entry without 'files'

        # Create a FileEntry for each uploaded file
        for file in files:
            FileEntry.objects.create(file_nest=file_nest, file=file)

        return file_nest
