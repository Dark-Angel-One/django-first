from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import F, Case, When, Value
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Note, Label, ChecklistItem
from .serializers import NoteSerializer, LabelSerializer, ChecklistItemSerializer

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
    ordering = ['-is_pinned', 'order', '-updated_at']

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user).prefetch_related('labels', 'checklist_items')

        if 'is_archived' not in self.request.query_params:
            queryset = queryset.filter(is_archived=False)

        if 'is_trashed' not in self.request.query_params:
            queryset = queryset.filter(is_trashed=False)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        # Используем оптимизированный метод обновления (без лишнего запроса в БД)
        updated = Note.objects.filter(pk=pk, user=request.user).update(
            is_archived=Case(When(is_archived=True, then=Value(False)), default=Value(True)),
            is_trashed=Case(When(is_archived=False, then=Value(False)), default=F('is_trashed')),
            updated_at=timezone.now()
        )
        if updated == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        note = Note.objects.get(pk=pk)
        return Response({'is_archived': note.is_archived, 'is_trashed': note.is_trashed})

    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        try:
            note = Note.objects.get(pk=pk, user=request.user)
        except Note.DoesNotExist:
             return Response(status=status.HTTP_404_NOT_FOUND)

        if note.is_trashed:
            # Restore
            note.is_trashed = False
            note.is_archived = False
        else:
            # Trash
            note.is_trashed = True
            note.is_archived = False
            note.is_pinned = False

        note.updated_at = timezone.now()
        note.save()
        return Response({'is_trashed': note.is_trashed, 'is_archived': note.is_archived})

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        updated = Note.objects.filter(pk=pk, user=request.user).update(
            is_pinned=Case(When(is_pinned=True, then=Value(False)), default=Value(True)),
            updated_at=timezone.now()
        )
        if updated == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        note = Note.objects.get(pk=pk)
        return Response({'is_pinned': note.is_pinned})

    @action(detail=False, methods=['post'])
    def empty_trash(self, request):
        count, _ = Note.objects.filter(user=request.user, is_trashed=True).delete()
        return Response({'status': 'Корзина очищена', 'deleted_count': count})

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        pinned_ids = request.data.get('pinned_ids', [])
        other_ids = request.data.get('other_ids', [])

        all_ids = pinned_ids + other_ids
        if not all_ids:
            return Response({'status': 'ok'})

        notes = list(Note.objects.filter(id__in=all_ids, user=request.user))

        pinned_map = {int(pid): i for i, pid in enumerate(pinned_ids)}
        other_map = {int(pid): i for i, pid in enumerate(other_ids)}

        updates = []
        for note in notes:
            if note.id in pinned_map:
                note.is_pinned = True
                note.order = pinned_map[note.id]
                updates.append(note)
            elif note.id in other_map:
                note.is_pinned = False
                note.order = other_map[note.id]
                updates.append(note)

        if updates:
            Note.objects.bulk_update(updates, ['is_pinned', 'order'])

        return Response({'status': 'порядок обновлен'})

class LabelViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = LabelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Label.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChecklistItemViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Гарантируем, что пользователь видит только свои пункты списка
        return ChecklistItem.objects.filter(note__user=self.request.user)