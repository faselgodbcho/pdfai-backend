from django.contrib import admin

from .models import PDFDocument, PDFChunk

# Register your models here.
admin.site.register(PDFDocument)
admin.site.register(PDFChunk)
