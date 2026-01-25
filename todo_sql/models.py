from django.db import models
from django.contrib.auth.models import User

class Label(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labels')
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

class Note(models.Model):
    COLOR_CHOICES = [
        ('white', 'White'),
        ('red', 'Red'),
        ('orange', 'Orange'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('teal', 'Teal'),
        ('blue', 'Blue'),
        ('darkblue', 'Dark Blue'),
        ('purple', 'Purple'),
        ('pink', 'Pink'),
        ('brown', 'Brown'),
        ('gray', 'Gray'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст заметки", blank=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='white', verbose_name="Цвет")
    is_pinned = models.BooleanField(default=False, verbose_name="Закреплено")
    is_archived = models.BooleanField(default=False, verbose_name="В архиве")
    is_trashed = models.BooleanField(default=False, verbose_name="В корзине")
    is_checklist = models.BooleanField(default=False, verbose_name="Режим чек-листа")
    labels = models.ManyToManyField(Label, related_name='notes', blank=True, verbose_name="Метки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title if self.title else (self.content[:20] if self.content else "Note")

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        ordering = ['-is_pinned', '-updated_at']

class ChecklistItem(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='checklist_items')
    text = models.CharField(max_length=255, verbose_name="Текст")
    is_checked = models.BooleanField(default=False, verbose_name="Выполнено")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
