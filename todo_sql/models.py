from django.db import models
from django.contrib.auth.models import User

class Label(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labels', verbose_name="Пользователь")
    name = models.CharField(max_length=50, verbose_name="Название")

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки'

    def __str__(self):
        return self.name

class Note(models.Model):
    COLOR_CHOICES = [
        ('white', 'Белый'),
        ('red', 'Красный'),
        ('orange', 'Оранжевый'),
        ('yellow', 'Желтый'),
        ('green', 'Зеленый'),
        ('teal', 'Бирюзовый'),
        ('blue', 'Синий'),
        ('darkblue', 'Темно-синий'),
        ('purple', 'Фиолетовый'),
        ('pink', 'Розовый'),
        ('brown', 'Коричневый'),
        ('gray', 'Серый'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', verbose_name="Пользователь")
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое", blank=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='white', verbose_name="Цвет")
    is_pinned = models.BooleanField(default=False, verbose_name="Закреплено", db_index=True)
    is_archived = models.BooleanField(default=False, verbose_name="В архиве", db_index=True)
    is_trashed = models.BooleanField(default=False, verbose_name="В корзине", db_index=True)
    is_checklist = models.BooleanField(default=False, verbose_name="Режим чеклиста")
    labels = models.ManyToManyField(Label, related_name='notes', blank=True, verbose_name="Метки")
    reminder_date = models.DateTimeField(null=True, blank=True, verbose_name="Напоминание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления", db_index=True)
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="Порядок")

    def __str__(self):
        return self.title if self.title else (self.content[:20] if self.content else "Note")

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        ordering = ['-is_pinned', 'order', '-updated_at']

class ChecklistItem(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='checklist_items', verbose_name="Заметка")
    text = models.CharField(max_length=255, verbose_name="Текст")
    is_checked = models.BooleanField(default=False, verbose_name="Выполнено")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = 'Пункт чеклиста'
        verbose_name_plural = 'Пункты чеклиста'
