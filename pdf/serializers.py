from rest_framework import serializers

from .models import PDFDocument
from users.serializers import UserSerializer


class PDFDocumentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    title = serializers.CharField(read_only=True)

    class Meta:
        model = PDFDocument
        fields = ['id', 'user', 'title', 'file', 'uploaded_at']
        read_only_fields = ['user', 'uploaded_at']
