from django.urls import path
from .views import DocumentListView, DocumentCreateView, DocumentDetailView, DocumentDownloadView

urlpatterns = [
    path('', DocumentListView.as_view(), name='document_list'),
    path('add/', DocumentCreateView.as_view(), name='document_add'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/download/', DocumentDownloadView.as_view(), name='document_download'),
]
