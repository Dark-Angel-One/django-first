from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Note, Label, ChecklistItem
from .serializers import NoteSerializer, LabelSerializer, ChecklistItemSerializer

class NoteViewSet(viewsets.ModelViewSet):
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
        note.save()
        return Response({'status': 'archived' if note.is_archived else 'unarchived', 'is_archived': note.is_archived})

    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        note = self.get_object()
        # Toggle logic:
        # If not in trash -> move to trash
        # If in trash -> User might want to restore or delete forever.
        # But this endpoint is usually "Toggle Trash".
        # If the requirement says "returns to main list instead of deleting forever", it implies the user expects "Delete" in Trash to mean "Delete Forever".
        # So:
        # 1. If we are in the main list, "Trash" button calls this to set is_trashed=True.
        # 2. If we are in the Trash view, "Delete" button should call DELETE method (destroy).
        # 3. If we are in the Trash view, "Restore" button calls this to set is_trashed=False.

        # Current logic just toggles.
        note.is_trashed = not note.is_trashed
        if note.is_trashed:
            note.is_archived = False
            note.is_pinned = False # Usually unpin when trashed
        note.save()
        return Response({'status': 'trashed' if note.is_trashed else 'restored', 'is_trashed': note.is_trashed})

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        note = self.get_object()
        note.is_pinned = not note.is_pinned
        note.save()
        return Response({'status': 'pinned' if note.is_pinned else 'unpinned', 'is_pinned': note.is_pinned})

    @action(detail=True, methods=['patch'], url_path='check')
    def toggle_check(self, request, pk=None):
        """Endpoint to toggle a specific checklist item's checked status"""
        # Note: This is usually done on the item itself, but we can do it via Note if we pass item_id
        # Alternatively, create a ChecklistItemViewSet.
        # But requirements say "Fix PATCH request on click".
        # Let's support patching the item directly via a nested structure or a separate endpoint?
        # A separate ViewSet for ChecklistItem is cleaner.
        pass

    @action(detail=False, methods=['post'])
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

class ChecklistItemViewSet(viewsets.ModelViewSet):
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure user owns the note
        return ChecklistItem.objects.filter(note__user=self.request.user)
