from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Note
from datetime import datetime

class NoteReminderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_note_with_reminder_date_html5_format(self):
        # HTML5 datetime-local sends 'YYYY-MM-DDTHH:MM' (no seconds)
        data = {
            'title': 'Reminder Note',
            'content': 'Test Content',
            'reminder_date': '2023-10-27T14:30'
        }
        response = self.client.post('/api/v1/notes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note = Note.objects.get()
        self.assertIsNotNone(note.reminder_date)
        # Note: formatting might include timezone or seconds in DB, but as long as it parses, it's good.
        self.assertEqual(note.reminder_date.year, 2023)
        self.assertEqual(note.reminder_date.month, 10)
        self.assertEqual(note.reminder_date.day, 27)
        self.assertEqual(note.reminder_date.hour, 14)
        self.assertEqual(note.reminder_date.minute, 30)

    def test_create_note_with_reminder_date_iso_format(self):
        # ISO format often includes seconds
        data = {
            'title': 'Reminder Note ISO',
            'content': 'Test Content',
            'reminder_date': '2023-10-27T14:30:00'
        }
        response = self.client.post('/api/v1/notes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
