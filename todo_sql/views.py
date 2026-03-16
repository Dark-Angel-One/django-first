from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
import random

from .models import Note
from .forms import UserRegistrationForm

# ТИМЛИД: API для "живой" проверки занятости никнейма
def check_username(request):
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'status': 'empty'})
    
    if len(username) < 3:
        return JsonResponse({'status': 'invalid', 'message': 'Имя должно быть длиннее 3 символов'})

    if User.objects.filter(username__iexact=username).exists():
        # Если занято, генерируем варианты
        suggestions = []
        for _ in range(3):
            suffix = str(random.randint(10, 999))
            suggestions.append(f"{username}{suffix}")
        return JsonResponse({
            'status': 'taken', 
            'message': 'Имя пользователя занято',
            'suggestions': suggestions
        })
    else:
        return JsonResponse({'status': 'available', 'message': 'Имя пользователя свободно!'})

# ТИМЛИД: Функция удаления аккаунта
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete() # Каскадное удаление сотрет все заметки
        return redirect('login')
    return redirect('index')

# ТИМЛИД: Дебаг панель только для админов (staff)
@user_passes_test(lambda u: u.is_staff)
def debug_panel(request):
    total_users = User.objects.count()
    total_notes = Note.objects.count()
    context = {
        'total_users': total_users,
        'total_notes': total_notes,
    }
    return render(request, 'debug_panel.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # ТИМЛИД: ИСПРАВЛЕНИЕ БАГА! Указываем backend явно, так как у нас их 2 в settings.py
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user, is_archived=False, is_trashed=False)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return queryset.prefetch_related('labels', 'checklist_items').order_by('-is_pinned', '-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Заметки'
        context['active_tab'] = 'notes'
        return context

class ArchiveView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user, is_archived=True, is_trashed=False).prefetch_related('labels', 'checklist_items').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Архив'
        context['active_tab'] = 'archive'
        return context

class TrashView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user, is_trashed=True).prefetch_related('labels', 'checklist_items').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Корзина'
        context['active_tab'] = 'trash'
        return context

class RemindersView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user, reminder_date__isnull=False, is_archived=False, is_trashed=False
        ).prefetch_related('labels', 'checklist_items').order_by('reminder_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Напоминания'
        context['active_tab'] = 'reminders'
        return context

class LabelNoteView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'index.html'
    context_object_name = 'notes'

    def get_queryset(self):
        label_name = self.kwargs['label']
        return Note.objects.filter(user=self.request.user, labels__name=label_name, is_archived=False, is_trashed=False).prefetch_related('labels', 'checklist_items').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.kwargs['label']
        context['active_tab'] = 'label'
        context['active_label'] = self.kwargs['label']
        return context