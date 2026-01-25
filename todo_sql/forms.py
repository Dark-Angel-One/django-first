from django import forms
from .models import Task

class TaskForm(forms.ModelForm):

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError("Слишком коротко! Напиши подробнее.")
        return title

    class Meta:
        model = Task
        fields = ['title', 'description'] # Какие поля показать пользователю
