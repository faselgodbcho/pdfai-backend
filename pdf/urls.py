from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.upload_pdf_view, name='pdf-upload'),
    path("download/<uuid:session_id>/",
         views.export_pdf_view, name='pdf-download'),
]
