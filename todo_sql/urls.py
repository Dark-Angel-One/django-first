from django.urls import path
from . import views

urlpatterns = [
    # 1. Главная (имя 'index')
    path('', views.TaskListView.as_view(), name='index'),

    # 2. Добавление (имя 'add')
    path('add/', views.TaskCreateView.as_view(), name='add'),

    # 3. Редактирование (имя 'edit')
    path('edit/<int:pk>/', views.TaskUpdateView.as_view(), name='edit'),

    # 4. Удаление (имя 'delete')
    path('delete/<int:pk>/', views.TaskDeleteView.as_view(), name='delete'),

    # БЫЛО: path('toggle/<int:task_id>/', views.toggle_task, name='toggle'),

    # СТАЛО:
    path('toggle/<int:pk>/', views.TaskToggleView.as_view(), name='toggle'),
]