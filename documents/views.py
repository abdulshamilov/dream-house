from rest_framework import generics, permissions
from .models import Document
from .serializers import DocumentSerializer

class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.AllowAny]  # можно позже ограничить

class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]  # только авторизованные могут загружать

class DocumentDetailView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.AllowAny]

class DocumentDownloadView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        response = document.file.open('rb')
        from django.http import FileResponse
        return FileResponse(response, as_attachment=True, filename=document.file.name)
