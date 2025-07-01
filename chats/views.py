import json
import uuid
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status


from pdf.models import PDFChunk
from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from pdfai.client import co
from .utils import embed_query, cosine_sim


class ChatSessionListAPIView(generics.ListAPIView):
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')


session_list_view = ChatSessionListAPIView.as_view()


class ChatAPIView(APIView):
    def post(self, request):
        user = request.user
        prompt = request.data.get("prompt")
        session_id = request.data.get("session_id")

        if not prompt.strip() or not session_id:
            return Response({"error": "prompt and session_id are required"}, status=400)

        try:
            prompt_embedding = embed_query(prompt)
        except Exception as e:
            return Response({"error": f"Embedding Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            session_uuid = uuid.UUID(session_id.strip())
        except (ValueError, TypeError):
            return Response({"error": "Invalid session ID format"}, status=status.HTTP_400_BAD_REQUEST)

        session = get_object_or_404(ChatSession, id=session_uuid, user=user)

        user_msg = Message.objects.create(
            session=session, sender="user", content=prompt)

        messages = Message.objects.filter(
            session=session).order_by("timestamp")

        chat_history = [
            {"role": "user" if m.sender ==
                "user" else "assistant", "content": m.content}
            for m in messages
        ]

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

        if context:
            system_message = {
                "role": "system",
                "content": (
                    "You are PDF AI, a helpful assistant created by Cohere and used by Fasel Godbcho. "
                    "Your role is to answer questions about PDF documents the user uploads. "
                    "If the user wants to learn more about Fasel's projects, suggest visiting https://github.com/faselgodbcho.\n\n"
                    f"Use the following context from the uploaded PDF to assist the user:\n\n{context}"
                )
            }

            chat_messages = [system_message] + chat_history
        else:
            system_message = {
                "role": "system",
                "content": (
                    "You are PDF AI, a helpful assistant created by Cohere and used by Fasel Godbcho. "
                    "Your role is to answer questions about PDF documents the user uploads. "
                    "If the user wants to learn more about Fasel's projects, suggest visiting https://github.com/faselgodbcho."
                )
            }

            chat_messages = [system_message] + chat_history

        try:
            response = co.chat(
                messages=chat_messages,
                model="command-r-plus",
                temperature=0.3,
                max_tokens=500
            )
            ai_response = response.json()
        except Exception as e:
            return Response({"error": f"AI chat error: {str(e)}"}, status=500)

        ai_msg = Message.objects.create(
            session=session, sender="ai", content=ai_response)

        return Response({
            "messages": [
                MessageSerializer(user_msg).data,
                MessageSerializer(ai_msg).data
            ]
        }, status=201)


chat_api_view = ChatAPIView.as_view()


class DeleteChatSessionAPIview(generics.DestroyAPIView):
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


delete_session_api_view = DeleteChatSessionAPIview.as_view()
