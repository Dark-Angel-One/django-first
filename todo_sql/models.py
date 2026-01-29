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
    title = models.CharField(max_length=200, blank=True, verbose_name="Title")
    content = models.TextField(verbose_name="Content", blank=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='white', verbose_name="Color")
    is_pinned = models.BooleanField(default=False, verbose_name="Pinned", db_index=True)
    is_archived = models.BooleanField(default=False, verbose_name="Archived", db_index=True)
    is_trashed = models.BooleanField(default=False, verbose_name="Trashed", db_index=True)
    is_checklist = models.BooleanField(default=False, verbose_name="Checklist Mode")
    labels = models.ManyToManyField(Label, related_name='notes', blank=True, verbose_name="Labels")
    reminder_date = models.DateTimeField(null=True, blank=True, verbose_name="Reminder")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", db_index=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    def __str__(self):
        return self.title if self.title else (self.content[:20] if self.content else "Note")

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-is_pinned', 'order', '-updated_at']

class ChecklistItem(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='checklist_items')
    text = models.CharField(max_length=255, verbose_name="Text")
    is_checked = models.BooleanField(default=False, verbose_name="Checked")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
