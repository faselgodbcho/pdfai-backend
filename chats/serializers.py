from rest_framework import serializers
from .models import ChatSession, Message
from users.serializers import UserSerializer
from pdf.serializers import PDFDocumentSerializer


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content']


class ChatSessionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    pdf = PDFDocumentSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'pdf', 'created_at', 'messages']
        read_only_fields = ['user', 'pdf', 'created_at', 'messages']
