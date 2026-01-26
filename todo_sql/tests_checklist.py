from django.test import TestCase
from django.contrib.auth.models import User
from .models import Note, ChecklistItem
from .serializers import NoteSerializer

class ChecklistSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_create_note_with_checklist_items(self):
        data = {
            'title': 'Shopping List',
            'content': '',
            'is_checklist': True,
            'checklist_items': [
                {'text': 'Milk', 'is_checked': False, 'order': 0},
                {'text': 'Eggs', 'is_checked': True, 'order': 1},
            ],
            'color': 'white'
        }

        # Serializer needs context with request or user?
        # NoteSerializer uses HiddenField? No.
        # But Note model has user field.
        # The view usually handles injecting user.
        # Let's test the serializer directly but we need to pass user?
        # NoteSerializer definition:
        # user = models.ForeignKey(User, ...)
        # The serializer doesn't seem to have user in fields list or read_only_fields?
        # Wait, let's check serializer again.

        # It has: fields = ['id', 'title', 'content', ..., 'created_at', 'updated_at']
        # It does NOT have 'user' in fields.
        # So perform_create in ViewSet likely handles it: serializer.save(user=self.request.user)

        serializer = NoteSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        note = serializer.save(user=self.user)

        self.assertEqual(note.title, 'Shopping List')
        self.assertTrue(note.is_checklist)
        self.assertEqual(note.checklist_items.count(), 2)

        items = note.checklist_items.all().order_by('order')
        self.assertEqual(items[0].text, 'Milk')
        self.assertFalse(items[0].is_checked)
        self.assertEqual(items[1].text, 'Eggs')
        self.assertTrue(items[1].is_checked)
