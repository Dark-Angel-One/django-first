from django.db import models

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

    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст заметки")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='white', verbose_name="Цвет")
    is_pinned = models.BooleanField(default=False, verbose_name="Закреплено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title if self.title else self.content[:20]

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        ordering = ['-is_pinned', '-updated_at']
