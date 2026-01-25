from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
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
        # Pagination is now enabled
        self.assertEqual(len(response.data['results']), 1)

    def test_archive_note(self):
        note = Note.objects.get()
        response = self.client.post(f'/api/v1/notes/{note.id}/archive/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertTrue(note.is_archived)

class NoteToggleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='toggleuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.note = Note.objects.create(user=self.user, title="Test Note", content="Content")

    def test_pin_toggle(self):
        url = reverse('note-pin', args=[self.note.id])

        # Pin
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_pinned'], True)
        self.note.refresh_from_db()
        self.assertTrue(self.note.is_pinned)

        # Unpin
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_pinned'], False)
        self.note.refresh_from_db()
        self.assertFalse(self.note.is_pinned)

    def test_archive_toggle(self):
        url = reverse('note-archive', args=[self.note.id])

        # Archive
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_archived'], True)
        self.note.refresh_from_db()
        self.assertTrue(self.note.is_archived)

        # Unarchive
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_archived'], False)
        self.note.refresh_from_db()
        self.assertFalse(self.note.is_archived)

    def test_trash_toggle(self):
        url = reverse('note-trash', args=[self.note.id])

        # Trash
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_trashed'], True)
        self.note.refresh_from_db()
        self.assertTrue(self.note.is_trashed)

        # Restore
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_trashed'], False)
        self.note.refresh_from_db()
        self.assertFalse(self.note.is_trashed)
