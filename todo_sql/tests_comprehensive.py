from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Note, Label, ChecklistItem

class ModelIndexTests(TestCase):
    def test_note_db_indices(self):
        """Verify required fields have db_index=True"""
        fields_with_index = [
            'is_pinned', 'is_archived', 'is_trashed',
            'created_at', 'updated_at', 'order'
        ]
        for field_name in fields_with_index:
            field = Note._meta.get_field(field_name)
            self.assertTrue(field.db_index, f"Field '{field_name}' should have db_index=True")

class APIReorderTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        # User 1 notes
        self.note1 = Note.objects.create(user=self.user1, title="U1 N1", order=0)
        self.note2 = Note.objects.create(user=self.user1, title="U1 N2", order=1)

        # User 2 note
        self.note_foreign = Note.objects.create(user=self.user2, title="U2 N1", order=0)

    def test_reorder_ignores_foreign_notes(self):
        """Reorder should only affect user's own notes"""
        # Attempt to reorder user1's notes but also include user2's note ID in pinned_ids
        # If vulnerable, it might move user2's note or error out.
        # Ideally, it should just ignore user2's note ID.

        data = {
            'pinned_ids': [self.note2.id, self.note_foreign.id], # Try to pin foreign note
            'other_ids': [self.note1.id]
        }

        response = self.client.post('/api/v1/notes/reorder/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Reload from DB
        self.note1.refresh_from_db()
        self.note2.refresh_from_db()
        self.note_foreign.refresh_from_db()

        # Check User 1 notes
        self.assertTrue(self.note2.is_pinned)
        self.assertEqual(self.note2.order, 0)

        self.assertFalse(self.note1.is_pinned)
        self.assertEqual(self.note1.order, 0)

        # Check Foreign Note (Should be untouched)
        self.assertFalse(self.note_foreign.is_pinned) # Should NOT become pinned
        # Order might remain same
        self.assertEqual(self.note_foreign.order, 0)

class APIStateTransitionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.note = Note.objects.create(user=self.user, title="State Test")

    def test_trash_unarchives_note(self):
        """Trashing an archived note should unarchive it"""
        self.note.is_archived = True
        self.note.save()

        response = self.client.post(f'/api/v1/notes/{self.note.id}/trash/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_trashed'])
        self.assertFalse(response.data['is_archived'])

        self.note.refresh_from_db()
        self.assertTrue(self.note.is_trashed)
        self.assertFalse(self.note.is_archived)

    def test_trash_unpins_note(self):
        """Trashing a pinned note should unpin it"""
        self.note.is_pinned = True
        self.note.save()

        response = self.client.post(f'/api/v1/notes/{self.note.id}/trash/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.note.refresh_from_db()
        self.assertTrue(self.note.is_trashed)
        self.assertFalse(self.note.is_pinned)

    def test_archive_toggle(self):
        """Archive toggle works correctly"""
        # Archive
        response = self.client.post(f'/api/v1/notes/{self.note.id}/archive/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_archived'])

        self.note.refresh_from_db()
        self.assertTrue(self.note.is_archived)

        # Unarchive
        response = self.client.post(f'/api/v1/notes/{self.note.id}/archive/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_archived'])

        self.note.refresh_from_db()
        self.assertFalse(self.note.is_archived)

class PaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pager', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Create 13 notes to trigger pagination (page size is 12)
        for i in range(13):
            n = Note.objects.create(user=self.user, title=f"Note {i}")
            # Create Checklist items for pagination test on items
            ChecklistItem.objects.create(note=n, text=f"Item {i}")
            # Create Labels for pagination test on labels
            Label.objects.create(user=self.user, name=f"Label {i}")

    def test_api_pagination_size_notes(self):
        response = self.client.get('/api/v1/notes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 12) # Should be 12 on first page
        self.assertIsNotNone(response.data['next'])

    def test_api_pagination_size_checklist_items(self):
        response = self.client.get('/api/v1/checklist-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if paginated (look for 'results' key)
        if 'results' not in response.data:
            self.fail("Checklist Items API is not paginated")
        self.assertEqual(len(response.data['results']), 12)

    def test_api_pagination_size_labels(self):
        response = self.client.get('/api/v1/labels/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if paginated
        if 'results' not in response.data:
            self.fail("Labels API is not paginated")
        self.assertEqual(len(response.data['results']), 12)

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='viewer', password='password')
        self.client.force_login(self.user)

    def test_label_view_nonexistent(self):
        """Accessing a label view for a label that doesn't exist returns empty list, not 404"""
        # The view implementation filters by label name.
        # If no notes have that label, it's just an empty list.
        # This confirms behavior.
        response = self.client.get('/label/ghost-label/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notes']), 0)
        self.assertEqual(response.context['active_label'], 'ghost-label')
