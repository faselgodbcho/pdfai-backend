from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .serializers import PDFDocumentSerializer
from .utils import extract_text_from_pdf
from chats.models import ChatSession
from .utils import embed_chunks, chunk_text
from .models import PDFChunk


class PDFUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = PDFDocumentSerializer(data=request.data)

        MAX_FILE_SIZE_MB = 10

        uploaded_file = request.FILES.get("file")

        file_size_mb = uploaded_file.size / (1024 * 1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            return Response({"error": f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB."}, status=400)

        if not uploaded_file.name.endswith('.pdf'):
            return Response({"error": "Only PDF files are allowed."}, status=400)

        serializer.is_valid(raise_exception=True)
        pdf_instance = serializer.save(user=request.user)

        try:
            extracted_content = extract_text_from_pdf(pdf_instance.file.path)
        except Exception as e:
            return Response({"error": f"Failed to read PDF: {str(e)}"}, status=400)

        chunks = chunk_text(extracted_content)

        if len(extracted_content.strip()) < 50:
            return Response({"error": "PDF contains little or no extractable text"}, status=400)

        try:
            embeddings = embed_chunks(chunks)

        except Exception as e:
            return Response({"error": f"Embedding error: {str(e)}"}, status=500)

        chunk_objects = []

        for chunk, embedding in zip(chunks, embeddings):
            chunk_objects.append(PDFChunk(
                pdf=pdf_instance,
                content=chunk,
                embedding=embedding
            ))

        session = ChatSession.objects.create(
            user=request.user, pdf=pdf_instance)

        PDFChunk.objects.bulk_create(chunk_objects, batch_size=100)

        response_data = serializer.data
        response_data["session_id"] = str(session.id)

        return Response(response_data, status=status.HTTP_201_CREATED)


upload_pdf_view = PDFUploadView.as_view()
