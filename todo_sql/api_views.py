from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import F, Case, When, Value
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
        # Используем оптимизированный метод обновления (без лишнего запроса в БД)
        updated = Note.objects.filter(pk=pk, user=request.user).update(
            is_archived=Case(When(is_archived=True, then=Value(False)), default=Value(True)),
            is_trashed=Case(When(is_archived=False, then=Value(False)), default=F('is_trashed'))
        )
        if updated == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'toggled'})

    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        updated = Note.objects.filter(pk=pk, user=request.user).update(
            is_trashed=Case(When(is_trashed=True, then=Value(False)), default=Value(True)),
            is_archived=Case(When(is_trashed=False, then=Value(False)), default=F('is_archived'))
        )
        if updated == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'toggled'})

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        updated = Note.objects.filter(pk=pk, user=request.user).update(
            is_pinned=Case(When(is_pinned=True, then=Value(False)), default=Value(True))
        )
        if updated == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'toggled'})

    @action(detail=False, methods=['post'])
    def empty_trash(self, request):
        count, _ = Note.objects.filter(user=request.user, is_trashed=True).delete()
        return Response({'status': 'trash emptied', 'deleted_count': count})

class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Label.objects.filter(user=self.request.user)