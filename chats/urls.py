from django.urls import path

from . import views

urlpatterns = [
    path("sessions/", views.session_list_view, name="chat-session-list"),
    path("chat/", views.chat_api_view, name="ai-chat"),
]
