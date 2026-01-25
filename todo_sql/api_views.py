from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Note, Label, ChecklistItem
from .serializers import NoteSerializer, LabelSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class NoteViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_pinned', 'is_archived', 'is_trashed', 'color', 'is_checklist', 'labels']
    search_fields = ['title', 'content', 'checklist_items__text']
    ordering_fields = ['updated_at', 'created_at']
    ordering = ['-is_pinned', '-updated_at']

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        note = self.get_object()
        note.is_archived = not note.is_archived
        if note.is_archived:
            note.is_trashed = False
        note.save(update_fields=['is_archived', 'is_trashed'])
        return Response({'status': 'archived' if note.is_archived else 'unarchived', 'is_archived': note.is_archived})

    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        note = self.get_object()
        note.is_trashed = not note.is_trashed
        if note.is_trashed:
            note.is_archived = False
        note.save(update_fields=['is_trashed', 'is_archived'])
        return Response({'status': 'trashed' if note.is_trashed else 'restored', 'is_trashed': note.is_trashed})

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        note = self.get_object()
        note.is_pinned = not note.is_pinned
        note.save(update_fields=['is_pinned'])
        return Response({'status': 'pinned' if note.is_pinned else 'unpinned', 'is_pinned': note.is_pinned})

    @action(detail=False, methods=['post']) # Changed to POST for safety, though DELETE is semantic
    def empty_trash(self, request):
        count, _ = Note.objects.filter(user=request.user, is_trashed=True).delete()
        return Response({'status': 'trash emptied', 'deleted_count': count})

class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Label.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
