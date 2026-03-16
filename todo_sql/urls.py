from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views
from . import api_views

router = DefaultRouter()
router.register(r'notes', api_views.NoteViewSet, basename='note')
router.register(r'labels', api_views.LabelViewSet, basename='label')
router.register(r'checklist-items', api_views.ChecklistItemViewSet, basename='checklist-item')

urlpatterns = [
    path('', views.NoteListView.as_view(), name='index'),
    path('archive/', views.ArchiveView.as_view(), name='archive'),
    path('reminders/', views.RemindersView.as_view(), name='reminders'),
    path('trash/', views.TrashView.as_view(), name='trash'),
    path('label/<str:label>/', views.LabelNoteView.as_view(), name='label'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # ТИМЛИД: Новые роуты
    path('check-username/', views.check_username, name='check_username'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('debug-panel/', views.debug_panel, name='debug_panel'),

    # API
    path('api/v1/', include(router.urls)),
]