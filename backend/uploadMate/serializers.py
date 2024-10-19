from rest_framework import serializers
from .models import FileNest

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileNest
        fields = ['language','docType', 'file']