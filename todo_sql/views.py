from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
import json

from .models import Note
from .forms import NoteForm

class NoteListView(ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        # Sort by pinned (True first -> Descending), then updated_at (Desc)
        return queryset.order_by('-is_pinned', '-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = NoteForm() # For the "Create" part
        return context

@require_POST
def create_note_ajax(request):
    try:
        # Check if data is JSON (fetch) or Form Data (standard submit fallback)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            form = NoteForm(data)
        else:
            form = NoteForm(request.POST)

        if form.is_valid():
            note = form.save()
            return JsonResponse({
                'success': True,
                'note': {
                    'id': note.id,
                    'title': note.title,
                    'content': note.content,
                    'color': note.color,
                    'is_pinned': note.is_pinned,
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'edit.html'
    success_url = reverse_lazy('index')

class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'delete.html'
    success_url = reverse_lazy('index')
