from rest_framework import serializers
from .models import ChatSession, Message
from pdf.serializers import PDFDocumentSerializer


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content']


class ChatSessionListSerializer(serializers.ModelSerializer):
    pdf = PDFDocumentSerializer(read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'pdf']
