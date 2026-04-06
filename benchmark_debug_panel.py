import os
import django
import time
from django.contrib.auth.models import User

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from todo_sql.models import Note
from todo_sql.views import debug_panel
from django.test import RequestFactory

def benchmark_debug_panel(num_users, num_notes):
    print(f"Preparing data: {num_users} users, {num_notes} notes...")

    # We don't want to actually create 100k users/notes if we can avoid it,
    # as it might be slow in the sandbox.
    # But to see a "count" slowness we usually need a lot.

    # Instead, let's just measure the time for the current implementation.
    # Even if it's fast now, caching will make it nearly 0 after first call.

    user = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')

    # Create some notes
    notes = [Note(user=user, title=f"Note {i}") for i in range(num_notes)]
    Note.objects.bulk_create(notes)

    factory = RequestFactory()
    request = factory.get('/debug-panel/')
    request.user = user

    # Warm up
    debug_panel(request)

    start_time = time.time()
    for _ in range(10):
        debug_panel(request)
    end_time = time.time()

    avg_time = (end_time - start_time) / 10
    print(f"Average execution time (10 runs): {avg_time:.6f} seconds")

    # Clean up
    User.objects.all().delete()

if __name__ == "__main__":
    benchmark_debug_panel(100, 1000)
