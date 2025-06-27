from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL


class PDFDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PDFChunk(models.Model):
    pdf = models.ForeignKey(
        PDFDocument, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    embedding = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk for {self.pdf.title[:30]} - {self.id}"
