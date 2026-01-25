from django.contrib import admin
from .models import Note

# Регистрируем модель в админке
admin.site.register(Note)
