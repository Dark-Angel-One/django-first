from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'color', 'is_pinned']
        widgets = {
            'color': forms.HiddenInput(),
        }
