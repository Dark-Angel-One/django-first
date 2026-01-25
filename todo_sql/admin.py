from django.contrib import admin
from .models import Task  # Импортируем наш класс из соседнего файла

# Регистрируем модель в админке
admin.site.register(Task)