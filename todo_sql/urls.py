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
    path('trash/', views.TrashView.as_view(), name='trash'),
    path('label/<str:label>/', views.LabelNoteView.as_view(), name='label'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # API
    path('api/v1/', include(router.urls)),

    # Legacy/Fallback Views
    path('edit/<int:pk>/', views.NoteUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.NoteDeleteView.as_view(), name='delete'),
]
