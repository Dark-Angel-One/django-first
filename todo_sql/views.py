from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
import json

from .models import Note
from .forms import NoteForm, UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user, is_archived=False, is_trashed=False)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        return queryset.order_by('-is_pinned', '-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Notes'
        context['active_tab'] = 'notes'
        return context

class ArchiveView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user, is_archived=True, is_trashed=False).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Archive'
        context['active_tab'] = 'archive'
        return context

class TrashView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user, is_trashed=True).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Trash'
        context['active_tab'] = 'trash'
        return context

class LabelNoteView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        label_name = self.kwargs['label']
        return Note.objects.filter(user=self.request.user, labels__name=label_name, is_archived=False, is_trashed=False).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.kwargs['label']
        context['active_tab'] = 'label'
        context['active_label'] = self.kwargs['label']
        return context

@login_required
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
            note = form.save(commit=False)
            note.user = request.user
            note.save()
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

class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'edit.html'
    success_url = reverse_lazy('index')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'delete.html'
    success_url = reverse_lazy('index')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
