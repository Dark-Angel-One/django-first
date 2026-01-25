from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Note

class NoteAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.note_data = {'title': 'Test Note', 'content': 'Test Content', 'color': 'white'}
        self.response = self.client.post('/api/v1/notes/', self.note_data, format='json')

    def test_create_note(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().title, 'Test Note')
        self.assertEqual(Note.objects.get().user, self.user)

    def test_get_notes(self):
        response = self.client.get('/api/v1/notes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming no pagination configured in settings
        self.assertEqual(len(response.data), 1)

    def test_archive_note(self):
        note = Note.objects.get()
        response = self.client.post(f'/api/v1/notes/{note.id}/archive/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertTrue(note.is_archived)
