from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Note, Label, ChecklistItem

class SecurityTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.note1 = Note.objects.create(user=self.user1, title="Note 1")
        self.note2 = Note.objects.create(user=self.user2, title="Note 2")

    def test_idor_checklist_item_creation(self):
        """Cannot add checklist item to another user's note"""
        data = {
            'text': 'Malicious item',
            'note': self.note2.id
        }
        response = self.client.post('/api/v1/checklist-items/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify it wasn't created
        self.assertFalse(ChecklistItem.objects.filter(text='Malicious item').exists())

    def test_label_uniqueness(self):
        """Cannot create duplicate label"""
        Label.objects.create(user=self.user1, name="Work")
        data = {'name': 'Work'}
        response = self.client.post('/api/v1/labels/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', str(response.data))

    def test_checklist_smart_update(self):
        """Updating note should preserve checklist item IDs"""
        # Create note with items via API
        data = {
            'title': 'Checklist Note',
            'is_checklist': True,
            'checklist_items': [
                {'text': 'Item 1', 'order': 0},
                {'text': 'Item 2', 'order': 1}
            ]
        }
        response = self.client.post('/api/v1/notes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note_id = response.data['id']
        items = response.data['checklist_items']
        id1 = items[0]['id']
        id2 = items[1]['id']

        # Update: Modify Item 1, Keep Item 2, Add Item 3
        update_data = {
            'checklist_items': [
                {'id': id1, 'text': 'Item 1 Updated', 'order': 0},
                {'id': id2, 'text': 'Item 2', 'order': 2},
                {'text': 'Item 3', 'order': 1}
            ]
        }
        response = self.client.patch(f'/api/v1/notes/{note_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify IDs
        new_items = response.data['checklist_items']
        # Should have 3 items
        self.assertEqual(len(new_items), 3)

        # Check Item 1 ID preserved
        item1 = next(i for i in new_items if i['text'] == 'Item 1 Updated')
        self.assertEqual(item1['id'], id1)

        # Check Item 2 ID preserved
        item2 = next(i for i in new_items if i['text'] == 'Item 2')
        self.assertEqual(item2['id'], id2)

        # Check Item 3 has new ID
        item3 = next(i for i in new_items if i['text'] == 'Item 3')
        self.assertNotEqual(item3['id'], id1)
        self.assertNotEqual(item3['id'], id2)
