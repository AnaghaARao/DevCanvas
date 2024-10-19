from rest_framework import serializers
from .models import SummaryDoc

class SummaryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryDoc
        fields = ['language', 'author', 'file']