import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# ТИМЛИД: Этот скрипт создаст суперюзера для дебага
username = 'admin_lead'
password = 'Password123!'
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Суперюзер '{username}' успешно создан! Пароль: {password}")
else:
    print(f"Пользователь '{username}' уже существует.")