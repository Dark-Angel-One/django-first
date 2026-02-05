from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Note, Label

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.force_login(self.user)

        # Create Notes
        self.normal_note = Note.objects.create(user=self.user, title="Normal", content="Content")
        self.archived_note = Note.objects.create(user=self.user, title="Archived", is_archived=True)
        self.trashed_note = Note.objects.create(user=self.user, title="Trashed", is_trashed=True)
        self.reminder_note = Note.objects.create(user=self.user, title="Reminder", reminder_date=timezone.now())

        self.label = Label.objects.create(user=self.user, name="Work")
        self.labeled_note = Note.objects.create(user=self.user, title="Labeled")
        self.labeled_note.labels.add(self.label)

    def test_note_list_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.normal_note, notes)
        self.assertIn(self.reminder_note, notes) # reminders are also normal notes if not archived
        self.assertIn(self.labeled_note, notes)
        self.assertNotIn(self.archived_note, notes)
        self.assertNotIn(self.trashed_note, notes)

    def test_archive_view(self):
        response = self.client.get(reverse('archive'))
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.archived_note, notes)
        self.assertNotIn(self.normal_note, notes)
        self.assertNotIn(self.trashed_note, notes)

    def test_trash_view(self):
        response = self.client.get(reverse('trash'))
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.trashed_note, notes)
        self.assertNotIn(self.normal_note, notes)
        self.assertNotIn(self.archived_note, notes)

    def test_reminders_view(self):
        response = self.client.get(reverse('reminders'))
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.reminder_note, notes)
        self.assertNotIn(self.normal_note, notes)
        self.assertNotIn(self.archived_note, notes)
        self.assertNotIn(self.trashed_note, notes)

    def test_label_note_view(self):
        response = self.client.get(reverse('label', args=[self.label.name]))
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.labeled_note, notes)
        self.assertNotIn(self.normal_note, notes)
