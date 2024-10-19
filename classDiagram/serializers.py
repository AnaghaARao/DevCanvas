from rest_framework import serializers
from .models import ClassDiagram

class ClassDiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassDiagram
        fields = ['language', 'author', 'file']
