from django.urls import path

from . import views

urlpatterns = [
    path("sessions/", views.session_list_view, name="chat-session-list"),
    path("chat/", views.chat_api_view, name="ai-chat"),
    path("sessions/<uuid:session_id>/messages/",
         views.message_list_view, name="session-messages"),
    path("sessions/<uuid:pk>",
         views.delete_session_view, name="session-delete"),

]
