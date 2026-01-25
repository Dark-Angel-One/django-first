from django.urls import path
from . import views

urlpatterns = [
    path('', views.NoteListView.as_view(), name='index'),
    path('api/create/', views.create_note_ajax, name='create_note_ajax'),
    path('edit/<int:pk>/', views.NoteUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.NoteDeleteView.as_view(), name='delete'),
]
