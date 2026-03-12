from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
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

class ChecklistItemViewSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.note = Note.objects.create(user=self.user, title="My List", is_checklist=True)
        self.item = ChecklistItem.objects.create(note=self.note, text="Item 1", order=0)

    def test_update_item_status(self):
        response = self.client.patch(f'/api/v1/checklist-items/{self.item.id}/', {'is_checked': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_checked)

    def test_update_item_text(self):
        response = self.client.patch(f'/api/v1/checklist-items/{self.item.id}/', {'text': 'Updated Item'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.text, 'Updated Item')

    def test_delete_item(self):
        response = self.client.delete(f'/api/v1/checklist-items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChecklistItem.objects.filter(id=self.item.id).exists())

    def test_create_item(self):
        data = {'note': self.note.id, 'text': 'New Item', 'order': 1}
        response = self.client.post('/api/v1/checklist-items/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ChecklistItem.objects.filter(text='New Item', note=self.note).exists())

    def test_update_note_removes_unspecified_items(self):
        # Add another item
        item2 = ChecklistItem.objects.create(note=self.note, text="Item 2", order=1)

        # Prepare update data with only item2, effectively removing self.item
        data = {
            'checklist_items': [
                {'id': item2.id, 'text': 'Updated Item 2', 'order': 0}
            ]
        }

        # We need to use NoteViewSet or NoteSerializer directly as tests_checklist.py doesn't have a Note update test
        # Let's use the API
        response = self.client.patch(f'/api/v1/notes/{self.note.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify item2 is updated
        item2.refresh_from_db()
        self.assertEqual(item2.text, 'Updated Item 2')

        # Verify self.item is deleted
        self.assertFalse(ChecklistItem.objects.filter(id=self.item.id).exists())
        self.assertEqual(self.note.checklist_items.count(), 1)
