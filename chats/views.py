import uuid
from io import BytesIO
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas

from users.models import UserSettings
from pdf.models import PDFChunk
from .models import ChatSession, Message
from .serializers import ChatSessionListSerializer, MessageSerializer
from pdfai.client import co
from .utils import embed_query, cosine_sim


class ChatSessionListAPIView(generics.ListAPIView):
    serializer_class = ChatSessionListSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')


session_list_view = ChatSessionListAPIView.as_view()


class ChatAPIView(APIView):
    def post(self, request):
        user = request.user
        prompt = request.data.get("prompt")
        session_id = request.data.get("session_id")

        if not prompt or not prompt.strip() or not session_id:
            return Response({"error": "prompt and session_id are required"}, status=400)

        try:
            prompt_embedding = embed_query(prompt)
        except Exception as e:
            return Response({"error": f"Embedding Error: {str(e)}"}, status=500)

        try:
            session_uuid = uuid.UUID(session_id.strip())
        except (ValueError, TypeError):
            return Response({"error": "Invalid session ID format"}, status=400)

        session = get_object_or_404(ChatSession, id=session_uuid, user=user)

        # Fetch user settings with defaults if not set
        try:
            settings = UserSettings.objects.get(user=user)
        except ObjectDoesNotExist:
            # Fallback defaults
            settings = UserSettings(
                user=user,
                response_length="medium",
                tone="neutral",
                context_memory=True,
            )

        user_msg = Message.objects.create(
            session=session, sender="user", content=prompt)

        if settings.context_memory:
            messages = Message.objects.filter(
                session=session).order_by("timestamp")
            chat_history = [
                {"role": "user" if m.sender ==
                    "user" else "assistant", "content": m.content}
                for m in messages
            ]
        else:
            chat_history = [{"role": "user", "content": prompt}]

        chunks = PDFChunk.objects.filter(pdf=session.pdf)

        if not chunks.exists():
            return Response({"error": "No data available for this PDF yet"}, status=400)

        ranked_chunks = sorted(
            chunks,
            key=lambda chunk: cosine_sim(prompt_embedding, chunk.embedding),
            reverse=True
        )
        top_chunks = ranked_chunks[:5]

        context = "\n\n".join(chunk.content for chunk in top_chunks)

        system_content = (
            "You are PDF AI, a helpful assistant created by Cohere and used by Fasel Godbcho to create PDF AI. "
            "Your role is to answer questions about PDF documents the user uploads. "
            "If the user asks about Fasel Godbcho, kindly suggest visiting his GitHub portfolio: https://github.com/faselgodbcho."
            f" Use the following context from the uploaded PDF to assist the user:\n\n{context}"
        )

        system_message = {"role": "system", "content": system_content}

        chat_messages = [system_message] + \
            chat_history if context else [system_message]

        system_message["content"] += (
            f"\n\nPlease respond in a {settings.tone} tone and keep your reply "
            f"{settings.response_length} in length."
        )

        max_tokens_map = {
            "short": 150,
            "medium": 300,
            "long": 600,
        }

        try:
            response = co.chat(
                messages=chat_messages,
                model="command-r-plus",
                temperature=0.3,
                max_tokens=max_tokens_map[settings.response_length]
            )
            ai_response = response.json()
        except Exception as e:
            return Response({"error": f"AI chat error: {str(e)}"}, status=500)

        ai_msg = Message.objects.create(
            session=session, sender="ai", content=ai_response)

        return Response({"message": MessageSerializer(ai_msg).data}, status=201)


chat_api_view = ChatAPIView.as_view()


class DeleteChatSessionAPIView(generics.DestroyAPIView):
    serializer_class = ChatSessionListSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


delete_session_view = DeleteChatSessionAPIView.as_view()


class MessageListAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        session_id = self.kwargs.get("session_id")
        session = get_object_or_404(
            ChatSession, id=session_id, user=self.request.user)
        return session.messages.all()


message_list_view = MessageListAPIView.as_view()


class ExportAllChatsPDFAPIView(APIView):

    def get(self, request):
        sessions = ChatSession.objects.filter(
            user=request.user).order_by("created_at")

        if not sessions.exists():
            return Response({"error": "No chat sessions found"}, status=404)

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        y = 800
        pdf.setFont("Helvetica", 12)

        for session in sessions:
            pdf.drawString(50, y, f"Session ID: {session.id}")
            y -= 20

            messages = Message.objects.filter(
                session=session).order_by("timestamp")
            for msg in messages:
                sender = "You" if msg.sender == "user" else "PDF AI"
                lines = msg.content.splitlines()

                for line in lines:
                    if y < 50:
                        pdf.showPage()
                        pdf.setFont("Helvetica", 12)
                        y = 800
                    pdf.drawString(70, y, f"{sender}: {line}")
                    y -= 15
                y -= 10

            y -= 30  # space between sessions

            if y < 100:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y = 800

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename="all-chat-sessions.pdf")


export_chat_view = ExportAllChatsPDFAPIView.as_view()


class ClearChatHistoryAPIView(APIView):
    def delete(self, request):
        sessions = ChatSession.objects.filter(user=request.user)
        for session in sessions:
            session.messages.all().delete()
        sessions.delete()
        return Response({"message": "Chat history cleared"}, status=status.HTTP_204_NO_CONTENT)


clear_chat_view = ClearChatHistoryAPIView.as_view()
